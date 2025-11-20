import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

interface Agent {
  id: string;
  name: string;
  description: string;
  type: 'data-analyst' | 'code-assistant' | 'content-generator' | 'research' | 'custom';
  status: 'active' | 'idle' | 'training' | 'error';
  capabilities: string[];
  mcpConnections: string[];
  lastUsed: Date;
  totalConversations: number;
  successRate: number;
  created: Date;
}

@Component({
  selector: 'app-agents',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="agents-container">
      <!-- Header Section -->
      <div class="agents-header">
        <div class="header-content">
          <h1>AI Agents</h1>
          <p>Create and manage your custom AI agents with specialized capabilities</p>
        </div>
        <div class="header-actions">
          <button class="create-agent-btn" (click)="showCreateModal.set(true)">
            <i class="icon">🤖</i>
            Create New Agent
          </button>
        </div>
      </div>

      <!-- Filter and Search -->
      <div class="agents-controls">
        <div class="search-section">
          <div class="search-input">
            <i class="search-icon">🔍</i>
            <input type="text" 
                   placeholder="Search agents..." 
                   [(ngModel)]="searchQuery"
                   (ngModelChange)="filterAgents()">
          </div>
        </div>

        <div class="filter-section">
          <div class="filter-group">
            <label>Status:</label>
            <select [(ngModel)]="selectedStatus" (ngModelChange)="filterAgents()">
              <option value="">All</option>
              <option value="active">Active</option>
              <option value="idle">Idle</option>
              <option value="training">Training</option>
              <option value="error">Error</option>
            </select>
          </div>

          <div class="filter-group">
            <label>Type:</label>
            <select [(ngModel)]="selectedType" (ngModelChange)="filterAgents()">
              <option value="">All Types</option>
              <option value="data-analyst">Data Analyst</option>
              <option value="code-assistant">Code Assistant</option>
              <option value="content-generator">Content Generator</option>
              <option value="research">Research</option>
              <option value="custom">Custom</option>
            </select>
          </div>

          <div class="view-toggle">
            <button [class.active]="viewMode === 'grid'" (click)="viewMode = 'grid'">⊞</button>
            <button [class.active]="viewMode === 'list'" (click)="viewMode = 'list'">☰</button>
          </div>
        </div>
      </div>

      <!-- Agents Grid/List -->
      <div class="agents-content" [class]="viewMode + '-view'">
        <div class="agent-card" 
             *ngFor="let agent of filteredAgents()" 
             [class]="agent.status">
          
          <div class="agent-header">
            <div class="agent-avatar">
              <span>{{ getAgentIcon(agent.type) }}</span>
              <div class="status-indicator" [class]="agent.status"></div>
            </div>
            <div class="agent-info">
              <h3>{{ agent.name }}</h3>
              <p>{{ agent.description }}</p>
              <div class="agent-meta">
                <span class="agent-type">{{ formatType(agent.type) }}</span>
                <span class="last-used">Last used {{ getRelativeTime(agent.lastUsed) }}</span>
              </div>
            </div>
            <div class="agent-actions">
              <button class="action-btn primary" (click)="startConversation(agent, $event)">
                <i class="icon">💬</i>
              </button>
              <button class="action-btn secondary" (click)="editAgent(agent, $event)">
                <i class="icon">✏️</i>
              </button>
              <button class="action-btn danger" (click)="deleteAgent(agent, $event)">
                <i class="icon">🗑️</i>
              </button>
            </div>
          </div>

          <div class="agent-capabilities">
            <h4>Capabilities</h4>
            <div class="capability-tags">
              <span class="capability-tag" *ngFor="let capability of agent.capabilities">
                {{ capability }}
              </span>
            </div>
          </div>

          <div class="agent-connections">
            <h4>MCP Connections</h4>
            <div class="connection-list">
              <div class="connection-item" *ngFor="let connection of agent.mcpConnections">
                <div class="connection-status active"></div>
                <span>{{ connection }}</span>
              </div>
            </div>
          </div>

          <div class="agent-stats">
            <div class="stat-item">
              <span class="stat-value">{{ agent.totalConversations }}</span>
              <span class="stat-label">Conversations</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ agent.successRate }}%</span>
              <span class="stat-label">Success Rate</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ getDaysActive(agent.created) }}</span>
              <span class="stat-label">Days Active</span>
            </div>
          </div>

          <div class="agent-footer">
            <button class="deploy-btn" [class.deployed]="agent.status === 'active'" (click)="toggleAgent(agent, $event)">
              {{ agent.status === 'active' ? 'Stop' : 'Deploy' }}
            </button>
            <span class="created-date">Created {{ formatDate(agent.created) }}</span>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div class="empty-state" *ngIf="filteredAgents().length === 0">
        <div class="empty-icon">🤖</div>
        <h3>No agents found</h3>
        <p>Create your first AI agent to get started with automated tasks and conversations.</p>
        <button class="create-first-agent-btn" (click)="showCreateModal.set(true)">
          Create Your First Agent
        </button>
      </div>
    </div>

    <!-- Create Agent Modal -->
    <div class="modal-overlay" *ngIf="showCreateModal()" (click)="closeCreateModal($event)">
      <div class="create-agent-modal" (click)="$event.stopPropagation()">
        <div class="modal-header">
          <h2>Create New AI Agent</h2>
          <button class="close-btn" (click)="showCreateModal.set(false)">×</button>
        </div>

        <form class="agent-form" (ngSubmit)="createAgent()">
          <div class="form-row">
            <div class="form-group">
              <label for="agentName">Agent Name</label>
              <input type="text" 
                     id="agentName" 
                     [(ngModel)]="newAgent.name" 
                     name="agentName"
                     placeholder="Enter agent name"
                     required>
            </div>

            <div class="form-group">
              <label for="agentType">Agent Type</label>
              <select id="agentType" [(ngModel)]="newAgent.type" name="agentType" required>
                <option value="data-analyst">Data Analyst</option>
                <option value="code-assistant">Code Assistant</option>
                <option value="content-generator">Content Generator</option>
                <option value="research">Research Assistant</option>
                <option value="custom">Custom</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label for="agentDescription">Description</label>
            <textarea id="agentDescription" 
                      [(ngModel)]="newAgent.description" 
                      name="agentDescription"
                      placeholder="Describe what this agent does..."
                      rows="3"
                      required></textarea>
          </div>

          <div class="form-group">
            <label>Capabilities</label>
            <div class="capabilities-input">
              <input type="text" 
                     [(ngModel)]="capabilityInput" 
                     name="capabilityInput"
                     placeholder="Add capability and press Enter"
                     (keyup.enter)="addCapability()">
              <div class="selected-capabilities">
                <span class="capability-tag" *ngFor="let cap of newAgent.capabilities; let i = index">
                  {{ cap }}
                  <button type="button" (click)="removeCapability(i)">×</button>
                </span>
              </div>
            </div>
          </div>

          <div class="form-group">
            <label>MCP Connections</label>
            <div class="mcp-connections-select">
              <div class="connection-option" *ngFor="let connection of availableMCPConnections">
                <input type="checkbox" 
                       [id]="'mcp-' + connection" 
                       [checked]="newAgent.mcpConnections.includes(connection)"
                       (change)="toggleMCPConnection(connection, $event)">
                <label [for]="'mcp-' + connection">{{ connection }}</label>
              </div>
            </div>
          </div>

          <div class="form-actions">
            <button type="button" class="cancel-btn" (click)="showCreateModal.set(false)">
              Cancel
            </button>
            <button type="submit" class="create-btn" [disabled]="!isFormValid()">
              Create Agent
            </button>
          </div>
        </form>
      </div>
    </div>
  `,
  styleUrls: ['./agents.component.scss']
})
export class AgentsComponent implements OnInit {
  
  // UI state - using regular properties for ngModel compatibility
  searchQuery = '';
  selectedStatus = '';
  selectedType = '';
  viewMode = 'grid' as 'grid' | 'list';
  showCreateModal = signal(false);

  agents = signal<Agent[]>([
    {
      id: '1',
      name: 'Data Insight Pro',
      description: 'Advanced data analysis and visualization agent with machine learning capabilities',
      type: 'data-analyst',
      status: 'active',
      capabilities: ['Data Analysis', 'Visualization', 'ML Insights', 'Report Generation'],
      mcpConnections: ['Database', 'Filesystem', 'Web Scraper'],
      lastUsed: new Date(Date.now() - 1000 * 60 * 30),
      totalConversations: 156,
      successRate: 94,
      created: new Date('2024-01-15')
    },
    {
      id: '2',
      name: 'Code Companion',
      description: 'AI-powered coding assistant for multiple programming languages',
      type: 'code-assistant',
      status: 'active',
      capabilities: ['Code Generation', 'Debugging', 'Code Review', 'Documentation'],
      mcpConnections: ['Git', 'Filesystem', 'Database'],
      lastUsed: new Date(Date.now() - 1000 * 60 * 60 * 2),
      totalConversations: 89,
      successRate: 97,
      created: new Date('2024-02-03')
    },
    {
      id: '3',
      name: 'Content Creator',
      description: 'Creative writing and content generation specialist',
      type: 'content-generator',
      status: 'idle',
      capabilities: ['Creative Writing', 'SEO Content', 'Social Media', 'Copywriting'],
      mcpConnections: ['Web Scraper', 'Slack'],
      lastUsed: new Date(Date.now() - 1000 * 60 * 60 * 24),
      totalConversations: 45,
      successRate: 91,
      created: new Date('2024-02-20')
    },
    {
      id: '4',
      name: 'Research Assistant',
      description: 'Comprehensive research and information gathering agent',
      type: 'research',
      status: 'training',
      capabilities: ['Web Research', 'Data Collection', 'Fact Checking', 'Summarization'],
      mcpConnections: ['Web Scraper', 'Database', 'Filesystem'],
      lastUsed: new Date(Date.now() - 1000 * 60 * 60 * 6),
      totalConversations: 23,
      successRate: 88,
      created: new Date('2024-03-01')
    }
  ]);

  filteredAgents = signal<Agent[]>([]);

  newAgent = {
    name: '',
    description: '',
    type: 'data-analyst' as Agent['type'],
    capabilities: [] as string[],
    mcpConnections: [] as string[]
  };

  capabilityInput = '';

  availableMCPConnections = [
    'Database',
    'Filesystem', 
    'Web Scraper',
    'Git',
    'Slack',
    'Email',
    'Calendar',
    'Weather API',
    'Stock API'
  ];

  ngOnInit() {
    this.filteredAgents.set(this.agents());
  }

  filterAgents() {
    let filtered = this.agents();

    if (this.searchQuery) {
      filtered = filtered.filter(agent => 
        agent.name.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
        agent.description.toLowerCase().includes(this.searchQuery.toLowerCase())
      );
    }

    if (this.selectedStatus) {
      filtered = filtered.filter(agent => agent.status === this.selectedStatus);
    }

    if (this.selectedType) {
      filtered = filtered.filter(agent => agent.type === this.selectedType);
    }

    this.filteredAgents.set(filtered);
  }

  getAgentIcon(type: string): string {
    const icons = {
      'data-analyst': '📊',
      'code-assistant': '💻',
      'content-generator': '✍️',
      'research': '🔍',
      'custom': '🛠️'
    };
    return icons[type as keyof typeof icons] || '🤖';
  }

  formatType(type: string): string {
    return type.split('-').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
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

  getDaysActive(created: Date): number {
    const now = new Date();
    const diff = now.getTime() - created.getTime();
    return Math.floor(diff / (1000 * 60 * 60 * 24));
  }

  formatDate(date: Date): string {
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    });
  }

  startConversation(agent: Agent, event?: Event) {
    if (event) {
      event.preventDefault();
      event.stopPropagation();
    }
    console.log('Starting conversation with:', agent.name);
    alert(`Starting conversation with ${agent.name}. This would navigate to the conversations page.`);
    // Navigate to conversations page with agent pre-selected
  }

  editAgent(agent: Agent, event?: Event) {
    if (event) {
      event.preventDefault();
      event.stopPropagation();
    }
    console.log('Editing agent:', agent.name);
    alert(`Editing ${agent.name}. This would open an edit modal.`);
    // Open edit modal
  }

  deleteAgent(agent: Agent, event?: Event) {
    if (event) {
      event.preventDefault();
      event.stopPropagation();
    }
    if (confirm(`Are you sure you want to delete "${agent.name}"?`)) {
      const updatedAgents = this.agents().filter(a => a.id !== agent.id);
      this.agents.set(updatedAgents);
      this.filterAgents();
      alert(`${agent.name} has been deleted successfully.`);
    }
  }

  toggleAgent(agent: Agent, event?: Event) {
    if (event) {
      event.preventDefault();
      event.stopPropagation();
    }
    const newStatus = agent.status === 'active' ? 'idle' : 'active';
    const updatedAgents = this.agents().map(a => {
      if (a.id === agent.id) {
        return {
          ...a,
          status: newStatus as Agent['status']
        };
      }
      return a;
    });
    this.agents.set(updatedAgents);
    this.filterAgents();
    alert(`${agent.name} is now ${newStatus}.`);
  }

  closeCreateModal(event: Event) {
    if (event.target === event.currentTarget) {
      this.showCreateModal.set(false);
    }
  }

  addCapability() {
    if (this.capabilityInput.trim() && !this.newAgent.capabilities.includes(this.capabilityInput.trim())) {
      this.newAgent.capabilities.push(this.capabilityInput.trim());
      this.capabilityInput = '';
    }
  }

  removeCapability(index: number) {
    this.newAgent.capabilities.splice(index, 1);
  }

  toggleMCPConnection(connection: string, event: any) {
    if (event.target.checked) {
      if (!this.newAgent.mcpConnections.includes(connection)) {
        this.newAgent.mcpConnections.push(connection);
      }
    } else {
      this.newAgent.mcpConnections = this.newAgent.mcpConnections.filter(c => c !== connection);
    }
  }

  isFormValid(): boolean {
    return this.newAgent.name.trim() !== '' && 
           this.newAgent.description.trim() !== '' &&
           this.newAgent.capabilities.length > 0;
  }

  createAgent() {
    if (!this.isFormValid()) {
      alert('Please fill in all required fields (Name, Description, and at least one capability).');
      return;
    }

    const newAgent: Agent = {
      id: Date.now().toString(),
      name: this.newAgent.name,
      description: this.newAgent.description,
      type: this.newAgent.type,
      status: 'idle',
      capabilities: [...this.newAgent.capabilities],
      mcpConnections: [...this.newAgent.mcpConnections],
      lastUsed: new Date(),
      totalConversations: 0,
      successRate: 100,
      created: new Date()
    };

    this.agents.update(agents => [...agents, newAgent]);
    this.filterAgents();
    
    // Reset form
    this.newAgent = {
      name: '',
      description: '',
      type: 'data-analyst',
      capabilities: [],
      mcpConnections: []
    };
    this.capabilityInput = '';
    this.showCreateModal.set(false);
    
    alert(`✅ Agent "${newAgent.name}" created successfully!`);
  }
}
