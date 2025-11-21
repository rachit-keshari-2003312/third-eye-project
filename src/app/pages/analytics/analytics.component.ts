import { Component, OnInit, inject, ViewChild, ElementRef, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { trigger, transition, style, animate } from '@angular/animations';
import { Chart, ChartConfiguration, registerables } from 'chart.js';

Chart.register(...registerables);

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
  animations: [
    trigger('fadeIn', [
      transition(':enter', [
        style({ opacity: 0, transform: 'translateY(20px)' }),
        animate('300ms ease-out', style({ opacity: 1, transform: 'translateY(0)' }))
      ])
    ])
  ],
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
            <span class="stat-value">{{ queryHistory.length }}</span>
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
              [disabled]="isProcessing"
              class="query-input">
            </textarea>
            
            <div class="query-actions">
              <div class="action-buttons">
                <button 
                  class="clear-btn" 
                  (click)="clearQuery()"
                  [disabled]="isProcessing">
                  Clear
                </button>
                <button 
                  class="execute-btn" 
                  (click)="executeQuery()"
                  [disabled]="!queryText.trim() || isProcessing">
                  <span *ngIf="!isProcessing">⚡ Execute Query</span>
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

      <!-- JSON Output Section -->
      <div class="output-section">
        <div class="output-header">
          <h2>📋 Response</h2>
          <div class="output-controls">
            <div class="view-toggle" *ngIf="canShowChart">
              <button 
                class="toggle-btn" 
                [class.active]="viewMode === 'json'"
                (click)="toggleView('json')">
                📋 JSON
              </button>
              <button 
                class="toggle-btn" 
                [class.active]="viewMode === 'chart'"
                (click)="toggleView('chart')">
                📊 Chart
              </button>
            </div>
            <button class="copy-btn" (click)="copyToClipboard()" [disabled]="!currentResponse">
              📋 Copy
            </button>
            <button class="download-btn" (click)="downloadJSON()" [disabled]="!currentResponse">
              💾 Download
            </button>
            <button class="clear-output-btn" (click)="clearOutput()" [disabled]="!currentResponse">
              🗑️ Clear
            </button>
          </div>
        </div>

        <!-- Current JSON Response -->
        <div class="json-response" *ngIf="currentResponse">
          <div class="response-card" [class]="currentResponse?.status">
            <div class="response-header">
              <div class="response-meta">
                <span class="query-text">{{ currentResponse?.query }}</span>
                <span class="response-time">{{ formatTime(currentResponse!.timestamp) }}</span>
              </div>
              <div class="response-status" [class]="currentResponse?.status">
                {{ currentResponse?.status }}
              </div>
            </div>
            
            <!-- JSON View -->
            <div class="json-content" *ngIf="viewMode === 'json'">
              <div class="json-output" *ngIf="currentResponse!.status === 'success'">
                <pre class="json-text">{{ formatJSON(currentResponse!.response) }}</pre>
              </div>
              <div class="error-output" *ngIf="currentResponse!.status === 'error'">
                <pre class="error-text">{{ currentResponse!.response }}</pre>
              </div>
              <div class="loading-output" *ngIf="currentResponse!.status === 'loading'">
                <div class="loading-animation">
                  <div class="dot"></div>
                  <div class="dot"></div>
                  <div class="dot"></div>
                </div>
                <span>Executing query...</span>
              </div>
            </div>
            
            <!-- Chart View -->
            <div class="chart-content" *ngIf="viewMode === 'chart' && canShowChart">
              <div class="chart-type-selector">
                <button 
                  class="chart-type-btn" 
                  [class.active]="chartType === 'bar'"
                  (click)="changeChartType('bar')"
                  title="Bar Chart">
                  📊 Bar
                </button>
                <button 
                  class="chart-type-btn" 
                  [class.active]="chartType === 'line'"
                  (click)="changeChartType('line')"
                  title="Line Chart">
                  📈 Line
                </button>
                <button 
                  class="chart-type-btn" 
                  [class.active]="chartType === 'doughnut'"
                  (click)="changeChartType('doughnut')"
                  title="Doughnut Chart">
                  🍩 Doughnut
                </button>
                <button 
                  class="chart-type-btn" 
                  [class.active]="chartType === 'pie'"
                  (click)="changeChartType('pie')"
                  title="Pie Chart">
                  🥧 Pie
                </button>
              </div>
              <div class="chart-wrapper">
                <canvas #chartCanvas></canvas>
              </div>
            </div>

            <div class="response-footer" *ngIf="currentResponse!.processingTime">
              <span class="processing-time">
                ⚡ Processed in {{ currentResponse!.processingTime }}ms
              </span>
              <span class="data-size">
                📊 Response size: {{ getResponseSize() }} characters
              </span>
            </div>
          </div>
        </div>

        <!-- Query History -->
        <div class="history-section" *ngIf="queryHistory.length > 0">
          <h3>📚 Query History</h3>
          <div class="history-list">
            <div class="history-item" 
                 *ngFor="let item of queryHistory.slice().reverse(); let i = index"
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
        <div class="empty-output" *ngIf="!currentResponse">
          <div class="empty-icon">📊</div>
          <h3>No analytics data</h3>
          <p>Enter a query above and click "Execute Query" to see JSON results here.</p>
        </div>
      </div>
    </div>
  `,
  styleUrls: ['./analytics.component.scss']
})
export class AnalyticsComponent implements OnInit, AfterViewInit {
  
  @ViewChild('chartCanvas') chartCanvas!: ElementRef<HTMLCanvasElement>;
  
  // Form inputs
  queryText = '';
  outputFormat = 'json';
  viewMode: 'json' | 'chart' = 'chart'; // Default to chart view

  // State management
  isProcessing = false;
  currentResponse: QueryResponse | null = null;
  queryHistory: QueryResponse[] = [];
  
  // Chart management
  private chart: Chart | null = null;
  canShowChart = false;
  chartType: 'bar' | 'line' | 'pie' | 'doughnut' = 'bar';

  private apiBaseUrl = 'http://localhost:8000/api';
  private http = inject(HttpClient);

  get isButtonDisabled(): boolean {
    return !this.queryText || this.queryText.trim().length === 0 || this.isProcessing;
  }

  ngOnInit() {
    console.log('📈 AnalyticsComponent initialized - Enhanced with Charts');
    this.loadQueryHistory();
  }
  
  ngAfterViewInit() {
    // Chart canvas is now available
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

    this.currentResponse = loadingResponse;
    this.isProcessing = true;

    try {
      // Generate mock JSON response for analytics
      const jsonResponse = await this.generateAnalyticsJSON(this.queryText);
      const processingTime = Date.now() - startTime;
      
      const successResponse: QueryResponse = {
        id: queryId,
        query: this.queryText,
        response: jsonResponse,
        timestamp: new Date(),
        status: 'success',
        processingTime
      };

      this.currentResponse = successResponse;
      this.queryHistory = [...this.queryHistory, successResponse];
      this.saveQueryHistory();
      
      // Check if we can show chart
      this.canShowChart = this.checkIfChartable(jsonResponse);
      
      // Auto-switch to chart view and generate
      if (this.canShowChart) {
        this.viewMode = 'chart';
        this.determineChartType(jsonResponse);
        setTimeout(() => this.generateChart(), 100);
      } else {
        this.viewMode = 'json';
      }

    } catch (error) {
      console.error('❌ Query error:', error);
      
      const errorResponse: QueryResponse = {
        id: queryId,
        query: this.queryText,
        response: { error: 'Failed to process analytics query', details: String(error) },
        timestamp: new Date(),
        status: 'error'
      };

      this.currentResponse = errorResponse;
      this.queryHistory = [...this.queryHistory, errorResponse];
    } finally {
      this.isProcessing = false;
    }
  }

  private async generateAnalyticsJSON(query: string): Promise<any> {
    // Simulate processing time
    await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 1000));

    const queryLower = query.toLowerCase();
    
    // Return funnel data format (like the example provided)
    if (queryLower.includes('funnel') || queryLower.includes('status') || queryLower.includes('stage')) {
      return {
        success: true,
        prompt: query,
        session_id: this.generateSessionId(),
        analysis: {},
        service: "redash",
        action: "sql_query",
        result: null,
        raw_data: {
          columns: [
            {
              friendly_name: "Status",
              type: "string",
              name: "current_status"
            },
            {
              friendly_name: "Count",
              type: "integer",
              name: "count"
            }
          ],
          rows: [
            { count: 21123, current_status: "CREATED" },
            { count: 7993, current_status: "APPLICATION_APPROVED" },
            { count: 3456, current_status: "UTR_RECEIVED" },
            { count: 2134, current_status: "COMPLETED" }
          ]
        },
        answer: "Here's the funnel data showing the progression of applications through different stages. There are 21,123 applications in the CREATED stage, 7,993 have been approved, 3,456 have received UTR, and 2,134 are completed.",
        llm_intent: null,
        sql: "SELECT ast.current_status, COUNT(*) AS count FROM a_application_stage_tracker ast GROUP BY ast.current_status;",
        explanation: "This query retrieves the funnel data by counting applications in each status stage.",
        row_count: 4,
        data_source_id: 79,
        error: null,
        timestamp: new Date().toISOString()
      };
    }
    
    // Return sales data
    if (queryLower.includes('sales') || queryLower.includes('revenue') || queryLower.includes('product')) {
      return {
        success: true,
        prompt: query,
        session_id: this.generateSessionId(),
        analysis: {},
        service: "redash",
        action: "sql_query",
        result: null,
        raw_data: {
          columns: [
            {
              friendly_name: "Product Category",
              type: "string",
              name: "category"
            },
            {
              friendly_name: "Revenue",
              type: "integer",
              name: "revenue"
            }
          ],
          rows: [
            { category: "Electronics", revenue: 45230 },
            { category: "Clothing", revenue: 32150 },
            { category: "Home & Garden", revenue: 28900 },
            { category: "Sports", revenue: 19800 },
            { category: "Books", revenue: 15600 }
          ]
        },
        answer: "Revenue breakdown by product category shows Electronics leading with $45,230, followed by Clothing at $32,150.",
        llm_intent: null,
        sql: "SELECT category, SUM(revenue) as revenue FROM products GROUP BY category ORDER BY revenue DESC;",
        explanation: "This query aggregates revenue by product category.",
        row_count: 5,
        data_source_id: 79,
        error: null,
        timestamp: new Date().toISOString()
      };
    }
    
    // Return user engagement data
    if (queryLower.includes('user') || queryLower.includes('engagement') || queryLower.includes('active')) {
      return {
        success: true,
        prompt: query,
        session_id: this.generateSessionId(),
        analysis: {},
        service: "redash",
        action: "sql_query",
        result: null,
        raw_data: {
          columns: [
            {
              friendly_name: "Day",
              type: "string",
              name: "day"
            },
            {
              friendly_name: "Active Users",
              type: "integer",
              name: "users"
            }
          ],
          rows: [
            { day: "Monday", users: 8450 },
            { day: "Tuesday", users: 9120 },
            { day: "Wednesday", users: 8890 },
            { day: "Thursday", users: 9560 },
            { day: "Friday", users: 10230 },
            { day: "Saturday", users: 7650 },
            { day: "Sunday", users: 6890 }
          ]
        },
        answer: "Weekly user engagement shows peak activity on Friday with 10,230 active users, and lowest on Sunday with 6,890 users.",
        llm_intent: null,
        sql: "SELECT DATE_FORMAT(created_at, '%W') as day, COUNT(DISTINCT user_id) as users FROM user_activity WHERE created_at >= NOW() - INTERVAL 7 DAY GROUP BY day;",
        explanation: "This query counts active users by day of the week for the last 7 days.",
        row_count: 7,
        data_source_id: 79,
        error: null,
        timestamp: new Date().toISOString()
      };
    }
    
    // Default: Return channel performance data
    return {
      success: true,
      prompt: query,
      session_id: this.generateSessionId(),
      analysis: {},
      service: "redash",
      action: "sql_query",
      result: null,
      raw_data: {
        columns: [
          {
            friendly_name: "Channel",
            type: "string",
            name: "channel_name"
          },
          {
            friendly_name: "Applications",
            type: "integer",
            name: "total_applications"
          }
        ],
        rows: [
          { channel_name: "EDI_PP_01", total_applications: 15234 },
          { channel_name: "WEB_DIRECT", total_applications: 12890 },
          { channel_name: "MOBILE_APP", total_applications: 9876 },
          { channel_name: "PARTNER_API", total_applications: 7654 },
          { channel_name: "BRANCH", total_applications: 5432 }
        ]
      },
      answer: "Channel performance analysis shows EDI_PP_01 leading with 15,234 applications, followed by WEB_DIRECT with 12,890.",
      llm_intent: null,
      sql: "SELECT channel_name, COUNT(*) as total_applications FROM applications GROUP BY channel_name ORDER BY total_applications DESC;",
      explanation: "This query counts total applications by channel source.",
      row_count: 5,
      data_source_id: 79,
      error: null,
      timestamp: new Date().toISOString()
    };
  }
  
  private generateSessionId(): string {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0;
      const v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }
    
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
  }

  clearOutput() {
    this.currentResponse = null;
    this.canShowChart = false;
    this.viewMode = 'json';
    if (this.chart) {
      this.chart.destroy();
      this.chart = null;
    }
  }
  
  checkIfChartable(data: any): boolean {
    // Check if data has the structure needed for charts
    if (data && data.raw_data && data.raw_data.rows && data.raw_data.columns) {
      const rows = data.raw_data.rows;
      const columns = data.raw_data.columns;
      
      // Need at least 2 columns and 1 row
      if (rows.length > 0 && columns.length >= 2) {
        // Check if we have at least one numeric column
        const hasNumeric = columns.some((col: any) => 
          col.type === 'integer' || col.type === 'float' || col.type === 'number'
        );
        return hasNumeric;
      }
    }
    return false;
  }
  
  determineChartType(data: any) {
    if (!data || !data.raw_data) return;
    
    const rows = data.raw_data.rows;
    const rowCount = rows.length;
    
    // Funnel or stage data -> Bar chart
    if (data.prompt?.toLowerCase().includes('funnel') || 
        data.prompt?.toLowerCase().includes('status') ||
        data.prompt?.toLowerCase().includes('stage')) {
      this.chartType = 'bar';
    }
    // Time series or daily data -> Line chart
    else if (data.prompt?.toLowerCase().includes('day') || 
             data.prompt?.toLowerCase().includes('week') ||
             data.prompt?.toLowerCase().includes('time')) {
      this.chartType = 'line';
    }
    // Few items (<=5) with percentages -> Doughnut chart
    else if (rowCount <= 5) {
      this.chartType = 'doughnut';
    }
    // Default to bar
    else {
      this.chartType = 'bar';
    }
  }
  
  generateChart() {
    if (!this.currentResponse || !this.chartCanvas) return;
    
    const data = this.currentResponse.response;
    if (!data || !data.raw_data) return;
    
    const { rows, columns } = data.raw_data;
    
    // Destroy existing chart
    if (this.chart) {
      this.chart.destroy();
    }
    
    // Find label and value columns
    const labelColumn = columns.find((col: any) => col.type === 'string') || columns[0];
    const valueColumn = columns.find((col: any) => 
      col.type === 'integer' || col.type === 'float' || col.type === 'number'
    ) || columns[1];
    
    const labels = rows.map((row: any) => row[labelColumn.name]);
    const values = rows.map((row: any) => row[valueColumn.name]);
    
    // Color schemes based on chart type
    const colors = this.getChartColors(values.length);
    
    const ctx = this.chartCanvas.nativeElement.getContext('2d');
    
    let dataset: any;
    
    if (this.chartType === 'line') {
      // Line chart with gradient fill
      const gradient = ctx!.createLinearGradient(0, 0, 0, 400);
      gradient.addColorStop(0, 'rgba(102, 126, 234, 0.3)');
      gradient.addColorStop(1, 'rgba(102, 126, 234, 0.05)');
      
      dataset = {
        label: valueColumn.friendly_name || valueColumn.name,
        data: values,
        borderColor: 'rgba(102, 126, 234, 1)',
        backgroundColor: gradient,
        borderWidth: 3,
        fill: true,
        tension: 0.4,
        pointBackgroundColor: 'rgba(102, 126, 234, 1)',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointRadius: 5,
        pointHoverRadius: 7
      };
    } else if (this.chartType === 'doughnut' || this.chartType === 'pie') {
      // Pie/Doughnut with multiple colors
      dataset = {
        label: valueColumn.friendly_name || valueColumn.name,
        data: values,
        backgroundColor: colors,
        borderColor: '#fff',
        borderWidth: 3,
        hoverOffset: 15
      };
    } else {
      // Bar chart with gradient
      const gradient = ctx!.createLinearGradient(0, 0, 0, 400);
      gradient.addColorStop(0, 'rgba(102, 126, 234, 0.9)');
      gradient.addColorStop(1, 'rgba(118, 75, 162, 0.9)');
      
      dataset = {
        label: valueColumn.friendly_name || valueColumn.name,
        data: values,
        backgroundColor: this.chartType === 'bar' ? colors : gradient,
        borderColor: 'rgba(102, 126, 234, 1)',
        borderWidth: 2,
        borderRadius: 10,
        hoverBackgroundColor: colors.map((c: string) => c.replace('0.8', '1'))
      };
    }
    
    const config: ChartConfiguration = {
      type: this.chartType,
      data: {
        labels: labels,
        datasets: [dataset]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true,
            position: this.chartType === 'doughnut' || this.chartType === 'pie' ? 'right' : 'top',
            labels: {
              font: {
                size: 13,
                weight: 'bold'
              },
              color: '#2c3e50',
              padding: 15,
              usePointStyle: this.chartType === 'doughnut' || this.chartType === 'pie'
            }
          },
          title: {
            display: true,
            text: this.getChartTitle(data),
            font: {
              size: 20,
              weight: 'bold'
            },
            color: '#2c3e50',
            padding: 20
          },
          tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.85)',
            titleFont: {
              size: 14,
              weight: 'bold'
            },
            bodyFont: {
              size: 13
            },
            padding: 14,
            cornerRadius: 10,
            displayColors: true,
            callbacks: {
              label: (context: any) => {
                const label = context.dataset.label || '';
                const value = context.parsed.y || context.parsed;
                const total = context.dataset.data.reduce((a: number, b: number) => a + b, 0);
                const percentage = ((value / total) * 100).toFixed(1);
                return ` ${label}: ${value.toLocaleString()} (${percentage}%)`;
              }
            }
          }
        },
        ...(this.chartType !== 'doughnut' && this.chartType !== 'pie' ? {
          scales: {
            y: {
              beginAtZero: true,
              grid: {
                color: 'rgba(0, 0, 0, 0.06)',
                drawBorder: false
              },
              ticks: {
                font: {
                  size: 12
                },
                color: '#7f8c8d',
                padding: 10,
                callback: (value: any) => {
                  if (value >= 1000) {
                    return (value / 1000).toFixed(1) + 'K';
                  }
                  return value;
                }
              }
            },
            x: {
              grid: {
                display: false,
                drawBorder: false
              },
              ticks: {
                font: {
                  size: 12
                },
                color: '#7f8c8d',
                padding: 10
              }
            }
          }
        } : {})
      }
    };
    
    this.chart = new Chart(this.chartCanvas.nativeElement, config);
  }
  
  getChartColors(count: number): string[] {
    const colorSchemes = [
      'rgba(102, 126, 234, 0.8)',  // Purple
      'rgba(250, 112, 154, 0.8)',  // Pink
      'rgba(79, 172, 254, 0.8)',   // Blue
      'rgba(254, 225, 64, 0.8)',   // Yellow
      'rgba(46, 213, 115, 0.8)',   // Green
      'rgba(255, 107, 107, 0.8)',  // Red
      'rgba(72, 219, 251, 0.8)',   // Cyan
      'rgba(255, 177, 66, 0.8)'    // Orange
    ];
    
    return Array.from({ length: count }, (_, i) => colorSchemes[i % colorSchemes.length]);
  }
  
  getChartTitle(data: any): string {
    const prompt = data.prompt || '';
    if (prompt.toLowerCase().includes('funnel')) {
      return '📊 Application Funnel Status';
    } else if (prompt.toLowerCase().includes('sales') || prompt.toLowerCase().includes('revenue')) {
      return '💰 Revenue by Category';
    } else if (prompt.toLowerCase().includes('user') || prompt.toLowerCase().includes('engagement')) {
      return '👥 User Engagement';
    } else if (prompt.toLowerCase().includes('channel')) {
      return '📡 Channel Performance';
    }
    return '📊 Data Visualization';
  }
  
  changeChartType(type: 'bar' | 'line' | 'pie' | 'doughnut') {
    this.chartType = type;
    this.generateChart();
  }
  
  toggleView(mode: 'json' | 'chart') {
    this.viewMode = mode;
    if (mode === 'chart' && this.canShowChart) {
      setTimeout(() => this.generateChart(), 100);
    }
  }

  loadHistoryItem(item: QueryResponse) {
    this.currentResponse = item;
    this.queryText = item.query;
  }

  copyToClipboard() {
    const response = this.currentResponse;
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
    const response = this.currentResponse;
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
    return JSON.stringify(obj, null, 2);
  }

  getJSONPreview(obj: any): string {
    const preview = JSON.stringify(obj, null, 0);
    return preview.length > 100 ? preview.substring(0, 100) + '...' : preview;
  }

  getSuccessfulQueries(): number {
    return this.queryHistory.filter(q => q.status === 'success').length;
  }

  getResponseSize(): number {
    const response = this.currentResponse;
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

  private loadQueryHistory() {
    if (typeof window !== 'undefined' && window.localStorage) {
      const stored = localStorage.getItem('thirdEyeAnalyticsHistory');
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
      localStorage.setItem('thirdEyeAnalyticsHistory', JSON.stringify(this.queryHistory));
    }
  }
}