#!/usr/bin/env python3
"""
Text-to-SQL Agent using Claude/Bedrock
Autonomous agent that converts natural language to SQL
"""

import json
import logging
from typing import Dict, Any, Optional, List
from bedrock_client import BedrockClient
from redash_sql_executor import RedashSQLExecutor

logger = logging.getLogger(__name__)


class TextToSQLAgent:
    """
    Autonomous agent that:
    1. Discovers schema
    2. Generates SQL from natural language
    3. Executes SQL
    4. Returns natural language answer
    """
    
    def __init__(self, bedrock_client: BedrockClient, sql_executor: RedashSQLExecutor):
        self.bedrock = bedrock_client
        self.sql_executor = sql_executor
    
    def _discover_relevant_tables(self, data_source_id: int, question: str) -> List[Dict[str, Any]]:
        """
        Use Claude to identify which tables are relevant for the question
        
        Args:
            data_source_id: Data source ID
            question: User's question
            
        Returns:
            List of relevant tables with columns
        """
        # Get all tables
        all_tables = self.sql_executor.get_data_source_schema(data_source_id)
        
        if not all_tables:
            logger.warning("No tables found in schema")
            return []
        
        logger.info(f"Total tables in schema: {len(all_tables)}")
        
        # ✅ FIX: Check if user explicitly mentioned a table name
        # Patterns: "from table X", "from X table", "table X", "X table"
        import re
        table_patterns = [
            r'from\s+table\s+(\w+)',
            r'from\s+(\w+)\s+table',
            r'table\s+(\w+)',
            r'in\s+(\w+)\s+table',
            r'in\s+table\s+(\w+)',
        ]
        
        for pattern in table_patterns:
            match = re.search(pattern, question.lower())
            if match:
                mentioned_table = match.group(1)
                # Find this exact table in schema
                for table in all_tables:
                    if table.get('name', '').lower() == mentioned_table.lower():
                        logger.info(f"✅ USER SPECIFIED TABLE: {table['name']} - skipping discovery!")
                        return [table]
                # If not found with pattern, try direct name match
                for table in all_tables:
                    table_name = table.get('name', '').lower()
                    if mentioned_table in table_name or table_name in mentioned_table:
                        logger.info(f"✅ USER SPECIFIED TABLE (fuzzy match): {table['name']}")
                        return [table]
        
        # Also check for table names that appear as-is in question (like a_vcip_payufin_applications)
        question_lower = question.lower()
        for table in all_tables:
            table_name = table.get('name', '')
            # If the full table name appears in the question, use it!
            if table_name.lower() in question_lower:
                logger.info(f"✅ TABLE NAME FOUND IN QUESTION: {table_name}")
                return [table]
        
        # OPTIMIZATION: Filter tables by keywords in the question first
        # This reduces the schema size sent to Claude
        question_lower = question.lower()
        
        # Extract potential table name keywords from question
        import re
        words = re.findall(r'\b\w+\b', question_lower)
        # Common keywords that might be in table names
        stop_words = [
            'from', 'with', 'this', 'that', 'what', 'where', 'show', 'give', 
            'find', 'list', 'last', 'first', 'only', 'data', 'source', 'look',
            'table', 'record', 'database', 'query', 'select', 'the', 'and', 'or'
        ]
        potential_keywords = [w for w in words if len(w) > 2 and w not in stop_words]
        
        logger.info(f"Potential keywords from question: {potential_keywords}")
        
        # Pre-filter tables based on keywords
        candidate_tables = []
        for table in all_tables:
            table_name = table.get('name', '').lower()
            # Include table if any keyword appears in table name OR table columns
            table_match = any(keyword in table_name for keyword in potential_keywords)
            
            # Also check if keywords are in column names
            columns = [col.lower() for col in table.get('columns', [])]
            column_match = any(
                any(keyword in col for keyword in potential_keywords)
                for col in columns
            )
            
            if table_match or column_match:
                candidate_tables.append(table)
        
        # If we filtered too aggressively and got nothing, use all tables
        # But limit to reasonable size to avoid token limits
        if not candidate_tables:
            logger.warning("No keyword matches, using first 100 tables")
            candidate_tables = all_tables[:100]
        elif len(candidate_tables) > 100:
            logger.warning(f"Too many candidates ({len(candidate_tables)}), limiting to 100")
            candidate_tables = candidate_tables[:100]
        
        logger.info(f"Filtered to {len(candidate_tables)} candidate tables")
        
        # Format schema for Claude (only candidate tables)
        schema_summary = []
        for table in candidate_tables:
            table_name = table.get('name', '')
            # Columns is a simple list of strings from Redash
            columns = table.get('columns', [])
            # Limit columns shown to save tokens
            columns_preview = columns[:20]  # Only show first 20 columns
            if len(columns) > 20:
                columns_preview.append(f"... and {len(columns) - 20} more columns")
            schema_summary.append(f"Table: {table_name}\nColumns: {', '.join(columns_preview)}")
        
        schema_text = "\n\n".join(schema_summary)
        
        # Ask Claude to identify relevant tables
        prompt = f"""Given this database schema and user question, identify which tables are most relevant.

DATABASE SCHEMA:
{schema_text}

USER QUESTION: {question}

Respond with ONLY a JSON array of table names that are relevant, like: ["table1", "table2"]
If unsure, include all potentially relevant tables."""

        try:
            response = self.bedrock.generate_response(prompt, max_tokens=500)
            
            # Parse table names - be robust with JSON parsing
            logger.info(f"LLM response for table discovery: {response[:200]}")
            
            # Extract JSON array from response
            import re
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                table_names = json.loads(json_str)
            else:
                # Fallback: try to parse the whole response
                table_names = json.loads(response.strip())
            
            # Filter tables
            relevant_tables = []
            for table in candidate_tables:  # Use candidate_tables instead of all_tables
                if table.get('name', '') in table_names:
                    relevant_tables.append(table)
            
            logger.info(f"Identified {len(relevant_tables)} relevant tables: {table_names}")
            return relevant_tables
            
        except Exception as e:
            logger.error(f"Error discovering tables: {e}")
            logger.error(f"LLM response was: {response[:500] if 'response' in locals() else 'N/A'}")
            # Fallback: return all tables
            return all_tables
    
    def generate_sql(self, data_source_id: int, question: str, 
                    schema: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Generate SQL query from natural language question
        
        Args:
            data_source_id: Data source ID
            question: User's natural language question
            schema: Optional schema (if not provided, will auto-discover)
            
        Returns:
            Dict with 'sql' and 'explanation'
        """
        try:
            # Discover relevant tables if schema not provided
            if not schema:
                schema = self._discover_relevant_tables(data_source_id, question)
            
            if not schema:
                return {
                    "error": "No relevant tables found",
                    "sql": None
                }
            
            # Format schema for SQL generation
            schema_text = []
            for table in schema:
                table_name = table.get('name', '')
                # Columns is a simple list of strings from Redash
                columns = table.get('columns', [])
                column_list = "\n".join([f"  - {col}" for col in columns])
                
                schema_text.append(f"Table: {table_name}\n{column_list}")
            
            schema_formatted = "\n\n".join(schema_text)
            
            # Generate SQL using Claude
            prompt = f"""You are an expert SQL query generator. Generate a SQL query to answer the user's question.

DATABASE SCHEMA:
{schema_formatted}

USER QUESTION: {question}

IMPORTANT RULES FOR MYSQL SYNTAX:
1. Generate ONLY valid MySQL syntax
2. **CRITICAL**: DO NOT include database name prefixes in table names
   ❌ WRONG: FROM ZC_Prod_Wibmo.a_application_stage_tracker
   ✅ CORRECT: FROM a_application_stage_tracker
   (The data source already points to the correct database)
3. For time intervals: use NOW() - INTERVAL X HOUR (not 'X hours')
   Examples:
   - Last 2 hours: NOW() - INTERVAL 2 HOUR
   - Last 24 hours: NOW() - INTERVAL 24 HOUR
   - Last 7 days: NOW() - INTERVAL 7 DAY
4. For today: use DATE(column) = CURDATE()
5. Use >= for date comparisons with NOW()
6. Common column patterns:
   - created_at, updated_at, date_created for timestamps
   - current_status, status, state for status values
   - Try columns ending with _id, _date, _at, _time
7. For JOINs: 
   - Use table aliases (e.g., ast, aua) but NO database prefixes
   - **CRITICAL**: Only use columns that EXIST in the schema
   - Common join columns: application_id, user_id, tenant_id
   - Check the schema carefully before assuming column names
8. Return ONLY JSON with this structure:
{{
  "sql": "SELECT ...",
  "explanation": "This query does..."
}}

Generate the SQL now:"""

            response = self.bedrock.generate_response(prompt, max_tokens=1000)
            
            # Parse response - be robust with JSON parsing
            logger.info(f"LLM response for SQL generation: {response[:300]}")
            
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                # Fix common JSON issues: escape newlines in strings
                # This is a simple fix - replace actual newlines with \n in JSON values
                # More robust: use a custom parser, but this works for our case
                try:
                    result = json.loads(json_str)
                except json.JSONDecodeError as json_err:
                    logger.warning(f"JSON decode error, trying manual extraction: {json_err}")
                    # Try to fix by removing actual newlines in SQL
                    # Extract sql and explanation separately with better regex
                    sql_match = re.search(r'"sql"\s*:\s*"(.*?)(?:"\s*,?\s*"explanation)', json_str, re.DOTALL)
                    exp_match = re.search(r'"explanation"\s*:\s*"(.*?)"(?:\s*\}|$)', json_str, re.DOTALL)
                    
                    if sql_match:
                        # Clean up SQL: replace newlines and extra whitespace
                        sql = sql_match.group(1)
                        sql = re.sub(r'\s+', ' ', sql)  # Replace multiple spaces/newlines with single space
                        sql = sql.strip()
                        
                        explanation = ""
                        if exp_match:
                            explanation = exp_match.group(1).replace('\n', ' ').replace('\r', '').strip()
                        
                        result = {
                            "sql": sql,
                            "explanation": explanation or "Generated SQL query based on the schema and question"
                        }
                        logger.info("Successfully extracted SQL and explanation manually")
                    else:
                        logger.error("Could not extract SQL from response")
                        raise json_err  # Re-raise original error
            else:
                result = json.loads(response.strip())
            
            logger.info(f"Generated SQL: {result.get('sql', '')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating SQL: {e}", exc_info=True)
            return {
                "error": str(e),
                "sql": None
            }
    
    def execute_and_explain(self, data_source_id: int, question: str) -> Dict[str, Any]:
        """
        Complete autonomous flow:
        1. Discover schema
        2. Generate SQL
        3. Execute SQL
        4. Generate natural language answer
        
        Args:
            data_source_id: Data source ID
            question: User's natural language question
            
        Returns:
            Dict with answer, sql, and raw data
        """
        try:
            logger.info(f"Starting autonomous SQL execution for: {question}")
            
            # Step 1: Generate SQL
            sql_result = self.generate_sql(data_source_id, question)
            
            if "error" in sql_result or not sql_result.get("sql"):
                return {
                    "answer": f"❌ Could not generate SQL: {sql_result.get('error', 'Unknown error')}",
                    "sql": None,
                    "raw_data": None
                }
            
            sql_query = sql_result["sql"]
            explanation = sql_result.get("explanation", "")
            
            # Step 2: Execute SQL
            results = self.sql_executor.execute_adhoc_query(data_source_id, sql_query)
            
            if "error" in results:
                return {
                    "answer": f"❌ SQL execution failed: {results['error']}",
                    "sql": sql_query,
                    "explanation": explanation,
                    "raw_data": None
                }
            
            # Extract data
            query_result = results.get('query_result', {})
            data = query_result.get('data', {})
            rows = data.get('rows', [])
            columns = data.get('columns', [])
            
            logger.info(f"Query returned {len(rows)} rows")
            
            # Step 3: Generate natural language answer
            if not rows:
                natural_answer = "✅ Query executed successfully, but no results found."
            else:
                # Format data for Claude
                data_sample = rows[:5]  # First 5 rows
                data_text = json.dumps(data_sample, indent=2)
                
                answer_prompt = f"""Given the SQL query results, provide a clear, natural language answer to the user's question.

USER QUESTION: {question}

SQL QUERY: {sql_query}

RESULTS ({len(rows)} total rows):
{data_text}

Provide a concise, human-readable answer. Include:
1. Direct answer to the question
2. Key numbers/stats
3. Any notable patterns

Keep it conversational and helpful."""

                natural_answer = self.bedrock.generate_response(answer_prompt, max_tokens=1000)
            
            return {
                "answer": natural_answer,
                "sql": sql_query,
                "explanation": explanation,
                "row_count": len(rows),
                "raw_data": {
                    "columns": columns,
                    "rows": rows
                }
            }
            
        except Exception as e:
            logger.error(f"Error in execute_and_explain: {e}", exc_info=True)
            return {
                "answer": f"❌ Error: {str(e)}",
                "sql": None,
                "raw_data": None
            }

