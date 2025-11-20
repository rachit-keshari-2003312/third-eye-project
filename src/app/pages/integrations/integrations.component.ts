import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

interface MCPServer {
  id: string;
  name: string;
  description: string;
  type: 'filesystem' | 'database' | 'web' | 'api' | 'git' | 'communication' | 'custom';
  status: 'connected' | 'disconnected' | 'error' | 'configuring';
  endpoint: string;
  capabilities: string[];
  lastUsed: Date;
  requestCount: number;
  config: Record<string, any>;
  isBuiltIn: boolean;
}

@Component({
  selector: 'app-integrations',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="integrations-container">
      <!-- Header -->
      <div class="integrations-header">
        <div class="header-content">
          <h1>MCP Server Integrations</h1>
          <p>Connect and manage Model Context Protocol servers for enhanced AI capabilities</p>
          <div class="beta-badge">Beta</div>
        </div>
        <button class="add-integration-btn" (click)="showAddModal.set(true)">
          <i class="icon">🔗</i>
          Add Integration
        </button>
      </div>

      <!-- Quick Stats -->
      <div class="stats-row">
        <div class="stat-card">
          <div class="stat-icon">🔗</div>
          <div class="stat-info">
            <h3>{{ getConnectedCount() }}</h3>
            <p>Connected Servers</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">📊</div>
          <div class="stat-info">
            <h3>{{ getTotalRequests() }}</h3>
            <p>Total Requests</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">⚡</div>
          <div class="stat-info">
            <h3>{{ getActiveCapabilities() }}</h3>
            <p>Active Capabilities</p>
          </div>
        </div>
      </div>

      <!-- Filters -->
      <div class="filters-section">
        <div class="search-filter">
          <input type="text" 
                 placeholder="Search integrations..." 
                 [(ngModel)]="searchQuery"
                 (ngModelChange)="filterServers()">
        </div>
        <div class="status-filters">
          <button class="filter-btn" 
                  [class.active]="selectedStatus() === ''"
                  (click)="setStatusFilter('')">All</button>
          <button class="filter-btn" 
                  [class.active]="selectedStatus() === 'connected'"
                  (click)="setStatusFilter('connected')">Connected</button>
          <button class="filter-btn" 
                  [class.active]="selectedStatus() === 'disconnected'"
                  (click)="setStatusFilter('disconnected')">Disconnected</button>
          <button class="filter-btn" 
                  [class.active]="selectedStatus() === 'error'"
                  (click)="setStatusFilter('error')">Error</button>
        </div>
      </div>

      <!-- Built-in Servers -->
      <div class="servers-section">
        <h2>Built-in MCP Servers</h2>
        <div class="servers-grid">
          <div class="server-card builtin" 
               *ngFor="let server of getBuiltInServers()" 
               [class]="server.status">
            <div class="server-header">
              <div class="server-icon" [class]="server.type">
                {{ getServerIcon(server.type) }}
              </div>
              <div class="server-info">
                <h3>{{ server.name }}</h3>
                <p>{{ server.description }}</p>
              </div>
              <div class="server-status" [class]="server.status">
                <div class="status-dot"></div>
                {{ server.status }}
              </div>
            </div>

            <div class="server-capabilities">
              <span class="capability" *ngFor="let cap of server.capabilities.slice(0, 3)">
                {{ cap }}
              </span>
              <span class="more-capabilities" *ngIf="server.capabilities.length > 3">
                +{{ server.capabilities.length - 3 }} more
              </span>
            </div>

            <div class="server-metrics">
              <div class="metric">
                <span class="metric-value">{{ server.requestCount }}</span>
                <span class="metric-label">Requests</span>
              </div>
              <div class="metric">
                <span class="metric-value">{{ getRelativeTime(server.lastUsed) }}</span>
                <span class="metric-label">Last Used</span>
              </div>
            </div>

            <div class="server-actions">
              <button class="action-btn" 
                      [class]="server.status === 'connected' ? 'disconnect' : 'connect'"
                      (click)="toggleServerConnection(server)">
                {{ server.status === 'connected' ? 'Disconnect' : 'Connect' }}
              </button>
              <button class="action-btn config" (click)="configureServer(server)">
                Configure
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Custom Servers -->
      <div class="servers-section" *ngIf="getCustomServers().length > 0">
        <h2>Custom MCP Servers</h2>
        <div class="servers-grid">
          <div class="server-card custom" 
               *ngFor="let server of getCustomServers()" 
               [class]="server.status">
            <div class="server-header">
              <div class="server-icon custom">🛠️</div>
              <div class="server-info">
                <h3>{{ server.name }}</h3>
                <p>{{ server.description }}</p>
                <span class="endpoint">{{ server.endpoint }}</span>
              </div>
              <div class="server-actions-inline">
                <button class="action-btn-small edit" (click)="editServer(server)">✏️</button>
                <button class="action-btn-small delete" (click)="deleteServer(server)">🗑️</button>
              </div>
            </div>

            <div class="server-capabilities">
              <span class="capability" *ngFor="let cap of server.capabilities">
                {{ cap }}
              </span>
            </div>

            <div class="server-actions">
              <button class="action-btn" 
                      [class]="server.status === 'connected' ? 'disconnect' : 'connect'"
                      (click)="toggleServerConnection(server)">
                {{ server.status === 'connected' ? 'Disconnect' : 'Connect' }}
              </button>
              <button class="action-btn test" (click)="testConnection(server)">
                Test
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div class="empty-state" *ngIf="filteredServers().length === 0">
        <div class="empty-icon">🔗</div>
        <h3>No integrations found</h3>
        <p>Add your first MCP server integration to extend AI capabilities.</p>
        <button class="add-first-btn" (click)="showAddModal.set(true)">
          Add Your First Integration
        </button>
      </div>
    </div>

    <!-- Add Integration Modal -->
    <div class="modal-overlay" *ngIf="showAddModal" (click)="closeAddModal($event)">
      <div class="add-modal" (click)="$event.stopPropagation()">
        <div class="modal-header">
          <h2>Add MCP Server Integration</h2>
          <button class="close-btn" (click)="showAddModal.set(false)">×</button>
        </div>

        <div class="modal-tabs">
          <button class="tab-btn" 
                  [class.active]="activeTab === 'preset'"
                  (click)="activeTab = 'preset'">Preset Servers</button>
          <button class="tab-btn" 
                  [class.active]="activeTab === 'custom'"
                  (click)="activeTab = 'custom'">Custom Server</button>
        </div>

        <!-- Preset Servers Tab -->
        <div class="tab-content" *ngIf="activeTab === 'preset'">
          <div class="preset-servers">
            <div class="preset-server" 
                 *ngFor="let preset of presetServers"
                 (click)="selectPreset(preset)">
              <div class="preset-icon">{{ getServerIcon(preset.type) }}</div>
              <div class="preset-info">
                <h3>{{ preset.name }}</h3>
                <p>{{ preset.description }}</p>
              </div>
              <div class="preset-capabilities">
                <span *ngFor="let cap of preset.capabilities.slice(0, 2)">{{ cap }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Custom Server Tab -->
        <div class="tab-content" *ngIf="activeTab === 'custom'">
          <form class="custom-server-form" (ngSubmit)="addCustomServer()">
            <div class="form-group">
              <label>Server Name</label>
              <input type="text" [(ngModel)]="newServer.name" name="name" required>
            </div>
            
            <div class="form-group">
              <label>Description</label>
              <textarea [(ngModel)]="newServer.description" name="description" rows="2"></textarea>
            </div>
            
            <div class="form-group">
              <label>Endpoint URL</label>
              <input type="url" [(ngModel)]="newServer.endpoint" name="endpoint" required>
            </div>
            
            <div class="form-group">
              <label>Server Type</label>
              <select [(ngModel)]="newServer.type" name="type">
                <option value="api">API Service</option>
                <option value="database">Database</option>
                <option value="web">Web Service</option>
                <option value="custom">Custom</option>
              </select>
            </div>

            <div class="form-actions">
              <button type="button" class="cancel-btn" (click)="showAddModal.set(false)">Cancel</button>
              <button type="submit" class="add-btn">Add Server</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  `,
  styleUrls: ['./integrations.component.scss']
})
export class IntegrationsComponent implements OnInit {
  
  searchQuery = '';
  selectedStatus = signal('');
  showAddModal = signal(false);
  activeTab = 'preset';

  servers = signal<MCPServer[]>([
    {
      id: '1',
      name: 'Filesystem MCP',
      description: 'Access and manipulate files and directories',
      type: 'filesystem',
      status: 'connected',
      endpoint: 'mcp://filesystem',
      capabilities: ['File Read', 'File Write', 'Directory Listing', 'File Search'],
      lastUsed: new Date(Date.now() - 1000 * 60 * 30),
      requestCount: 145,
      config: {},
      isBuiltIn: true
    },
    {
      id: '2',
      name: 'Database MCP',
      description: 'Execute SQL queries and manage database connections',
      type: 'database',
      status: 'connected',
      endpoint: 'mcp://database',
      capabilities: ['SQL Queries', 'Schema Inspection', 'Data Export'],
      lastUsed: new Date(Date.now() - 1000 * 60 * 60 * 2),
      requestCount: 89,
      config: {},
      isBuiltIn: true
    },
    {
      id: '3',
      name: 'Web Scraper MCP',
      description: 'Scrape and extract data from websites',
      type: 'web',
      status: 'connected',
      endpoint: 'mcp://webscraper',
      capabilities: ['HTML Parsing', 'Data Extraction', 'URL Fetching'],
      lastUsed: new Date(Date.now() - 1000 * 60 * 60 * 4),
      requestCount: 67,
      config: {},
      isBuiltIn: true
    },
    {
      id: '4',
      name: 'Git MCP',
      description: 'Git repository operations and version control',
      type: 'git',
      status: 'disconnected',
      endpoint: 'mcp://git',
      capabilities: ['Repository Cloning', 'Commit History', 'Branch Management'],
      lastUsed: new Date(Date.now() - 1000 * 60 * 60 * 24),
      requestCount: 23,
      config: {},
      isBuiltIn: true
    },
    {
      id: '5',
      name: 'Slack MCP',
      description: 'Send messages and interact with Slack workspaces',
      type: 'communication',
      status: 'error',
      endpoint: 'mcp://slack',
      capabilities: ['Message Sending', 'Channel Management', 'User Lookup'],
      lastUsed: new Date(Date.now() - 1000 * 60 * 60 * 6),
      requestCount: 12,
      config: {},
      isBuiltIn: true
    }
  ]);

  filteredServers = signal<MCPServer[]>([]);

  newServer = {
    name: '',
    description: '',
    endpoint: '',
    type: 'api' as MCPServer['type']
  };

  presetServers = [
    {
      name: 'Weather API',
      description: 'Get weather information and forecasts',
      type: 'api' as const,
      capabilities: ['Current Weather', 'Forecasts', 'Weather Alerts'],
      endpoint: 'https://api.openweathermap.org'
    },
    {
      name: 'Stock Market API',
      description: 'Access real-time stock market data',
      type: 'api' as const,
      capabilities: ['Stock Prices', 'Market Data', 'Financial News'],
      endpoint: 'https://api.polygon.io'
    },
    {
      name: 'Email Service',
      description: 'Send and manage email communications',
      type: 'communication' as const,
      capabilities: ['Send Email', 'Read Inbox', 'Manage Contacts'],
      endpoint: 'smtp://mail.example.com'
    }
  ];

  ngOnInit() {
    this.filteredServers.set(this.servers());
  }

  getConnectedCount(): number {
    return this.servers().filter(s => s.status === 'connected').length;
  }

  getTotalRequests(): number {
    return this.servers().reduce((total, s) => total + s.requestCount, 0);
  }

  getActiveCapabilities(): number {
    return this.servers()
      .filter(s => s.status === 'connected')
      .reduce((total, s) => total + s.capabilities.length, 0);
  }

  getBuiltInServers(): MCPServer[] {
    return this.filteredServers().filter(s => s.isBuiltIn);
  }

  getCustomServers(): MCPServer[] {
    return this.filteredServers().filter(s => !s.isBuiltIn);
  }

  setStatusFilter(status: string) {
    this.selectedStatus.set(status);
    this.filterServers();
  }

  filterServers() {
    let filtered = this.servers();

    if (this.searchQuery) {
      filtered = filtered.filter(s => 
        s.name.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
        s.description.toLowerCase().includes(this.searchQuery.toLowerCase())
      );
    }

    if (this.selectedStatus()) {
      filtered = filtered.filter(s => s.status === this.selectedStatus());
    }

    this.filteredServers.set(filtered);
  }

  getServerIcon(type: string): string {
    const icons = {
      filesystem: '📁',
      database: '🗄️',
      web: '🌐',
      api: '🔌',
      git: '📝',
      communication: '💬',
      custom: '🛠️'
    };
    return icons[type as keyof typeof icons] || '🔗';
  }

  getRelativeTime(date: Date): string {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (hours < 24) return `${hours}h ago`;
    return `${days}d ago`;
  }

  toggleServerConnection(server: MCPServer) {
    const newStatus = server.status === 'connected' ? 'disconnected' : 'connected';
    this.updateServerStatus(server.id, newStatus);
  }

  updateServerStatus(serverId: string, status: MCPServer['status']) {
    this.servers.update(servers => 
      servers.map(s => s.id === serverId ? { ...s, status } : s)
    );
    this.filterServers();
  }

  configureServer(server: MCPServer) {
    console.log('Configuring server:', server.name);
    // Open configuration modal
  }

  editServer(server: MCPServer) {
    console.log('Editing server:', server.name);
    // Open edit modal
  }

  deleteServer(server: MCPServer) {
    if (confirm(`Are you sure you want to delete "${server.name}"?`)) {
      this.servers.update(servers => servers.filter(s => s.id !== server.id));
      this.filterServers();
    }
  }

  testConnection(server: MCPServer) {
    console.log('Testing connection for:', server.name);
    this.updateServerStatus(server.id, 'configuring');
    
    // Simulate test
    setTimeout(() => {
      const success = Math.random() > 0.3;
      this.updateServerStatus(server.id, success ? 'connected' : 'error');
    }, 2000);
  }

  closeAddModal(event: Event) {
    if (event.target === event.currentTarget) {
      this.showAddModal.set(false);
    }
  }

  selectPreset(preset: any) {
    const newServer: MCPServer = {
      id: Date.now().toString(),
      name: preset.name,
      description: preset.description,
      type: preset.type,
      status: 'disconnected',
      endpoint: preset.endpoint,
      capabilities: [...preset.capabilities],
      lastUsed: new Date(),
      requestCount: 0,
      config: {},
      isBuiltIn: false
    };

    this.servers.update(servers => [...servers, newServer]);
    this.filterServers();
    this.showAddModal.set(false);
  }

  addCustomServer() {
    if (!this.newServer.name || !this.newServer.endpoint) return;

    const server: MCPServer = {
      id: Date.now().toString(),
      name: this.newServer.name,
      description: this.newServer.description,
      type: this.newServer.type,
      status: 'disconnected',
      endpoint: this.newServer.endpoint,
      capabilities: ['Custom Capability'],
      lastUsed: new Date(),
      requestCount: 0,
      config: {},
      isBuiltIn: false
    };

    this.servers.update(servers => [...servers, server]);
    this.filterServers();
    
    // Reset form
    this.newServer = {
      name: '',
      description: '',
      endpoint: '',
      type: 'api'
    };
    
    this.showAddModal.set(false);
  }
}
