import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-analytics',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="analytics-container">
      <div class="analytics-header">
        <h1>Analytics</h1>
        <p>Monitor performance and usage across your AI agents</p>
      </div>
      
      <div class="analytics-grid">
        <div class="chart-card">
          <h3>Agent Usage</h3>
          <div class="chart-placeholder">
            <div class="chart-bars">
              <div class="bar" style="height: 60%"></div>
              <div class="bar" style="height: 80%"></div>
              <div class="bar" style="height: 45%"></div>
              <div class="bar" style="height: 90%"></div>
              <div class="bar" style="height: 70%"></div>
            </div>
          </div>
        </div>
        
        <div class="chart-card">
          <h3>Response Times</h3>
          <div class="chart-placeholder">
            <div class="chart-line">
              <svg width="100%" height="150" viewBox="0 0 300 150">
                <polyline points="0,120 60,80 120,100 180,60 240,90 300,40" 
                          stroke="#667eea" stroke-width="3" fill="none"/>
              </svg>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .analytics-container {
      max-width: 1200px;
      margin: 0 auto;
    }
    
    .analytics-header {
      background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
      color: white;
      padding: 30px;
      border-radius: 20px;
      margin-bottom: 30px;
      text-align: center;
    }
    
    .analytics-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
      gap: 25px;
    }
    
    .chart-card {
      background: rgba(255, 255, 255, 0.95);
      padding: 25px;
      border-radius: 16px;
      backdrop-filter: blur(20px);
    }
    
    .chart-placeholder .chart-bars {
      display: flex;
      align-items: end;
      gap: 10px;
      height: 150px;
    }
    
    .chart-bars .bar {
      flex: 1;
      background: linear-gradient(to top, #667eea 0%, #764ba2 100%);
      border-radius: 4px 4px 0 0;
      min-height: 20px;
    }
  `]
})
export class AnalyticsComponent {}
