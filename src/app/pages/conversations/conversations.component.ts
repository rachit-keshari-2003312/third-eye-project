import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-conversations',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="conversations-container">
      <div class="conversations-header">
        <h1>Conversations</h1>
        <p>Manage and review your AI agent conversations</p>
        <button class="new-conversation-btn">+ New Conversation</button>
      </div>
      
      <div class="conversations-grid">
        <div class="conversation-card" *ngFor="let i of [1,2,3,4,5,6]">
          <div class="conversation-header">
            <h3>Data Analysis Session {{ i }}</h3>
            <span class="timestamp">2 hours ago</span>
          </div>
          <p class="conversation-preview">Analyzed sales data for Q4 2024 and generated insights...</p>
          <div class="conversation-meta">
            <span class="agent-name">Data Analyst Pro</span>
            <span class="message-count">23 messages</span>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .conversations-container {
      max-width: 1200px;
      margin: 0 auto;
    }
    
    .conversations-header {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 30px;
      border-radius: 20px;
      margin-bottom: 30px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    
    .conversations-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
      gap: 20px;
    }
    
    .conversation-card {
      background: rgba(255, 255, 255, 0.95);
      padding: 20px;
      border-radius: 16px;
      backdrop-filter: blur(20px);
      transition: all 0.3s ease;
    }
    
    .conversation-card:hover {
      transform: translateY(-5px);
      box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
    }
  `]
})
export class ConversationsComponent {}
