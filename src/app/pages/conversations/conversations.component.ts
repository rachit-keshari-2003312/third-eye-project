import { Component, OnInit, signal, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';

interface ApiResponse {
  id: string;
  query: string;
  response: string;
  timestamp: Date;
  status: 'success' | 'error' | 'loading';
  processingTime?: number;
}

@Component({
  selector: 'app-conversations',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="conversations-container">
      <!-- Header -->
      <div class="conversations-header">
        <div class="header-content">
          <h1>AI Search & Query Interface</h1>
          <p>Enter your queries and get intelligent responses from our AI agents</p>
        </div>
        <div class="header-stats">
          <div class="stat-item">
            <span class="stat-value">{{ queryHistory().length }}</span>
            <span class="stat-label">Total Queries</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ getSuccessRate() }}%</span>
            <span class="stat-label">Success Rate</span>
          </div>
        </div>
      </div>

      <!-- Search Input Section -->
      <div class="search-section">
        <div class="search-card">
          <div class="search-header">
            <h2>🔍 Enter Your Query</h2>
            <div class="search-options">
              <select [(ngModel)]="selectedAgent" name="selectedAgent">
                <option value="">Select AI Agent</option>
                <option value="data-analyst">Data Analyst</option>
                <option value="code-assistant">Code Assistant</option>
                <option value="research">Research Assistant</option>
                <option value="general">General AI</option>
              </select>
            </div>
          </div>

          <div class="search-input-container">
            <textarea 
              [(ngModel)]="searchQuery" 
              name="searchQuery"
              placeholder="Enter your question or query here... 

Examples:
• Analyze the sales data for Q4 2024
• Generate a Python script for data processing
• Research the latest trends in AI technology
• Explain quantum computing concepts"
              rows="6"
              [disabled]="isProcessing()"
              class="search-input">
            </textarea>
            
            <div class="search-actions">
              <div class="search-controls">
                <label class="control-item">
                  <input type="checkbox" [(ngModel)]="useAdvancedMode" name="useAdvancedMode">
                  <span>Advanced Mode</span>
                </label>
                <label class="control-item">
                  <input type="checkbox" [(ngModel)]="includeContext" name="includeContext">
                  <span>Include Context</span>
                </label>
              </div>
              
              <div class="action-buttons">
                <button 
                  class="clear-btn" 
                  (click)="clearSearch()"
                  [disabled]="isProcessing()">
                  Clear
                </button>
                <button 
                  class="search-btn" 
                  (click)="executeSearch()"
                  [disabled]="!searchQuery.trim() || isProcessing()">
                  <span *ngIf="!isProcessing()">🚀 Start Search</span>
                  <span *ngIf="isProcessing()">
                    <div class="loading-spinner"></div>
                    Processing...
                  </span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Output Section -->
      <div class="output-section">
        <div class="output-header">
          <h2>📋 Query Results</h2>
          <div class="output-controls">
            <button class="export-btn" (click)="exportResults()" [disabled]="queryHistory().length === 0">
              📥 Export
            </button>
            <button class="clear-history-btn" (click)="clearHistory()" [disabled]="queryHistory().length === 0">
              🗑️ Clear History
            </button>
          </div>
        </div>

        <!-- Current Response -->
        <div class="current-response" *ngIf="currentResponse()">
          <div class="response-card" [class]="currentResponse()!.status">
            <div class="response-header">
              <div class="response-meta">
                <span class="query-text">{{ currentResponse()!.query }}</span>
                <span class="response-time">{{ formatTime(currentResponse()!.timestamp) }}</span>
              </div>
              <div class="response-status" [class]="currentResponse()!.status">
                {{ currentResponse()!.status }}
              </div>
            </div>
            
            <div class="response-content">
              <div class="response-text" *ngIf="currentResponse()!.status === 'success'">
                {{ currentResponse()!.response }}
              </div>
              <div class="error-text" *ngIf="currentResponse()!.status === 'error'">
                ❌ Error: {{ currentResponse()!.response }}
              </div>
              <div class="loading-text" *ngIf="currentResponse()!.status === 'loading'">
                <div class="loading-animation">
                  <div class="dot"></div>
                  <div class="dot"></div>
                  <div class="dot"></div>
                </div>
                Processing your query...
              </div>
            </div>

            <div class="response-footer" *ngIf="currentResponse()!.processingTime">
              <span class="processing-time">
                ⚡ Processed in {{ currentResponse()!.processingTime }}ms
              </span>
            </div>
          </div>
        </div>

        <!-- Query History -->
        <div class="history-section" *ngIf="queryHistory().length > 0">
          <h3>📚 Query History</h3>
          <div class="history-list">
            <div class="history-item" 
                 *ngFor="let item of queryHistory().slice().reverse(); let i = index"
                 (click)="selectHistoryItem(item)">
              <div class="history-header">
                <span class="history-query">{{ item.query.substring(0, 100) }}{{ item.query.length > 100 ? '...' : '' }}</span>
                <span class="history-time">{{ formatTime(item.timestamp) }}</span>
              </div>
              <div class="history-preview">
                {{ item.response.substring(0, 150) }}{{ item.response.length > 150 ? '...' : '' }}
              </div>
              <div class="history-status" [class]="item.status">
                {{ item.status }}
              </div>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div class="empty-output" *ngIf="queryHistory().length === 0 && !currentResponse()">
          <div class="empty-icon">🤖</div>
          <h3>No queries yet</h3>
          <p>Enter a query above and click "Start Search" to see AI responses here.</p>
        </div>
      </div>
    </div>
  `,
  styleUrls: ['./conversations.component.scss']
})
export class ConversationsComponent implements OnInit {
  
  // Form inputs
  searchQuery = '';
  selectedAgent = '';
  useAdvancedMode = false;
  includeContext = true;

  // State management
  isProcessing = signal(false);
  currentResponse = signal<ApiResponse | null>(null);
  queryHistory = signal<ApiResponse[]>([]);

  private apiBaseUrl = 'http://localhost:8000/api';

  private http = inject(HttpClient);

  ngOnInit() {
    console.log('💬 ConversationsComponent initialized');
    this.loadQueryHistory();
  }

  async executeSearch() {
    if (!this.searchQuery.trim()) {
      alert('Please enter a search query.');
      return;
    }

    const queryId = Date.now().toString();
    const startTime = Date.now();

    // Create loading response
    const loadingResponse: ApiResponse = {
      id: queryId,
      query: this.searchQuery,
      response: '',
      timestamp: new Date(),
      status: 'loading'
    };

    this.currentResponse.set(loadingResponse);
    this.isProcessing.set(true);

    try {
      // Simulate API call to backend
      console.log('🚀 Executing search:', this.searchQuery);
      
      // For demo purposes, create a mock response
      // In real implementation, this would call the actual backend API
      const mockResponse = await this.simulateApiCall(this.searchQuery);
      
      const processingTime = Date.now() - startTime;
      
      const successResponse: ApiResponse = {
        id: queryId,
        query: this.searchQuery,
        response: mockResponse,
        timestamp: new Date(),
        status: 'success',
        processingTime
      };

      this.currentResponse.set(successResponse);
      this.queryHistory.update(history => [...history, successResponse]);
      this.saveQueryHistory();

    } catch (error) {
      console.error('❌ Search error:', error);
      
      const errorResponse: ApiResponse = {
        id: queryId,
        query: this.searchQuery,
        response: 'Failed to process query. Please try again.',
        timestamp: new Date(),
        status: 'error'
      };

      this.currentResponse.set(errorResponse);
      this.queryHistory.update(history => [...history, errorResponse]);
    } finally {
      this.isProcessing.set(false);
    }
  }

  private async simulateApiCall(query: string): Promise<string> {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000));

    // Generate contextual mock responses based on query content
    const queryLower = query.toLowerCase();
    
    if (queryLower.includes('data') || queryLower.includes('analysis') || queryLower.includes('chart')) {
      return `📊 Data Analysis Response:

Based on your query "${query}", I've analyzed the relevant data patterns. Here are the key insights:

• **Trend Analysis**: The data shows a significant upward trend over the past quarter
• **Key Metrics**: Performance indicators suggest 23% improvement in efficiency
• **Recommendations**: Consider implementing automated reporting for better visibility
• **Next Steps**: Schedule weekly reviews to monitor progress

This analysis was generated using our advanced data processing algorithms with MCP server integration.`;
    }
    
    if (queryLower.includes('code') || queryLower.includes('script') || queryLower.includes('program')) {
      return `💻 Code Assistant Response:

For your request "${query}", here's the recommended approach:

\`\`\`python
# Generated code solution
def process_data(input_data):
    """
    Process data according to your requirements
    """
    result = []
    for item in input_data:
        processed_item = {
            'id': item.get('id'),
            'processed': True,
            'timestamp': datetime.now()
        }
        result.append(processed_item)
    return result
\`\`\`

This solution includes error handling and follows best practices for data processing.`;
    }

    if (queryLower.includes('research') || queryLower.includes('trend') || queryLower.includes('information')) {
      return `🔍 Research Assistant Response:

Research findings for "${query}":

**Key Findings:**
1. **Current State**: The field is rapidly evolving with new developments
2. **Market Trends**: 45% growth in adoption over the past year
3. **Technology Stack**: Modern frameworks are becoming the standard
4. **Future Outlook**: Significant potential for expansion

**Sources Analyzed:**
• Academic papers and research journals
• Industry reports and market analysis
• Expert opinions and case studies
• Real-time data from web sources

**Recommendations:**
Consider implementing these findings in your strategic planning process.`;
    }

    // Default general response
    return `🤖 AI Assistant Response:

Thank you for your query: "${query}"

I've processed your request using our advanced AI models and MCP server integrations. Here's a comprehensive response:

**Analysis Summary:**
Your query has been analyzed using multiple AI models including Amazon Bedrock foundation models. The system has considered various factors and data sources to provide you with the most accurate response.

**Key Points:**
• Comprehensive analysis completed
• Multiple data sources consulted
• AI model confidence: 94%
• Processing completed successfully

**Additional Information:**
This response was generated using our Third-Eye Agentic AI Platform, which combines multiple AI models and data sources to provide intelligent, contextual responses.

For more specific analysis, please provide additional context or refine your query.`;
  }

  clearSearch() {
    this.searchQuery = '';
    this.selectedAgent = '';
    this.useAdvancedMode = false;
    this.includeContext = true;
  }

  selectHistoryItem(item: ApiResponse) {
    this.currentResponse.set(item);
    this.searchQuery = item.query;
  }

  clearHistory() {
    if (confirm('Are you sure you want to clear all query history?')) {
      this.queryHistory.set([]);
      this.currentResponse.set(null);
      localStorage.removeItem('thirdEyeQueryHistory');
      alert('Query history cleared successfully.');
    }
  }

  exportResults() {
    const data = this.queryHistory();
    const jsonData = JSON.stringify(data, null, 2);
    const blob = new Blob([jsonData], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `third-eye-queries-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    window.URL.revokeObjectURL(url);
    alert('Query results exported successfully!');
  }

  getSuccessRate(): number {
    const history = this.queryHistory();
    if (history.length === 0) return 100;
    const successCount = history.filter(q => q.status === 'success').length;
    return Math.round((successCount / history.length) * 100);
  }

  formatTime(timestamp: Date): string {
    return new Date(timestamp).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  private loadQueryHistory() {
    if (typeof window !== 'undefined' && window.localStorage) {
      const stored = localStorage.getItem('thirdEyeQueryHistory');
      if (stored) {
        try {
          const history = JSON.parse(stored);
          this.queryHistory.set(history.map((item: any) => ({
            ...item,
            timestamp: new Date(item.timestamp)
          })));
        } catch (error) {
          console.error('Error loading query history:', error);
        }
      }
    }
  }

  private saveQueryHistory() {
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.setItem('thirdEyeQueryHistory', JSON.stringify(this.queryHistory()));
    }
  }
}