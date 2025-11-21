import { Component, OnInit, Input, signal, ViewChild, ElementRef, AfterViewChecked, effect } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { DashboardService, QueryResult } from '../../services/dashboard.service';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  model?: string;
}

interface ChatbotSession {
  session_id: string;
  messages: ChatMessage[];
  created_at: string;
}

@Component({
  selector: 'app-chatbot',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="chatbot-overlay" *ngIf="isOpen()" (click)="closeChatbot()">
      <div class="chatbot-container" (click)="$event.stopPropagation()">
        <!-- Chatbot Header -->
        <div class="chatbot-header">
          <div class="header-info">
            <div class="chatbot-avatar">🤖</div>
            <div class="header-text">
              <h3>Third-Eye Assistant</h3>
              <span class="status" [class.connected]="bedrockConnected()">
                {{ bedrockConnected() ? 'Connected to Bedrock' : 'Mock Mode' }}
              </span>
            </div>
          </div>
          <button class="close-btn" (click)="closeChatbot()">✕</button>
        </div>

        <!-- Messages Container -->
        <div class="messages-container" #messagesContainer>
          <div class="message" 
               *ngFor="let message of messages()" 
               [class.user]="message.role === 'user'"
               [class.assistant]="message.role === 'assistant'">
            <div class="message-avatar">
              {{ message.role === 'user' ? '👤' : '🤖' }}
            </div>
            <div class="message-content">
              <div class="message-text">{{ message.content }}</div>
              <div class="message-meta">
                <span class="timestamp">{{ formatTime(message.timestamp) }}</span>
                <span class="model" *ngIf="message.model">{{ message.model }}</span>
              </div>
            </div>
          </div>

          <!-- Typing Indicator -->
          <div class="message assistant typing" *ngIf="isGenerating()">
            <div class="message-avatar">🤖</div>
            <div class="message-content">
              <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        </div>

        <!-- Input Area -->
        <div class="input-area">
          <div class="input-container">
            <textarea 
              [(ngModel)]="currentMessage" 
              placeholder="Type your message..."
              (keydown)="handleKeyDown($event)"
              [disabled]="isGenerating()"
              rows="2"
              class="message-input"></textarea>
            <button 
              class="send-btn" 
              (click)="sendMessage()" 
              [disabled]="!currentMessage.trim() || isGenerating()">
              <span *ngIf="!isGenerating()">Send</span>
              <span *ngIf="isGenerating()">⏸️</span>
            </button>
          </div>
          <div class="input-options">
            <div class="option-group toggle-group">
              <label>
                <input type="checkbox" 
                       [checked]="useMCP()" 
                       (change)="useMCP.set($any($event.target).checked)">
                Use MCP Server
              </label>
              <label *ngIf="useMCP()" style="margin-left: 10px;">
                <input type="checkbox" 
                       [checked]="useBedrock()" 
                       (change)="useBedrock.set($any($event.target).checked)">
                Enhance with Bedrock
              </label>
              <label style="margin-left: 10px;">
                <input type="checkbox" 
                       [checked]="autoDashboardGeneration()" 
                       (change)="autoDashboardGeneration.set($any($event.target).checked)">
                📊 Auto-generate Dashboards
              </label>
            </div>
            <div class="option-group" *ngIf="!useMCP()">
              <label>Temperature: {{ temperature }}</label>
              <input type="range" 
                     [(ngModel)]="temperature" 
                     min="0" 
                     max="1" 
                     step="0.1"
                     class="slider">
            </div>
            <div class="option-group" *ngIf="!useMCP()">
              <label>Max Tokens: {{ maxTokens }}</label>
              <input type="range" 
                     [(ngModel)]="maxTokens" 
                     min="100" 
                     max="4000" 
                     step="100"
                     class="slider">
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styleUrls: ['./chatbot.component.scss']
})
export class ChatbotComponent implements OnInit, AfterViewChecked {
  @ViewChild('messagesContainer') messagesContainer!: ElementRef;
  @Input() openChatbotSignal: ReturnType<typeof signal<boolean>> = signal(false);
  @Input() dashboardService?: DashboardService;

  isOpen = signal(false);
  messages = signal<ChatMessage[]>([]);
  currentMessage = '';
  sessionId: string | null = null;
  isGenerating = signal(false);
  bedrockConnected = signal(false);
  temperature = 0.7;
  maxTokens = 1000;
  useMCP = signal(true);  // Default to using MCP servers
  useBedrock = signal(false);  // Option to enhance with Bedrock
  selectedMCPServer = signal<string | null>(null);  // null = auto-select
  autoDashboardGeneration = signal(true);  // Auto-generate dashboards from query results

  private apiUrl = 'http://localhost:8000/api';

  constructor(private http: HttpClient) {
    // Watch for changes to the input signal
    effect(() => {
      const shouldOpen = this.openChatbotSignal();
      if (shouldOpen) {
        this.openChatbot();
      }
    });
  }

  ngOnInit() {
    // Check Bedrock connection status
    this.checkBedrockConnection();
  }

  ngAfterViewChecked() {
    this.scrollToBottom();
  }

  openChatbot() {
    console.log('openChatbot called, current isOpen:', this.isOpen());
    this.isOpen.set(true);
    console.log('isOpen set to:', this.isOpen());
    if (!this.sessionId) {
      this.startSession();
    }
  }

  closeChatbot() {
    this.isOpen.set(false);
  }

  async startSession() {
    try {
      const response = await firstValueFrom(this.http.post<ChatbotSession>(`${this.apiUrl}/chatbot/start`, {}));
      if (response) {
        this.sessionId = response.session_id;
        this.messages.set(response.messages || []);
      }
    } catch (error) {
      console.error('Error starting session:', error);
    }
  }

  async sendMessage() {
    if (!this.currentMessage.trim() || this.isGenerating()) {
      return;
    }

    const userMessage: ChatMessage = {
      role: 'user',
      content: this.currentMessage,
      timestamp: new Date().toISOString()
    };

    // Add user message to UI immediately
    this.messages.update(msgs => [...msgs, userMessage]);
    const messageToSend = this.currentMessage;
    this.currentMessage = '';
    this.isGenerating.set(true);

    try {
      let response: any;
      
      // Use MCP endpoint if enabled, otherwise use regular Bedrock endpoint
      if (this.useMCP()) {
        response = await firstValueFrom(this.http.post<any>(`${this.apiUrl}/chatbot/mcp-message`, {
          message: messageToSend,
          session_id: this.sessionId,
          mcp_server_id: this.selectedMCPServer(),
          use_bedrock: this.useBedrock()
        }));
      } else {
        response = await firstValueFrom(this.http.post<any>(`${this.apiUrl}/chatbot/message`, {
          message: messageToSend,
          session_id: this.sessionId,
          temperature: this.temperature,
          max_tokens: this.maxTokens
        }));
      }

      if (response) {
        this.sessionId = response.session_id;
        this.bedrockConnected.set(response.bedrock_connected || response.bedrock_enhanced || false);
        
        if (response.ai_message) {
          this.messages.update(msgs => [...msgs, response.ai_message]);
        }
        
        // Log MCP server info if available
        if (response.mcp_server) {
          console.log(`Message processed via MCP server: ${response.mcp_server}`);
        }

        // Try to generate dashboard if response contains query result data
        this.tryGenerateDashboard(response);
      }
    } catch (error: any) {
      console.error('Error sending message:', error);
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: `Sorry, I encountered an error: ${error.error?.detail || error.message || 'Unknown error'}. Please try again.`,
        timestamp: new Date().toISOString()
      };
      this.messages.update(msgs => [...msgs, errorMessage]);
    } finally {
      this.isGenerating.set(false);
    }
  }

  handleKeyDown(event: Event) {
    const keyboardEvent = event as KeyboardEvent;
    if (keyboardEvent.key === 'Enter' && !keyboardEvent.shiftKey) {
      keyboardEvent.preventDefault();
      this.sendMessage();
    }
  }

  formatTime(timestamp: string): string {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  scrollToBottom() {
    if (this.messagesContainer) {
      const element = this.messagesContainer.nativeElement;
      element.scrollTop = element.scrollHeight;
    }
  }

  async checkBedrockConnection() {
    try {
      const response = await firstValueFrom(this.http.get<any>(`${this.apiUrl}/health`));
      if (response && response.services) {
        this.bedrockConnected.set(response.services.bedrock || false);
      }
    } catch (error) {
      console.error('Error checking Bedrock connection:', error);
    }
  }

  /**
   * Try to generate a dashboard widget from API response
   */
  private tryGenerateDashboard(response: any) {
    // Check if auto-generation is enabled and dashboard service is available
    if (!this.autoDashboardGeneration() || !this.dashboardService) {
      return;
    }

    // Check if response contains query result data
    if (this.isQueryResult(response)) {
      const queryResult = this.extractQueryResult(response);
      
      if (queryResult) {
        const widget = this.dashboardService.generateWidgetFromQueryResult(queryResult);
        
        if (widget) {
          this.dashboardService.addWidget(widget);
          console.log('Generated dashboard widget:', widget);
          
          // Add a system message to notify user
          const notificationMessage: ChatMessage = {
            role: 'assistant',
            content: '📊 Dashboard widget generated! Check the dashboard page to view your visualization.',
            timestamp: new Date().toISOString(),
            model: 'system'
          };
          this.messages.update(msgs => [...msgs, notificationMessage]);
        }
      }
    }
  }

  /**
   * Check if response is a query result
   */
  private isQueryResult(response: any): boolean {
    return response && 
           typeof response === 'object' && 
           'raw_data' in response &&
           response.raw_data &&
           'columns' in response.raw_data &&
           'rows' in response.raw_data &&
           Array.isArray(response.raw_data.columns) &&
           Array.isArray(response.raw_data.rows);
  }

  /**
   * Extract query result from various response formats
   */
  private extractQueryResult(response: any): QueryResult | null {
    try {
      // Direct query result
      if (this.isQueryResult(response)) {
        return {
          success: response.success !== false,
          prompt: response.prompt || response.query || 'Query Result',
          analysis: response.analysis || {},
          service: response.service || 'unknown',
          action: response.action || 'query',
          result: response.result,
          raw_data: response.raw_data,
          answer: response.answer || response.ai_message?.content || '',
          llm_intent: response.llm_intent,
          sql: response.sql,
          explanation: response.explanation,
          row_count: response.row_count || response.raw_data.rows.length,
          data_source_id: response.data_source_id,
          error: response.error,
          timestamp: response.timestamp || new Date().toISOString()
        };
      }

      // Check if response contains query_result field
      if (response.query_result && this.isQueryResult(response.query_result)) {
        return this.extractQueryResult(response.query_result);
      }

      // Check if response contains data field
      if (response.data && this.isQueryResult(response.data)) {
        return this.extractQueryResult(response.data);
      }

      return null;
    } catch (error) {
      console.error('Error extracting query result:', error);
      return null;
    }
  }
}

