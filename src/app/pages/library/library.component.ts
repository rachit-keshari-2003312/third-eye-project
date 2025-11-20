import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-library',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="library-container">
      <div class="library-header">
        <h1>Library</h1>
        <p>Prompts, templates, and reusable AI components</p>
        <button class="create-prompt-btn">+ Create Prompt</button>
      </div>
      
      <div class="library-tabs">
        <button class="tab-btn active">Prompts</button>
        <button class="tab-btn">Assets</button>
        <button class="tab-btn">Templates</button>
      </div>
      
      <div class="library-grid">
        <div class="library-item" *ngFor="let i of [1,2,3,4,5,6]">
          <div class="item-header">
            <h3>Data Analysis Prompt {{ i }}</h3>
            <span class="item-type">Prompt</span>
          </div>
          <p class="item-description">Analyze tabular data and generate comprehensive insights...</p>
          <div class="item-actions">
            <button class="use-btn">Use</button>
            <button class="edit-btn">Edit</button>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .library-container {
      max-width: 1200px;
      margin: 0 auto;
    }
    
    .library-header {
      background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
      color: white;
      padding: 30px;
      border-radius: 20px;
      margin-bottom: 30px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    
    .library-tabs {
      display: flex;
      gap: 10px;
      margin-bottom: 30px;
    }
    
    .tab-btn {
      padding: 10px 20px;
      border: 1px solid #e0e0e0;
      background: white;
      border-radius: 8px;
      cursor: pointer;
    }
    
    .tab-btn.active {
      background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
      color: white;
      border-color: transparent;
    }
    
    .library-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 20px;
    }
    
    .library-item {
      background: rgba(255, 255, 255, 0.95);
      padding: 20px;
      border-radius: 16px;
      backdrop-filter: blur(20px);
      transition: all 0.3s ease;
    }
    
    .library-item:hover {
      transform: translateY(-5px);
      box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
    }
  `]
})
export class LibraryComponent {}
