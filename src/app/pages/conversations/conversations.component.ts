import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { trigger, transition, style, animate, state } from '@angular/animations';

interface ApiResponse {
  id: string;
  query: string;
  response: string;
  timestamp: Date;
  status: 'success' | 'error' | 'loading';
  processingTime?: number;
  agent?: string;
  advancedMode?: boolean;
  includeContext?: boolean;
}

@Component({
  selector: 'app-conversations',
  standalone: true,
  imports: [CommonModule, FormsModule],
  animations: [
    trigger('fadeIn', [
      transition(':enter', [
        style({ opacity: 0, transform: 'translateY(20px)' }),
        animate('300ms ease-out', style({ opacity: 1, transform: 'translateY(0)' }))
      ])
    ]),
    trigger('slideIn', [
      transition(':enter', [
        style({ opacity: 0, transform: 'translateX(-20px)' }),
        animate('400ms ease-out', style({ opacity: 1, transform: 'translateX(0)' }))
      ])
    ]),
    trigger('scaleIn', [
      transition(':enter', [
        style({ opacity: 0, transform: 'scale(0.9)' }),
        animate('200ms ease-out', style({ opacity: 1, transform: 'scale(1)' }))
      ])
    ])
  ],
  template: `
    <div class="conversations-container">
      <!-- Header -->
      <div class="conversations-header" @fadeIn>
        <div class="header-content">
          <h1>🤖 AI Search & Query Interface</h1>
          <p>Enter your queries and get intelligent responses from our AI agents</p>
        </div>
        <div class="header-stats">
          <div class="stat-item" @scaleIn>
            <span class="stat-value">{{ queryHistory.length }}</span>
            <span class="stat-label">Total Queries</span>
          </div>
          <div class="stat-item" @scaleIn>
            <span class="stat-value">{{ getSuccessRate() }}%</span>
            <span class="stat-label">Success Rate</span>
          </div>
        </div>
      </div>

      <!-- Search Input Section -->
      <div class="search-section" @slideIn>
        <div class="search-card">
          <div class="search-header">
            <h2>🔍 Enter Your Query</h2>
            <div class="search-options">
              <select [(ngModel)]="selectedAgent" name="selectedAgent" class="agent-select">
                <option value="">Select AI Agent</option>
                <option value="data-analyst">📊 Data Analyst</option>
                <option value="code-assistant">💻 Code Assistant</option>
                <option value="research">🔬 Research Assistant</option>
                <option value="general">🤖 General AI</option>
              </select>
              <div class="selected-agent-indicator" *ngIf="selectedAgent" @scaleIn>
                <span class="agent-badge">{{ getAgentName(selectedAgent) }} selected</span>
              </div>
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
              [disabled]="isProcessing"
              class="search-input">
            </textarea>
            
            <div class="search-actions">
              <div class="action-buttons">
                <button 
                  class="clear-btn" 
                  (click)="clearSearch()"
                  [disabled]="isProcessing">
                  🗑️ Clear
                </button>
                <button 
                  class="search-btn" 
                  (click)="executeSearch()"
                  [disabled]="isButtonDisabled">
                  <span *ngIf="!isProcessing">🚀 Start Search</span>
                  <span *ngIf="isProcessing">
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
            <button class="export-btn" (click)="exportResults()" [disabled]="queryHistory.length === 0">
              📥 Export
            </button>
            <button class="clear-history-btn" (click)="clearHistory()" [disabled]="queryHistory.length === 0">
              🗑️ Clear History
            </button>
          </div>
        </div>

        <!-- Current Response -->
        <div class="current-response" *ngIf="currentResponse" @fadeIn>
          <div class="response-card" [class]="currentResponse.status">
            <div class="response-header">
              <div class="response-meta">
                <span class="query-text">{{ currentResponse.query }}</span>
                <div class="response-details">
                  <span class="response-time">{{ formatTime(currentResponse.timestamp) }}</span>
                  <span class="response-agent" *ngIf="currentResponse.agent">
                    🤖 {{ getAgentName(currentResponse.agent) }}
                  </span>
                  <span class="response-mode" *ngIf="currentResponse.advancedMode">⚙️ Advanced</span>
                </div>
              </div>
              <div class="response-status" [class]="currentResponse.status">
                {{ currentResponse.status }}
              </div>
            </div>
            
            <div class="response-content">
              <div class="response-text" *ngIf="currentResponse.status === 'success'">
                {{ currentResponse.response }}
              </div>
              <div class="error-text" *ngIf="currentResponse.status === 'error'">
                ❌ Error: {{ currentResponse.response }}
              </div>
              <div class="loading-text" *ngIf="currentResponse.status === 'loading'">
                <div class="loading-animation">
                  <div class="dot"></div>
                  <div class="dot"></div>
                  <div class="dot"></div>
                </div>
                Processing your query...
              </div>
            </div>

            <div class="response-footer" *ngIf="currentResponse.processingTime">
              <span class="processing-time">
                ⚡ Processed in {{ currentResponse.processingTime }}ms
              </span>
            </div>
          </div>
        </div>

        <!-- Query History -->
        <div class="history-section" *ngIf="queryHistory.length > 0" @slideIn>
          <h3>📚 Query History</h3>
          <div class="history-list">
            <div class="history-item" 
                 *ngFor="let item of queryHistory.slice().reverse(); let i = index"
                 (click)="selectHistoryItem(item)"
                 @fadeIn>
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
        <div class="empty-output" *ngIf="queryHistory.length === 0 && !currentResponse" @fadeIn>
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

  // State management
  isProcessing = false;
  currentResponse: ApiResponse | null = null;
  queryHistory: ApiResponse[] = [];

  private apiBaseUrl = 'http://localhost:8000/api';
  private http = inject(HttpClient);

  ngOnInit() {
    console.log('💬 ConversationsComponent initialized - Enhanced Version with Animations');
    this.loadQueryHistory();
  }

  get isButtonDisabled(): boolean {
    return !this.searchQuery || this.searchQuery.trim().length === 0 || this.isProcessing;
  }

  async executeSearch() {
    if (!this.searchQuery || !this.searchQuery.trim()) {
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

    this.currentResponse = loadingResponse;
    this.isProcessing = true;

    try {
      // Make actual API call to backend
      console.log('🚀 Executing search:', {
        query: this.searchQuery,
        agent: this.selectedAgent
      });
      
      // Call the new backend endpoint for conversations
      const response = await firstValueFrom(
        this.http.post<any>(
          `${this.apiBaseUrl}/conversations/start`,
          {
            agent_type: this.selectedAgent || 'auto',
            query_text: this.searchQuery,
            include_context: true
          }
        )
      );
      
      const processingTime = Date.now() - startTime;
      
      const successResponse: ApiResponse = {
        id: response.conversation_id || queryId,
        query: this.searchQuery,
        response: response.response?.content || response.result || response.response || 'Query processed successfully',
        timestamp: new Date(),
        status: 'success',
        processingTime,
        agent: response.agent_type || this.selectedAgent || 'auto'
      };

      this.currentResponse = successResponse;
      this.queryHistory = [...this.queryHistory, successResponse];
      this.saveQueryHistory();

      console.log('✅ Search completed successfully');

    } catch (error: any) {
      console.error('❌ Search error:', error);
      
      const errorMessage = error?.error?.detail || error?.message || 'Failed to process query. Please try again.';
      
      const errorResponse: ApiResponse = {
        id: queryId,
        query: this.searchQuery,
        response: errorMessage,
        timestamp: new Date(),
        status: 'error'
      };

      this.currentResponse = errorResponse;
      this.queryHistory = [...this.queryHistory, errorResponse];
    } finally {
      this.isProcessing = false;
    }
  }

  clearSearch() {
    this.searchQuery = '';
    this.selectedAgent = '';
  }

  selectHistoryItem(item: ApiResponse) {
    this.currentResponse = item;
    this.searchQuery = item.query;
  }

  clearHistory() {
    if (confirm('Are you sure you want to clear all query history?')) {
      this.queryHistory = [];
      this.currentResponse = null;
      localStorage.removeItem('thirdEyeQueryHistory');
      alert('Query history cleared successfully.');
    }
  }

  exportResults() {
    const data = this.queryHistory;
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
    const history = this.queryHistory;
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

  getAgentName(agentId: string): string {
    const agentNames: { [key: string]: string } = {
      'data-analyst': 'Data Analyst',
      'code-assistant': 'Code Assistant',
      'research': 'Research Assistant',
      'general': 'General AI'
    };
    return agentNames[agentId] || 'AI Agent';
  }

  private loadQueryHistory() {
    if (typeof window !== 'undefined' && window.localStorage) {
      const stored = localStorage.getItem('thirdEyeQueryHistory');
      if (stored) {
        try {
          const history = JSON.parse(stored);
          this.queryHistory = history.map((item: any) => ({
            ...item,
            timestamp: new Date(item.timestamp)
          }));
        } catch (error) {
          console.error('Error loading query history:', error);
        }
      }
    }
  }

  private saveQueryHistory() {
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.setItem('thirdEyeQueryHistory', JSON.stringify(this.queryHistory));
    }
  }
}