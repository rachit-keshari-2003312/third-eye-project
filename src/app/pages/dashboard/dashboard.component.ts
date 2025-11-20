import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

interface DashboardStats {
  totalAgents: number;
  activeConversations: number;
  mcpConnections: number;
  bedrockRequests: number;
}

interface RecentActivity {
  id: string;
  type: 'agent' | 'conversation' | 'integration' | 'bedrock';
  title: string;
  description: string;
  timestamp: Date;
  status: 'success' | 'pending' | 'error';
}

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="dashboard-container">
      <!-- Welcome Header -->
      <div class="welcome-section">
        <div class="welcome-content">
          <h1>Welcome to Third-Eye</h1>
          <p>Your Agentic AI Platform Dashboard</p>
          <div class="quick-actions">
            <button class="action-btn primary" (click)="createNewAgent()">
              <i class="icon">🤖</i>
              New AI Agent
            </button>
            <button class="action-btn secondary" (click)="startConversation()">
              <i class="icon">💬</i>
              Start Chat
            </button>
            <button class="action-btn tertiary" (click)="connectMCP()">
              <i class="icon">🔗</i>
              Connect MCP
            </button>
          </div>
        </div>
        <div class="welcome-visual">
          <div class="floating-eye">👁️</div>
          <div class="data-orbs">
            <div class="orb orb-1"></div>
            <div class="orb orb-2"></div>
            <div class="orb orb-3"></div>
          </div>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="stats-grid">
        <div class="stat-card" *ngFor="let stat of statsCards">
          <div class="stat-icon" [style.background]="stat.gradient">
            <span>{{ stat.icon }}</span>
          </div>
          <div class="stat-content">
            <h3>{{ stat.value }}</h3>
            <p>{{ stat.label }}</p>
            <span class="stat-change" [class]="stat.changeType">
              {{ stat.change }}
            </span>
          </div>
        </div>
      </div>

      <!-- Main Dashboard Grid -->
      <div class="dashboard-grid">
        <!-- AI Agents Overview -->
        <div class="dashboard-card agents-overview">
          <div class="card-header">
            <h3>AI Agents</h3>
            <button class="view-all-btn">View All</button>
          </div>
          <div class="agents-list">
            <div class="agent-item" *ngFor="let agent of recentAgents">
              <div class="agent-avatar">{{ agent.name.charAt(0) }}</div>
              <div class="agent-info">
                <h4>{{ agent.name }}</h4>
                <p>{{ agent.description }}</p>
                <span class="agent-status" [class]="agent.status">{{ agent.status }}</span>
              </div>
              <div class="agent-actions">
                <button class="action-btn-small">▶️</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Recent Activity -->
        <div class="dashboard-card activity-feed">
          <div class="card-header">
            <h3>Recent Activity</h3>
            <div class="activity-filters">
              <button class="filter-btn active">All</button>
              <button class="filter-btn">Agents</button>
              <button class="filter-btn">MCP</button>
            </div>
          </div>
          <div class="activity-list">
            <div class="activity-item" *ngFor="let activity of recentActivity()">
              <div class="activity-icon" [class]="activity.type">
                {{ getActivityIcon(activity.type) }}
              </div>
              <div class="activity-content">
                <h4>{{ activity.title }}</h4>
                <p>{{ activity.description }}</p>
                <span class="activity-time">{{ getRelativeTime(activity.timestamp) }}</span>
              </div>
              <div class="activity-status" [class]="activity.status">
                {{ activity.status }}
              </div>
            </div>
          </div>
        </div>

        <!-- MCP Connections -->
        <div class="dashboard-card mcp-connections">
          <div class="card-header">
            <h3>MCP Connections</h3>
            <button class="add-btn">+ Add</button>
          </div>
          <div class="connections-grid">
            <div class="connection-item" *ngFor="let connection of mcpConnections">
              <div class="connection-status" [class]="connection.status"></div>
              <div class="connection-info">
                <h4>{{ connection.name }}</h4>
                <p>{{ connection.type }}</p>
              </div>
              <div class="connection-metrics">
                <span class="metric">{{ connection.requests }} req/min</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Performance Chart -->
        <div class="dashboard-card performance-chart">
          <div class="card-header">
            <h3>Performance Metrics</h3>
            <select class="time-selector">
              <option>Last 24h</option>
              <option>Last 7d</option>
              <option>Last 30d</option>
            </select>
          </div>
          <div class="chart-container">
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
              <div class="chart-labels">
                <span>Mon</span>
                <span>Tue</span>
                <span>Wed</span>
                <span>Thu</span>
                <span>Fri</span>
                <span>Sat</span>
                <span>Sun</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- System Status -->
      <div class="system-status">
        <div class="status-header">
          <h3>System Status</h3>
          <div class="overall-status healthy">
            <div class="status-indicator"></div>
            All Systems Operational
          </div>
        </div>
        <div class="status-grid">
          <div class="status-item" *ngFor="let service of systemServices">
            <div class="service-info">
              <span class="service-name">{{ service.name }}</span>
              <span class="service-uptime">{{ service.uptime }}% uptime</span>
            </div>
            <div class="service-status" [class]="service.status">
              {{ service.status }}
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {
  
  dashboardStats = signal<DashboardStats>({
    totalAgents: 12,
    activeConversations: 8,
    mcpConnections: 5,
    bedrockRequests: 247
  });

  statsCards = [
    {
      icon: '🤖',
      label: 'AI Agents',
      value: '12',
      change: '+2 this week',
      changeType: 'positive',
      gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    },
    {
      icon: '💬',
      label: 'Active Chats',
      value: '8',
      change: '+4 today',
      changeType: 'positive',
      gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'
    },
    {
      icon: '🔗',
      label: 'MCP Connections',
      value: '5',
      change: 'All online',
      changeType: 'neutral',
      gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'
    },
    {
      icon: '☁️',
      label: 'Bedrock Requests',
      value: '247',
      change: '+15% from last week',
      changeType: 'positive',
      gradient: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)'
    }
  ];

  recentAgents = [
    {
      name: 'Data Analyst',
      description: 'Analyzes tabular data and generates insights',
      status: 'active',
      lastUsed: new Date()
    },
    {
      name: 'Code Assistant',
      description: 'Helps with code generation and debugging',
      status: 'active',
      lastUsed: new Date()
    },
    {
      name: 'Report Generator',
      description: 'Creates comprehensive reports from data',
      status: 'idle',
      lastUsed: new Date()
    }
  ];

  recentActivity = signal<RecentActivity[]>([
    {
      id: '1',
      type: 'agent',
      title: 'New agent created',
      description: 'Data Analyst agent was successfully created',
      timestamp: new Date(Date.now() - 1000 * 60 * 15),
      status: 'success'
    },
    {
      id: '2',
      type: 'bedrock',
      title: 'Bedrock model invoked',
      description: 'Claude-3 model processed 45 requests',
      timestamp: new Date(Date.now() - 1000 * 60 * 30),
      status: 'success'
    },
    {
      id: '3',
      type: 'integration',
      title: 'MCP server connected',
      description: 'Filesystem MCP server is now online',
      timestamp: new Date(Date.now() - 1000 * 60 * 60),
      status: 'success'
    }
  ]);

  mcpConnections = [
    { name: 'Filesystem', type: 'File Operations', status: 'connected', requests: 12 },
    { name: 'Database', type: 'SQL Operations', status: 'connected', requests: 8 },
    { name: 'Web Scraper', type: 'Data Collection', status: 'connected', requests: 5 },
    { name: 'Git', type: 'Version Control', status: 'idle', requests: 2 },
    { name: 'Slack', type: 'Communication', status: 'connected', requests: 15 }
  ];

  systemServices = [
    { name: 'API Gateway', status: 'healthy', uptime: 99.9 },
    { name: 'MCP Router', status: 'healthy', uptime: 98.7 },
    { name: 'Bedrock Connector', status: 'healthy', uptime: 99.5 },
    { name: 'Database', status: 'healthy', uptime: 100.0 },
    { name: 'Authentication', status: 'healthy', uptime: 99.8 }
  ];

  ngOnInit() {
    // Initialize dashboard data
    this.loadDashboardData();
  }

  loadDashboardData() {
    // Simulate loading dashboard data
    console.log('Loading dashboard data...');
  }

  createNewAgent() {
    console.log('Creating new agent...');
    // Navigate to agents page or open modal
  }

  startConversation() {
    console.log('Starting new conversation...');
    // Navigate to conversations page
  }

  connectMCP() {
    console.log('Connecting MCP server...');
    // Navigate to integrations page
  }

  getActivityIcon(type: string): string {
    const icons = {
      agent: '🤖',
      conversation: '💬',
      integration: '🔗',
      bedrock: '☁️'
    };
    return icons[type as keyof typeof icons] || '📋';
  }

  getRelativeTime(timestamp: Date): string {
    const now = new Date();
    const diff = now.getTime() - timestamp.getTime();
    const minutes = Math.floor(diff / (1000 * 60));
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    return `${days}d ago`;
  }
}
