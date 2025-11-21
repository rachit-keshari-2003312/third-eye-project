import { Component, OnInit, signal, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';

interface QueryResponse {
  id: string;
  query: string;
  response: any; // JSON response
  timestamp: Date;
  status: 'success' | 'error' | 'loading';
  processingTime?: number;
}

@Component({
  selector: 'app-analytics',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="analytics-container">
      <!-- Header -->
      <div class="analytics-header">
        <div class="header-content">
          <h1>📊 Analytics Query Interface</h1>
          <p>Enter queries and get structured JSON responses for data analysis</p>
        </div>
        <div class="header-stats">
          <div class="stat-item">
            <span class="stat-value">{{ queryHistory().length }}</span>
            <span class="stat-label">Total Queries</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ getSuccessfulQueries() }}</span>
            <span class="stat-label">Successful</span>
          </div>
        </div>
      </div>

      <!-- Query Input Section -->
      <div class="query-section">
        <div class="query-card">
          <div class="query-header">
            <h2>🔍 Enter Analytics Query</h2>
            <div class="query-options">
              <select [(ngModel)]="outputFormat" name="outputFormat">
                <option value="json">JSON Output</option>
                <option value="table">Table Format</option>
                <option value="chart">Chart Data</option>
              </select>
            </div>
          </div>

          <div class="query-input-container">
            <textarea 
              [(ngModel)]="queryText" 
              name="queryText"
              placeholder="Enter your analytics query here...

Examples:
• Get user engagement metrics for last 30 days
• Show revenue breakdown by product category
• Analyze customer retention rates
• Generate performance dashboard data"
              rows="6"
              [disabled]="isProcessing()"
              class="query-input">
            </textarea>
            
            <div class="query-actions">
              <div class="query-controls">
                <label class="control-item">
                  <input type="checkbox" [(ngModel)]="includeMetadata" name="includeMetadata">
                  <span>Include Metadata</span>
                </label>
                <label class="control-item">
                  <input type="checkbox" [(ngModel)]="prettyFormat" name="prettyFormat">
                  <span>Pretty Format</span>
                </label>
              </div>
              
              <div class="action-buttons">
                <button 
                  class="clear-btn" 
                  (click)="clearQuery()"
                  [disabled]="isProcessing()">
                  Clear
                </button>
                <button 
                  class="execute-btn" 
                  (click)="executeQuery()"
                  [disabled]="!queryText.trim() || isProcessing()">
                  <span *ngIf="!isProcessing()">⚡ Execute Query</span>
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

      <!-- JSON Output Section -->
      <div class="output-section">
        <div class="output-header">
          <h2>📋 JSON Response</h2>
          <div class="output-controls">
            <button class="copy-btn" (click)="copyToClipboard()" [disabled]="!currentResponse()">
              📋 Copy JSON
            </button>
            <button class="download-btn" (click)="downloadJSON()" [disabled]="!currentResponse()">
              💾 Download
            </button>
            <button class="clear-output-btn" (click)="clearOutput()" [disabled]="!currentResponse()">
              🗑️ Clear
            </button>
          </div>
        </div>

        <!-- Current JSON Response -->
        <div class="json-response" *ngIf="currentResponse()">
          <div class="response-card" [class]="currentResponse()?.status">
            <div class="response-header">
              <div class="response-meta">
                <span class="query-text">{{ currentResponse()?.query }}</span>
                <span class="response-time">{{ formatTime(currentResponse()!.timestamp) }}</span>
              </div>
              <div class="response-status" [class]="currentResponse()?.status">
                {{ currentResponse()?.status }}
              </div>
            </div>
            
            <div class="json-content">
              <div class="json-output" *ngIf="currentResponse()!.status === 'success'">
                <pre class="json-text">{{ formatJSON(currentResponse()!.response) }}</pre>
              </div>
              <div class="error-output" *ngIf="currentResponse()!.status === 'error'">
                <pre class="error-text">{{ currentResponse()!.response }}</pre>
              </div>
              <div class="loading-output" *ngIf="currentResponse()!.status === 'loading'">
                <div class="loading-animation">
                  <div class="dot"></div>
                  <div class="dot"></div>
                  <div class="dot"></div>
                </div>
                <span>Executing query...</span>
              </div>
            </div>

            <div class="response-footer" *ngIf="currentResponse()!.processingTime">
              <span class="processing-time">
                ⚡ Processed in {{ currentResponse()!.processingTime }}ms
              </span>
              <span class="data-size">
                📊 Response size: {{ getResponseSize() }} characters
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
                 (click)="loadHistoryItem(item)">
              <div class="history-header">
                <span class="history-query">{{ item.query.substring(0, 80) }}{{ item.query.length > 80 ? '...' : '' }}</span>
                <span class="history-time">{{ formatTime(item.timestamp) }}</span>
              </div>
              <div class="history-preview">
                <code>{{ getJSONPreview(item.response) }}</code>
              </div>
              <div class="history-status" [class]="item.status">
                {{ item.status }}
              </div>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div class="empty-output" *ngIf="!currentResponse()">
          <div class="empty-icon">📊</div>
          <h3>No analytics data</h3>
          <p>Enter a query above and click "Execute Query" to see JSON results here.</p>
        </div>
      </div>
    </div>
  `,
  styleUrls: ['./analytics.component.scss']
})
export class AnalyticsComponent implements OnInit {
  
  // Form inputs
  queryText = '';
  outputFormat = 'json';
  includeMetadata = true;
  prettyFormat = true;

  // State management
  isProcessing = signal(false);
  currentResponse = signal<QueryResponse | null>(null);
  queryHistory = signal<QueryResponse[]>([]);

  private apiBaseUrl = 'http://18.207.167.104:3001/api';
  private http = inject(HttpClient);

  ngOnInit() {
    console.log('📈 AnalyticsComponent initialized');
    this.loadQueryHistory();
  }

  async executeQuery() {
    if (!this.queryText.trim()) {
      alert('Please enter an analytics query.');
      return;
    }

    const queryId = Date.now().toString();
    const startTime = Date.now();

    // Create loading response
    const loadingResponse: QueryResponse = {
      id: queryId,
      query: this.queryText,
      response: null,
      timestamp: new Date(),
      status: 'loading'
    };

    this.currentResponse.set(loadingResponse);
    this.isProcessing.set(true);

    try {
      // Call the backend analytics endpoint
      console.log('🚀 Calling analytics API:', {
        query: this.queryText,
        output_format: this.outputFormat
      });

      const response = await this.http.post<any>(`${this.apiBaseUrl}/analytics/execute`, {
        query: this.queryText,
        output_format: this.outputFormat,
        session_id: this.generateSessionId()
      }).toPromise();

      const processingTime = Date.now() - startTime;
      const jsonResponse = response.result || response;
      
      console.log('✅ Backend response:', response);
      
      const successResponse: QueryResponse = {
        id: response.query_id || queryId,
        query: this.queryText,
        response: jsonResponse,
        timestamp: new Date(),
        status: 'success',
        processingTime
      };

      this.currentResponse.set(successResponse);
      this.queryHistory.update(history => [...history, successResponse]);
      this.saveQueryHistory();

    } catch (error) {
      console.error('❌ Query error:', error);
      
      const errorResponse: QueryResponse = {
        id: queryId,
        query: this.queryText,
        response: { error: 'Failed to process analytics query', details: String(error) },
        timestamp: new Date(),
        status: 'error'
      };

      this.currentResponse.set(errorResponse);
      this.queryHistory.update(history => [...history, errorResponse]);
    } finally {
      this.isProcessing.set(false);
    }
  }

  private async generateAnalyticsJSON(query: string): Promise<any> {
    // Simulate processing time
    await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000));

    const queryLower = query.toLowerCase();
    
    if (queryLower.includes('user') || queryLower.includes('engagement')) {
      return {
        analytics_type: "user_engagement",
        time_period: "last_30_days",
        data: {
          total_users: 12847,
          active_users: 8934,
          engagement_rate: 69.5,
          sessions: {
            total: 45623,
            avg_duration: 342,
            bounce_rate: 23.4
          },
          top_features: [
            { name: "AI Agents", usage: 87.3, trend: "+12%" },
            { name: "Analytics", usage: 76.8, trend: "+8%" },
            { name: "Conversations", usage: 92.1, trend: "+15%" }
          ]
        },
        metadata: {
          generated_at: new Date().toISOString(),
          query: query,
          confidence: 0.94
        }
      };
    }
    
    if (queryLower.includes('revenue') || queryLower.includes('sales')) {
      return {
        analytics_type: "revenue_analysis",
        time_period: "Q4_2024",
        data: {
          total_revenue: 2847392.50,
          growth_rate: 23.7,
          breakdown: {
            subscription: { amount: 1847392.50, percentage: 64.9 },
            one_time: { amount: 678234.20, percentage: 23.8 },
            enterprise: { amount: 321766.80, percentage: 11.3 }
          },
          by_region: [
            { region: "North America", revenue: 1423696.25, growth: "+18%" },
            { region: "Europe", revenue: 854217.50, growth: "+31%" },
            { region: "Asia Pacific", revenue: 569478.75, growth: "+42%" }
          ]
        },
        predictions: {
          next_quarter: 3247892.30,
          confidence_interval: [2987234.10, 3508550.50]
        },
        metadata: {
          generated_at: new Date().toISOString(),
          query: query,
          data_sources: ["sales_db", "analytics_warehouse", "customer_metrics"]
        }
      };
    }
    
    if (queryLower.includes('performance') || queryLower.includes('dashboard')) {
      return {
        analytics_type: "performance_dashboard",
        timestamp: new Date().toISOString(),
        data: {
          system_metrics: {
            cpu_usage: 67.3,
            memory_usage: 84.2,
            disk_usage: 45.7,
            network_throughput: 234.5
          },
          application_metrics: {
            response_time_ms: 234,
            requests_per_second: 1247,
            error_rate: 0.23,
            uptime_percentage: 99.97
          },
          user_metrics: {
            concurrent_users: 1847,
            peak_users_today: 2341,
            avg_session_duration: 18.7,
            conversion_rate: 12.4
          },
          alerts: [
            { level: "warning", message: "Memory usage above 80%", timestamp: new Date().toISOString() },
            { level: "info", message: "Peak traffic detected", timestamp: new Date().toISOString() }
          ]
        },
        metadata: {
          generated_at: new Date().toISOString(),
          query: query,
          refresh_interval: 30
        }
      };
    }

    // Default analytics response
    return {
      analytics_type: "general_analytics",
      query_processed: query,
      data: {
        summary: {
          total_data_points: 15847,
          processing_time_ms: Date.now() % 3000 + 500,
          analysis_confidence: 0.92,
          data_quality_score: 0.87
        },
        insights: [
          "Data shows consistent upward trend",
          "Peak activity detected during business hours",
          "Seasonal patterns identified in user behavior",
          "Optimization opportunities found in data pipeline"
        ],
        metrics: {
          accuracy: 94.7,
          completeness: 89.2,
          timeliness: 97.1,
          relevance: 91.8
        },
        recommendations: [
          { priority: "high", action: "Implement real-time monitoring" },
          { priority: "medium", action: "Optimize data collection frequency" },
          { priority: "low", action: "Review historical data retention policy" }
        ]
      },
      metadata: {
        generated_at: new Date().toISOString(),
        query: query,
        model_version: "third-eye-v1.0",
        data_sources: ["primary_db", "analytics_warehouse", "real_time_stream"]
      }
    };
  }

  clearQuery() {
    this.queryText = '';
    this.outputFormat = 'json';
    this.includeMetadata = true;
    this.prettyFormat = true;
  }

  clearOutput() {
    this.currentResponse.set(null);
  }

  loadHistoryItem(item: QueryResponse) {
    this.currentResponse.set(item);
    this.queryText = item.query;
  }

  copyToClipboard() {
    const response = this.currentResponse();
    if (response) {
      const jsonText = this.formatJSON(response.response);
      navigator.clipboard.writeText(jsonText).then(() => {
        alert('JSON response copied to clipboard!');
      }).catch(err => {
        console.error('Failed to copy: ', err);
        alert('Failed to copy to clipboard');
      });
    }
  }

  downloadJSON() {
    const response = this.currentResponse();
    if (response) {
      const jsonText = this.formatJSON(response.response);
      const blob = new Blob([jsonText], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `analytics-${new Date().toISOString().split('T')[0]}-${response.id}.json`;
      link.click();
      window.URL.revokeObjectURL(url);
      alert('JSON response downloaded successfully!');
    }
  }

  formatJSON(obj: any): string {
    if (this.prettyFormat) {
      return JSON.stringify(obj, null, 2);
    }
    return JSON.stringify(obj);
  }

  getJSONPreview(obj: any): string {
    const preview = JSON.stringify(obj, null, 0);
    return preview.length > 100 ? preview.substring(0, 100) + '...' : preview;
  }

  getSuccessfulQueries(): number {
    return this.queryHistory().filter(q => q.status === 'success').length;
  }

  getResponseSize(): number {
    const response = this.currentResponse();
    if (response && response.response) {
      return JSON.stringify(response.response).length;
    }
    return 0;
  }

  formatTime(timestamp: Date): string {
    return new Date(timestamp).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  generateSessionId(): string {
    // Generate a UUID-like session ID
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0;
      const v = c == 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }

  private loadQueryHistory() {
    if (typeof window !== 'undefined' && window.localStorage) {
      const stored = localStorage.getItem('thirdEyeAnalyticsHistory');
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
      localStorage.setItem('thirdEyeAnalyticsHistory', JSON.stringify(this.queryHistory()));
    }
  }
}