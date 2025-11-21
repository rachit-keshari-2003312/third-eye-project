import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DashboardWidget } from '../../services/dashboard.service';

@Component({
  selector: 'app-dashboard-widget',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="dashboard-widget" [class]="'widget-type-' + widget.type">
      <div class="widget-header">
        <div class="widget-title-section">
          <h4 class="widget-title">{{ widget.title }}</h4>
          <p class="widget-description" *ngIf="widget.description">{{ widget.description }}</p>
        </div>
        <div class="widget-actions">
          <button class="widget-action-btn" title="View Details" (click)="onViewDetails()">
            <span>ℹ️</span>
          </button>
          <button class="widget-action-btn" title="Remove" (click)="onRemove()">
            <span>✕</span>
          </button>
        </div>
      </div>

      <div class="widget-content">
        <!-- Metric Widget -->
        <div *ngIf="widget.type === 'metric'" class="metric-widget">
          <div class="metric-value">{{ formatMetricValue(widget.data.value) }}</div>
          <div class="metric-label">{{ widget.data.label }}</div>
        </div>

        <!-- Table Widget -->
        <div *ngIf="widget.type === 'table'" class="table-widget">
          <div class="table-container">
            <table>
              <thead>
                <tr>
                  <th *ngFor="let column of widget.data.columns">
                    {{ column.label }}
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr *ngFor="let row of widget.data.rows; let i = index">
                  <td *ngFor="let column of widget.data.columns">
                    {{ formatCellValue(row[column.name], column.type) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Chart Widget -->
        <div *ngIf="widget.type === 'chart'" class="chart-widget">
          <div class="chart-container">
            <div class="chart-bars">
              <div *ngFor="let label of widget.data.labels; let i = index" 
                   class="chart-bar-group">
                <div class="chart-bar-container">
                  <div *ngFor="let dataset of widget.data.datasets; let j = index"
                       class="chart-bar"
                       [style.height.%]="getBarHeight(dataset.data[i], widget.data.datasets)"
                       [style.background]="getBarColor(j)"
                       [title]="dataset.label + ': ' + dataset.data[i]">
                  </div>
                </div>
                <div class="chart-label">{{ formatChartLabel(label) }}</div>
              </div>
            </div>
            <div class="chart-legend">
              <div *ngFor="let dataset of widget.data.datasets; let i = index" 
                   class="legend-item">
                <div class="legend-color" [style.background]="getBarColor(i)"></div>
                <span>{{ dataset.label }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Text Widget -->
        <div *ngIf="widget.type === 'text'" class="text-widget">
          <p>{{ widget.data.text }}</p>
        </div>
      </div>

      <div class="widget-footer" *ngIf="widget.metadata?.timestamp">
        <span class="widget-timestamp">
          {{ formatTimestamp(widget.metadata?.timestamp || '') }}
        </span>
      </div>

      <!-- Details Modal -->
      <div class="widget-details-modal" *ngIf="showDetails" (click)="closeDetails()">
        <div class="modal-content" (click)="$event.stopPropagation()">
          <div class="modal-header">
            <h3>Widget Details</h3>
            <button class="close-btn" (click)="closeDetails()">✕</button>
          </div>
          <div class="modal-body">
            <div class="detail-section" *ngIf="widget.metadata?.prompt">
              <h4>Prompt</h4>
              <p>{{ widget.metadata?.prompt }}</p>
            </div>
            <div class="detail-section" *ngIf="widget.metadata?.sql">
              <h4>SQL Query</h4>
              <pre><code>{{ widget.metadata?.sql }}</code></pre>
            </div>
            <div class="detail-section" *ngIf="widget.metadata?.explanation">
              <h4>Explanation</h4>
              <p>{{ widget.metadata?.explanation }}</p>
            </div>
            <div class="detail-section" *ngIf="widget.metadata?.answer">
              <h4>Analysis</h4>
              <p>{{ widget.metadata?.answer }}</p>
            </div>
            <div class="detail-section" *ngIf="widget.metadata?.dataSourceId">
              <h4>Data Source</h4>
              <p>Data Source ID: {{ widget.metadata?.dataSourceId }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styleUrls: ['./dashboard-widget.component.scss']
})
export class DashboardWidgetComponent {
  @Input() widget!: DashboardWidget;
  @Output() remove = new EventEmitter<string>();
  @Output() viewDetails = new EventEmitter<DashboardWidget>();

  showDetails = false;

  private chartColors = [
    'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
    'linear-gradient(135deg, #30cfd0 0%, #330867 100%)',
  ];

  onRemove() {
    this.remove.emit(this.widget.id);
  }

  onViewDetails() {
    this.showDetails = true;
  }

  closeDetails() {
    this.showDetails = false;
  }

  formatMetricValue(value: any): string {
    if (typeof value === 'number') {
      // Format large numbers with commas
      return value.toLocaleString();
    }
    return String(value);
  }

  formatCellValue(value: any, type: string): string {
    if (value === null || value === undefined) {
      return '-';
    }

    if (type === 'integer' || type === 'float' || type === 'number') {
      if (typeof value === 'number') {
        return value.toLocaleString();
      }
    }

    if (type === 'date' || type === 'datetime') {
      try {
        return new Date(value).toLocaleDateString();
      } catch {
        return String(value);
      }
    }

    return String(value);
  }

  formatChartLabel(label: any): string {
    if (typeof label === 'string' && label.length > 15) {
      return label.substring(0, 12) + '...';
    }
    return String(label);
  }

  formatTimestamp(timestamp: string): string {
    try {
      const date = new Date(timestamp);
      return date.toLocaleString();
    } catch {
      return timestamp;
    }
  }

  getBarHeight(value: number, datasets: any[]): number {
    // Find max value across all datasets for normalization
    const allValues = datasets.flatMap(ds => ds.data);
    const maxValue = Math.max(...allValues);
    const minValue = Math.min(...allValues, 0);
    
    if (maxValue === minValue) {
      return 50; // Default if all values are the same
    }

    // Normalize to 0-100 range, with minimum of 5% for visibility
    const normalized = ((value - minValue) / (maxValue - minValue)) * 90 + 10;
    return Math.max(5, normalized);
  }

  getBarColor(index: number): string {
    return this.chartColors[index % this.chartColors.length];
  }
}

