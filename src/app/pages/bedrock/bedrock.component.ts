import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

interface BedrockModel {
  id: string;
  name: string;
  provider: 'anthropic' | 'amazon' | 'ai21' | 'cohere' | 'meta' | 'stability';
  type: 'text' | 'image' | 'embedding' | 'multimodal';
  status: 'available' | 'unavailable' | 'limited';
  pricing: {
    input: number;
    output: number;
    unit: string;
  };
  description: string;
  capabilities: string[];
  contextWindow: number;
}

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  model?: string;
  tokenCount?: number;
}

interface BedrockConnection {
  region: string;
  accessKeyId: string;
  secretAccessKey: string;
  sessionToken?: string;
  connected: boolean;
}

@Component({
  selector: 'app-bedrock',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="bedrock-container">
      <!-- Header Section -->
      <div class="bedrock-header">
        <div class="header-content">
          <div class="aws-logo">☁️</div>
          <div class="header-text">
            <h1>Amazon Bedrock Integration</h1>
            <p>Access powerful foundation models through AWS Bedrock</p>
          </div>
        </div>
        <div class="connection-status" [class]="connectionStatus()">
          <div class="status-indicator"></div>
          <span>{{ getConnectionStatusText() }}</span>
        </div>
      </div>

      <!-- Connection Configuration -->
      <div class="config-section" *ngIf="!bedrockConnection().connected">
        <div class="config-card">
          <h2>Configure AWS Bedrock Connection</h2>
          <form class="connection-form" (ngSubmit)="connectToBedrock()">
            <div class="form-row">
              <div class="form-group">
                <label for="region">AWS Region</label>
                <select id="region" [(ngModel)]="connectionConfig.region" name="region" required>
                  <option value="us-east-1">US East (N. Virginia)</option>
                  <option value="us-west-2">US West (Oregon)</option>
                  <option value="eu-west-1">Europe (Ireland)</option>
                  <option value="ap-southeast-1">Asia Pacific (Singapore)</option>
                </select>
              </div>
              <div class="form-group">
                <label for="accessKeyId">Access Key ID</label>
                <input type="text" 
                       id="accessKeyId" 
                       [(ngModel)]="connectionConfig.accessKeyId" 
                       name="accessKeyId"
                       placeholder="AKIAIOSFODNN7EXAMPLE"
                       required>
              </div>
            </div>
            
            <div class="form-group">
              <label for="secretAccessKey">Secret Access Key</label>
              <input type="password" 
                     id="secretAccessKey" 
                     [(ngModel)]="connectionConfig.secretAccessKey" 
                     name="secretAccessKey"
                     placeholder="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
                     required>
            </div>
            
            <div class="form-group">
              <label for="sessionToken">Session Token (Optional)</label>
              <input type="password" 
                     id="sessionToken" 
                     [(ngModel)]="connectionConfig.sessionToken" 
                     name="sessionToken"
                     placeholder="For temporary credentials">
            </div>
            
            <button type="submit" class="connect-btn" [disabled]="connecting()">
              {{ connecting() ? 'Connecting...' : 'Connect to Bedrock' }}
            </button>
          </form>
        </div>
      </div>

      <!-- Main Bedrock Interface -->
      <div class="bedrock-interface" *ngIf="bedrockConnection().connected">
        
        <!-- Models Section -->
        <div class="models-section">
          <div class="section-header">
            <h2>Available Models</h2>
            <div class="model-filters">
              <button class="filter-btn" 
                      [class.active]="selectedProvider === ''"
                      (click)="selectedProvider = ''">All</button>
              <button class="filter-btn" 
                      [class.active]="selectedProvider === 'anthropic'"
                      (click)="selectedProvider = 'anthropic'">Anthropic</button>
              <button class="filter-btn" 
                      [class.active]="selectedProvider === 'amazon'"
                      (click)="selectedProvider = 'amazon'">Amazon</button>
              <button class="filter-btn" 
                      [class.active]="selectedProvider === 'ai21'"
                      (click)="selectedProvider = 'ai21'">AI21</button>
            </div>
          </div>

          <div class="models-grid">
            <div class="model-card" 
                 *ngFor="let model of getFilteredModels()" 
                 [class.selected]="selectedModel()?.id === model.id"
                 (click)="selectModel(model)">
              <div class="model-header">
                <div class="model-provider" [class]="model.provider">
                  {{ getProviderIcon(model.provider) }}
                </div>
                <div class="model-info">
                  <h3>{{ model.name }}</h3>
                  <p>{{ model.description }}</p>
                </div>
                <div class="model-status" [class]="model.status">
                  {{ model.status }}
                </div>
              </div>
              
              <div class="model-details">
                <div class="model-specs">
                  <span class="spec">{{ model.type }}</span>
                  <span class="spec">{{ formatContextWindow(model.contextWindow) }} context</span>
                </div>
                
                <div class="model-pricing">
                  <span class="price">$\{{ model.pricing.input }}/{{ model.pricing.unit }} input</span>
                  <span class="price">$\{{ model.pricing.output }}/{{ model.pricing.unit }} output</span>
                </div>
              </div>

              <div class="model-capabilities">
                <span class="capability" *ngFor="let cap of model.capabilities.slice(0, 3)">
                  {{ cap }}
                </span>
                <span class="capability more" *ngIf="model.capabilities.length > 3">
                  +{{ model.capabilities.length - 3 }} more
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Chat Interface -->
        <div class="chat-section" *ngIf="selectedModel()">
          <div class="chat-header">
            <h2>Chat with {{ selectedModel()?.name }}</h2>
            <div class="chat-controls">
              <button class="clear-btn" (click)="clearChat()">Clear Chat</button>
              <div class="token-counter">
                Tokens: {{ totalTokens() }}
              </div>
            </div>
          </div>

          <div class="chat-container">
            <div class="messages-list" #messagesList>
              <div class="message" 
                   *ngFor="let message of chatMessages()" 
                   [class]="message.role">
                <div class="message-avatar">
                  {{ message.role === 'user' ? '👤' : '🤖' }}
                </div>
                <div class="message-content">
                  <div class="message-text">{{ message.content }}</div>
                  <div class="message-meta">
                    <span class="timestamp">{{ formatTime(message.timestamp) }}</span>
                    <span class="tokens" *ngIf="message.tokenCount">{{ message.tokenCount }} tokens</span>
                  </div>
                </div>
              </div>
              
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

            <div class="chat-input">
              <div class="input-container">
                <textarea [(ngModel)]="currentMessage" 
                          placeholder="Type your message to {{ selectedModel()?.name }}..."
                          (keydown.enter)="sendMessage($event)"
                          [disabled]="isGenerating()"
                          rows="3"></textarea>
                <button class="send-btn" 
                        (click)="sendMessage()" 
                        [disabled]="!currentMessage.trim() || isGenerating()">
                  <span *ngIf="!isGenerating()">Send</span>
                  <span *ngIf="isGenerating()">⏸️</span>
                </button>
              </div>
              
              <div class="input-options">
                <div class="model-params">
                  <label>Temperature: {{ temperature }}</label>
                  <input type="range" 
                         [(ngModel)]="temperature" 
                         min="0" 
                         max="1" 
                         step="0.1"
                         class="temp-slider">
                </div>
                <div class="model-params">
                  <label>Max Tokens: {{ maxTokens }}</label>
                  <input type="range" 
                         [(ngModel)]="maxTokens" 
                         min="100" 
                         max="4000" 
                         step="100"
                         class="token-slider">
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Usage Analytics -->
        <div class="analytics-section">
          <div class="analytics-header">
            <h2>Usage Analytics</h2>
            <select [(ngModel)]="analyticsTimeframe">
              <option value="today">Today</option>
              <option value="week">This Week</option>
              <option value="month">This Month</option>
            </select>
          </div>

          <div class="analytics-grid">
            <div class="analytics-card">
              <h3>Total Requests</h3>
              <div class="metric-value">{{ usageStats().totalRequests }}</div>
              <div class="metric-change positive">+12% from last week</div>
            </div>

            <div class="analytics-card">
              <h3>Tokens Used</h3>
              <div class="metric-value">{{ formatNumber(usageStats().totalTokens) }}</div>
              <div class="metric-change positive">+8% from last week</div>
            </div>

            <div class="analytics-card">
              <h3>Estimated Cost</h3>
              <div class="metric-value">\${{ usageStats().estimatedCost.toFixed(2) }}</div>
              <div class="metric-change neutral">Same as last week</div>
            </div>

            <div class="analytics-card">
              <h3>Avg Response Time</h3>
              <div class="metric-value">{{ usageStats().avgResponseTime }}ms</div>
              <div class="metric-change positive">-5% from last week</div>
            </div>
          </div>

          <div class="usage-chart">
            <h3>Request Volume</h3>
            <div class="chart-placeholder">
              <div class="chart-bars">
                <div class="bar" style="height: 60%"></div>
                <div class="bar" style="height: 80%"></div>
                <div class="bar" style="height: 45%"></div>
                <div class="bar" style="height: 90%"></div>
                <div class="bar" style="height: 70%"></div>
                <div class="bar" style="height: 85%"></div>
                <div class="bar" style="height: 95%"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styleUrls: ['./bedrock.component.scss']
})
export class BedrockComponent implements OnInit {
  
  bedrockConnection = signal<BedrockConnection>({
    region: 'us-east-1',
    accessKeyId: '',
    secretAccessKey: '',
    sessionToken: '',
    connected: false
  });

  connectionConfig = {
    region: 'us-east-1',
    accessKeyId: '',
    secretAccessKey: '',
    sessionToken: ''
  };

  connecting = signal(false);
  connectionStatus = signal<'connected' | 'disconnected' | 'error'>('disconnected');

  // UI state - using regular properties for ngModel compatibility  
  selectedProvider = '';
  selectedModel = signal<BedrockModel | null>(null);

  chatMessages = signal<ChatMessage[]>([]);
  currentMessage = '';
  isGenerating = signal(false);
  totalTokens = signal(0);

  temperature = 0.7;
  maxTokens = 1000;
  analyticsTimeframe = 'week';

  availableModels: BedrockModel[] = [
    {
      id: 'anthropic.claude-3-sonnet-20240229-v1:0',
      name: 'Claude 3 Sonnet',
      provider: 'anthropic',
      type: 'text',
      status: 'available',
      pricing: { input: 3.00, output: 15.00, unit: '1K tokens' },
      description: 'Balanced performance for a wide range of tasks',
      capabilities: ['Text Generation', 'Analysis', 'Code', 'Math', 'Reasoning'],
      contextWindow: 200000
    },
    {
      id: 'anthropic.claude-3-haiku-20240307-v1:0',
      name: 'Claude 3 Haiku',
      provider: 'anthropic',
      type: 'text',
      status: 'available',
      pricing: { input: 0.25, output: 1.25, unit: '1K tokens' },
      description: 'Fast and cost-effective for simple tasks',
      capabilities: ['Text Generation', 'Summarization', 'Q&A'],
      contextWindow: 200000
    },
    {
      id: 'amazon.nova-pro-v1:0',
      name: 'Amazon Nova Pro',
      provider: 'amazon',
      type: 'multimodal',
      status: 'available',
      pricing: { input: 0.80, output: 3.20, unit: '1K tokens' },
      description: 'Multimodal model for text and image understanding',
      capabilities: ['Text Generation', 'Image Analysis', 'Multimodal'],
      contextWindow: 300000
    },
    {
      id: 'ai21.jamba-instruct-v1:0',
      name: 'Jamba Instruct',
      provider: 'ai21',
      type: 'text',
      status: 'available',
      pricing: { input: 0.50, output: 0.70, unit: '1K tokens' },
      description: 'Instruction-following model with long context',
      capabilities: ['Instruction Following', 'Long Context', 'Reasoning'],
      contextWindow: 256000
    }
  ];

  usageStats = signal({
    totalRequests: 247,
    totalTokens: 125430,
    estimatedCost: 18.45,
    avgResponseTime: 1240
  });

  ngOnInit() {
    // Check if there's a stored connection
    this.checkStoredConnection();
  }

  checkStoredConnection() {
    if (typeof window !== 'undefined' && window.localStorage) {
      const storedConnection = localStorage.getItem('bedrockConnection');
      if (storedConnection) {
        try {
          const connection = JSON.parse(storedConnection);
          this.bedrockConnection.set(connection);
          this.connectionStatus.set(connection.connected ? 'connected' : 'disconnected');
        } catch (error) {
          console.error('Error parsing stored connection:', error);
        }
      }
    }
  }

  async connectToBedrock() {
    this.connecting.set(true);
    
    try {
      // Simulate connection process
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const connection: BedrockConnection = {
        ...this.connectionConfig,
        connected: true
      };
      
      this.bedrockConnection.set(connection);
      this.connectionStatus.set('connected');
      
      // Store connection (without sensitive data in real implementation)
      if (typeof window !== 'undefined' && window.localStorage) {
        localStorage.setItem('bedrockConnection', JSON.stringify(connection));
      }
      
    } catch (error) {
      console.error('Connection failed:', error);
      this.connectionStatus.set('error');
    } finally {
      this.connecting.set(false);
    }
  }

  getConnectionStatusText(): string {
    switch (this.connectionStatus()) {
      case 'connected': return 'Connected to AWS Bedrock';
      case 'disconnected': return 'Not Connected';
      case 'error': return 'Connection Error';
      default: return 'Unknown Status';
    }
  }

  getFilteredModels(): BedrockModel[] {
    if (!this.selectedProvider) {
      return this.availableModels;
    }
    return this.availableModels.filter(model => model.provider === this.selectedProvider);
  }

  selectModel(model: BedrockModel) {
    this.selectedModel.set(model);
    this.chatMessages.set([]);
    this.totalTokens.set(0);
  }

  getProviderIcon(provider: string): string {
    const icons = {
      anthropic: '🧠',
      amazon: '📦',
      ai21: '🔬',
      cohere: '🌐',
      meta: '🦙',
      stability: '🎨'
    };
    return icons[provider as keyof typeof icons] || '🤖';
  }

  formatContextWindow(tokens: number): string {
    if (tokens >= 1000000) {
      return `${(tokens / 1000000).toFixed(1)}M`;
    }
    if (tokens >= 1000) {
      return `${(tokens / 1000).toFixed(0)}K`;
    }
    return tokens.toString();
  }

  async sendMessage(event?: Event) {
    if (event) {
      event.preventDefault();
    }
    
    if (!this.currentMessage.trim() || this.isGenerating()) {
      return;
    }

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: this.currentMessage,
      timestamp: new Date(),
      model: this.selectedModel()?.id,
      tokenCount: this.estimateTokens(this.currentMessage)
    };

    this.chatMessages.update(messages => [...messages, userMessage]);
    this.totalTokens.update(total => total + (userMessage.tokenCount || 0));
    
    const messageContent = this.currentMessage;
    this.currentMessage = '';
    this.isGenerating.set(true);

    try {
      // Simulate API call to Bedrock
      await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000));
      
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: this.generateMockResponse(messageContent),
        timestamp: new Date(),
        model: this.selectedModel()?.id,
        tokenCount: Math.floor(Math.random() * 200) + 50
      };

      this.chatMessages.update(messages => [...messages, assistantMessage]);
      this.totalTokens.update(total => total + (assistantMessage.tokenCount || 0));
      
    } catch (error) {
      console.error('Error generating response:', error);
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error while processing your request. Please try again.',
        timestamp: new Date(),
        model: this.selectedModel()?.id
      };
      this.chatMessages.update(messages => [...messages, errorMessage]);
    } finally {
      this.isGenerating.set(false);
    }
  }

  generateMockResponse(input: string): string {
    const responses = [
      `I understand you're asking about "${input}". This is a sophisticated question that requires careful analysis. Based on the context and my training, I can provide several insights...`,
      `Great question! When considering "${input}", there are multiple factors to take into account. Let me break this down for you...`,
      `Thank you for your query about "${input}". This topic involves several interconnected concepts that I'd be happy to explore with you...`,
      `I'd be happy to help with "${input}". This is an interesting area that combines various aspects of the subject matter...`
    ];
    return responses[Math.floor(Math.random() * responses.length)];
  }

  estimateTokens(text: string): number {
    // Rough estimation: ~4 characters per token
    return Math.ceil(text.length / 4);
  }

  formatTime(timestamp: Date): string {
    return timestamp.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  }

  formatNumber(num: number): string {
    if (num >= 1000000) {
      return `${(num / 1000000).toFixed(1)}M`;
    }
    if (num >= 1000) {
      return `${(num / 1000).toFixed(1)}K`;
    }
    return num.toString();
  }

  clearChat() {
    this.chatMessages.set([]);
    this.totalTokens.set(0);
  }
}
