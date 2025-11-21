import { Injectable, signal } from '@angular/core';

export interface DashboardWidget {
  id: string;
  type: 'table' | 'metric' | 'chart' | 'text';
  title: string;
  description?: string;
  data: any;
  metadata?: {
    prompt?: string;
    sql?: string;
    explanation?: string;
    answer?: string;
    timestamp?: string;
    dataSourceId?: number;
  };
  position?: { x: number; y: number; width: number; height: number };
}

export interface QueryResult {
  success: boolean;
  prompt: string;
  analysis: any;
  service: string;
  action: string;
  result: any;
  raw_data: {
    columns: Array<{
      friendly_name: string;
      type: string;
      name: string;
    }>;
    rows: Array<any>;
  };
  answer: string;
  llm_intent?: string;
  sql?: string;
  explanation?: string;
  row_count?: number;
  data_source_id?: number;
  error?: string;
  timestamp?: string;
}

@Injectable({
  providedIn: 'root'
})
export class DashboardService {
  private widgets = signal<DashboardWidget[]>([]);
  
  // Expose as readonly signal
  readonly dashboardWidgets = this.widgets.asReadonly();

  constructor() {
    // Load saved widgets from localStorage
    this.loadWidgetsFromStorage();
  }

  /**
   * Generate dashboard widgets from a query result
   */
  generateWidgetFromQueryResult(queryResult: QueryResult): DashboardWidget | null {
    if (!queryResult.success || !queryResult.raw_data) {
      return null;
    }

    const widgetId = `widget-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    
    // Determine widget type based on data
    const widgetType = this.determineWidgetType(queryResult);
    
    const widget: DashboardWidget = {
      id: widgetId,
      type: widgetType,
      title: this.generateWidgetTitle(queryResult),
      description: queryResult.prompt,
      data: this.formatWidgetData(queryResult, widgetType),
      metadata: {
        prompt: queryResult.prompt,
        sql: queryResult.sql,
        explanation: queryResult.explanation,
        answer: queryResult.answer,
        timestamp: queryResult.timestamp,
        dataSourceId: queryResult.data_source_id
      }
    };

    return widget;
  }

  /**
   * Add a widget to the dashboard
   */
  addWidget(widget: DashboardWidget): void {
    this.widgets.update(widgets => [...widgets, widget]);
    this.saveWidgetsToStorage();
  }

  /**
   * Remove a widget from the dashboard
   */
  removeWidget(widgetId: string): void {
    this.widgets.update(widgets => widgets.filter(w => w.id !== widgetId));
    this.saveWidgetsToStorage();
  }

  /**
   * Update a widget
   */
  updateWidget(widgetId: string, updates: Partial<DashboardWidget>): void {
    this.widgets.update(widgets => 
      widgets.map(w => w.id === widgetId ? { ...w, ...updates } : w)
    );
    this.saveWidgetsToStorage();
  }

  /**
   * Clear all widgets
   */
  clearAllWidgets(): void {
    this.widgets.set([]);
    this.saveWidgetsToStorage();
  }

  /**
   * Get all widgets
   */
  getWidgets(): DashboardWidget[] {
    return this.widgets();
  }

  private determineWidgetType(queryResult: QueryResult): DashboardWidget['type'] {
    const { rows, columns } = queryResult.raw_data;

    // Single value = metric
    if (rows.length === 1 && columns.length === 1) {
      return 'metric';
    }

    // Multiple columns or rows = table (can be enhanced to detect chart data)
    if (rows.length > 1 || columns.length > 1) {
      // Check if it's time-series or suitable for chart
      const hasNumericColumn = columns.some(col => 
        col.type === 'integer' || col.type === 'float' || col.type === 'number'
      );
      const hasTimeColumn = columns.some(col => 
        col.type === 'date' || col.type === 'datetime' || 
        col.name.toLowerCase().includes('date') || 
        col.name.toLowerCase().includes('time')
      );

      // If it has time and numeric columns, it's chart-worthy
      if (hasTimeColumn && hasNumericColumn && rows.length > 1 && rows.length <= 50) {
        return 'chart';
      }

      return 'table';
    }

    return 'text';
  }

  private generateWidgetTitle(queryResult: QueryResult): string {
    // Extract meaningful title from prompt or SQL
    const prompt = queryResult.prompt;
    
    // Try to extract the main subject from the prompt
    if (prompt) {
      // Capitalize first letter and limit length
      const title = prompt.charAt(0).toUpperCase() + prompt.slice(1);
      return title.length > 50 ? title.substring(0, 50) + '...' : title;
    }

    return 'Query Result';
  }

  private formatWidgetData(queryResult: QueryResult, type: DashboardWidget['type']): any {
    const { rows, columns } = queryResult.raw_data;

    switch (type) {
      case 'metric':
        // Single value metric
        const col = columns[0];
        const value = rows[0][col.name];
        return {
          value,
          label: col.friendly_name || col.name,
          type: col.type
        };

      case 'table':
        return {
          columns: columns.map(col => ({
            name: col.name,
            label: col.friendly_name || col.name,
            type: col.type
          })),
          rows: rows
        };

      case 'chart':
        // Format for chart visualization
        return this.formatChartData(columns, rows);

      case 'text':
        return {
          text: queryResult.answer || 'No data available'
        };

      default:
        return queryResult.raw_data;
    }
  }

  private formatChartData(columns: any[], rows: any[]): any {
    // Find the label column (time/category) and value columns (numeric)
    const labelColumn = columns.find(col => 
      col.type === 'date' || col.type === 'datetime' || col.type === 'string'
    ) || columns[0];

    const valueColumns = columns.filter(col => 
      col.type === 'integer' || col.type === 'float' || col.type === 'number'
    );

    const labels = rows.map(row => row[labelColumn.name]);
    const datasets = valueColumns.map(col => ({
      label: col.friendly_name || col.name,
      data: rows.map(row => row[col.name]),
      type: col.type
    }));

    return {
      labels,
      datasets,
      chartType: 'bar' // Can be enhanced to detect best chart type
    };
  }

  private saveWidgetsToStorage(): void {
    try {
      const widgetsData = JSON.stringify(this.widgets());
      localStorage.setItem('third-eye-dashboard-widgets', widgetsData);
    } catch (error) {
      console.error('Error saving widgets to storage:', error);
    }
  }

  private loadWidgetsFromStorage(): void {
    try {
      const savedWidgets = localStorage.getItem('third-eye-dashboard-widgets');
      if (savedWidgets) {
        const widgets = JSON.parse(savedWidgets);
        this.widgets.set(widgets);
      }
    } catch (error) {
      console.error('Error loading widgets from storage:', error);
    }
  }
}


