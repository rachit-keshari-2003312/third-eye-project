#!/usr/bin/env python3
"""
Conversation Memory Manager
Enables interactive, context-aware conversations
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class ConversationMemory:
    """
    Manages conversation history and context for interactive queries
    """
    
    def __init__(self, max_history: int = 10):
        """
        Initialize conversation memory
        
        Args:
            max_history: Maximum number of conversation turns to keep
        """
        self.conversations: Dict[str, List[Dict[str, Any]]] = {}
        self.max_history = max_history
    
    def create_session(self) -> str:
        """
        Create a new conversation session
        
        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())
        self.conversations[session_id] = []
        logger.info(f"Created new conversation session: {session_id}")
        return session_id
    
    def add_turn(self, session_id: str, prompt: str, response: Dict[str, Any]):
        """
        Add a conversation turn (prompt + response) to session history
        
        Args:
            session_id: Conversation session ID
            prompt: User's prompt
            response: System's response
        """
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        
        turn = {
            'timestamp': datetime.now().isoformat(),
            'prompt': prompt,
            'sql': response.get('sql'),
            'data_source_id': response.get('data_source_id'),
            'row_count': response.get('row_count'),
            'success': response.get('success'),
            'tables_used': self._extract_tables(response.get('sql', ''))
        }
        
        self.conversations[session_id].append(turn)
        
        # Keep only last max_history turns
        if len(self.conversations[session_id]) > self.max_history:
            self.conversations[session_id] = self.conversations[session_id][-self.max_history:]
        
        logger.info(f"Added turn to session {session_id} (total turns: {len(self.conversations[session_id])})")
    
    def get_history(self, session_id: str, last_n: int = 5) -> List[Dict[str, Any]]:
        """
        Get conversation history for a session
        
        Args:
            session_id: Conversation session ID
            last_n: Number of recent turns to return
            
        Returns:
            List of conversation turns
        """
        if session_id not in self.conversations:
            return []
        
        return self.conversations[session_id][-last_n:]
    
    def get_context_summary(self, session_id: str) -> str:
        """
        Get a text summary of recent conversation context
        
        Args:
            session_id: Conversation session ID
            
        Returns:
            Context summary string
        """
        history = self.get_history(session_id, last_n=3)
        
        if not history:
            return "No previous context."
        
        context_parts = ["Recent conversation context:"]
        
        for i, turn in enumerate(history, 1):
            context_parts.append(f"\nTurn {i}:")
            context_parts.append(f"  User asked: {turn['prompt'][:100]}...")
            if turn['sql']:
                context_parts.append(f"  SQL generated: {turn['sql'][:100]}...")
            if turn.get('tables_used'):
                context_parts.append(f"  Tables used: {', '.join(turn['tables_used'])}")
            context_parts.append(f"  Data source: {turn.get('data_source_id', 'N/A')}")
            context_parts.append(f"  Rows returned: {turn.get('row_count', 0)}")
        
        return "\n".join(context_parts)
    
    def get_last_query_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about the last query in the session
        
        Args:
            session_id: Conversation session ID
            
        Returns:
            Last query info or None
        """
        history = self.get_history(session_id, last_n=1)
        return history[0] if history else None
    
    def _extract_tables(self, sql: Optional[str]) -> List[str]:
        """
        Extract table names from SQL query
        
        Args:
            sql: SQL query string
            
        Returns:
            List of table names
        """
        if not sql:
            return []
        
        import re
        # Simple extraction: find words after FROM and JOIN
        pattern = r'(?:FROM|JOIN)\s+(\w+)'
        matches = re.findall(pattern, sql, re.IGNORECASE)
        return list(set(matches))  # Remove duplicates
    
    def clear_session(self, session_id: str):
        """
        Clear all history for a session
        
        Args:
            session_id: Conversation session ID
        """
        if session_id in self.conversations:
            del self.conversations[session_id]
            logger.info(f"Cleared session: {session_id}")
    
    def get_active_sessions(self) -> List[str]:
        """
        Get list of active session IDs
        
        Returns:
            List of session IDs
        """
        return list(self.conversations.keys())


# Global conversation memory instance
_conversation_memory = ConversationMemory()


def get_conversation_memory() -> ConversationMemory:
    """Get the global conversation memory instance"""
    return _conversation_memory

