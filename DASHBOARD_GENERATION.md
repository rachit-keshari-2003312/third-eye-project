# Dashboard Generation System

## Overview

The Third-Eye platform now includes an **AI-powered Dashboard Generation System** that automatically creates beautiful, interactive visualizations from SQL query results. This feature seamlessly integrates with the chatbot to transform data queries into visual insights.

## Features

### 🎨 Automatic Widget Generation
- **Metric Widgets**: Display single-value KPIs with large, prominent numbers
- **Table Widgets**: Present tabular data with sortable columns and responsive design
- **Chart Widgets**: Visualize time-series and aggregated data with interactive bar charts
- **Text Widgets**: Display analysis and insights in formatted text

### 🤖 Chatbot Integration
- Enable/disable auto-generation with a simple checkbox
- Automatic detection of query result data
- Real-time widget creation from chatbot responses
- Persistent storage in localStorage

### 📊 Visual Presentation
- Modern, glassmorphic design with blur effects
- Responsive layouts for all screen sizes
- Interactive hover effects and animations
- Color-coded visualizations with gradients

### 🔍 Widget Details
- View SQL queries that generated the data
- See explanations and analysis
- Access metadata (data source, timestamp, etc.)
- Remove widgets individually or clear all at once

## Data Format

The system accepts query results in the following JSON format:

```json
{
  "success": true,
  "prompt": "Your query prompt here",
  "analysis": {},
  "service": "redash",
  "action": "sql_query",
  "result": null,
  "raw_data": {
    "columns": [
      {
        "friendly_name": "Column Display Name",
        "type": "integer",
        "name": "column_name"
      }
    ],
    "rows": [
      {
        "column_name": 12345
      }
    ]
  },
  "answer": "AI-generated analysis of the results",
  "llm_intent": null,
  "sql": "SELECT COUNT(*) as column_name FROM table_name;",
  "explanation": "Explanation of what the query does",
  "row_count": 1,
  "data_source_id": 79,
  "error": null,
  "timestamp": "2025-11-20T22:39:27.679044"
}
```

## Usage

### 1. Through Chatbot

The easiest way to generate dashboards is through the chatbot:

1. **Open the Chatbot**
   - Click on "Start Chat" from the dashboard
   - Or use the floating chatbot button

2. **Enable Dashboard Generation**
   - Check the "📊 Auto-generate Dashboards" option
   - This is enabled by default

3. **Ask Data Questions**
   - Ask natural language questions about your data
   - Example: "How many users signed up in the last 30 days?"
   - The chatbot will process your query and automatically generate a dashboard widget

4. **View Your Dashboards**
   - Navigate to the Dashboard page
   - Your generated widgets will appear in the "Generated Dashboards" section
   - Widgets are automatically saved and persist between sessions

### 2. Programmatically

You can also generate dashboards programmatically using the `DashboardService`:

```typescript
import { DashboardService, QueryResult } from './services/dashboard.service';

// Inject the service
constructor(private dashboardService: DashboardService) {}

// Create a widget from query result
const queryResult: QueryResult = {
  // ... your query result data
};

const widget = this.dashboardService.generateWidgetFromQueryResult(queryResult);
if (widget) {
  this.dashboardService.addWidget(widget);
}
```

### 3. Test Endpoints

The backend provides test endpoints to simulate query results:

```bash
# Test single metric
curl -X POST http://localhost:8000/api/dashboard/test-query

# Test table data
curl -X POST http://localhost:8000/api/dashboard/test-table-query

# Test chart data
curl -X POST http://localhost:8000/api/dashboard/test-chart-query
```

## Widget Types

### Metric Widget

**When Generated**: Single row, single column results

**Best For**:
- KPIs (Key Performance Indicators)
- Counts and totals
- Single value statistics

**Example Query**:
```sql
SELECT COUNT(*) as total_users FROM users;
```

**Appearance**: Large number display with label

---

### Table Widget

**When Generated**: Multiple rows or multiple columns

**Best For**:
- Detailed data listings
- User records
- Transaction histories
- Multi-dimensional data

**Example Query**:
```sql
SELECT user_id, username, email, created_at 
FROM users 
ORDER BY created_at DESC 
LIMIT 10;
```

**Appearance**: Scrollable table with sticky headers

---

### Chart Widget

**When Generated**: Time-series data or data with numeric values suitable for visualization

**Criteria**:
- Has date/time column
- Has numeric column(s)
- Between 2-50 rows
- Data is aggregated

**Best For**:
- Trends over time
- Comparisons
- Distribution analysis

**Example Query**:
```sql
SELECT DATE(created_at) as date, COUNT(*) as count
FROM transactions
WHERE created_at >= NOW() - INTERVAL 7 DAY
GROUP BY DATE(created_at);
```

**Appearance**: Animated bar chart with legend

---

### Text Widget

**When Generated**: No structured data or error cases

**Best For**:
- Analysis summaries
- Error messages
- Textual insights

**Appearance**: Formatted text box with styling

## API Reference

### DashboardService

#### Methods

##### `generateWidgetFromQueryResult(queryResult: QueryResult): DashboardWidget | null`
Generates a dashboard widget from a query result.

**Parameters**:
- `queryResult`: The query result object

**Returns**: Dashboard widget or null if generation fails

---

##### `addWidget(widget: DashboardWidget): void`
Adds a widget to the dashboard.

**Parameters**:
- `widget`: The widget to add

---

##### `removeWidget(widgetId: string): void`
Removes a widget from the dashboard.

**Parameters**:
- `widgetId`: The ID of the widget to remove

---

##### `updateWidget(widgetId: string, updates: Partial<DashboardWidget>): void`
Updates an existing widget.

**Parameters**:
- `widgetId`: The ID of the widget to update
- `updates`: Partial widget object with updates

---

##### `clearAllWidgets(): void`
Clears all widgets from the dashboard.

---

##### `getWidgets(): DashboardWidget[]`
Returns all current widgets.

**Returns**: Array of dashboard widgets

### Backend Endpoints

#### `POST /api/dashboard/test-query`
Returns a sample single-metric query result.

**Response**: QueryResult with single value

---

#### `POST /api/dashboard/test-table-query`
Returns a sample table query result with multiple rows.

**Response**: QueryResult with tabular data

---

#### `POST /api/dashboard/test-chart-query`
Returns a sample time-series query result suitable for charts.

**Response**: QueryResult with time-series data

## Customization

### Widget Styling

Widget styles can be customized in:
- `/src/app/components/dashboard-widget/dashboard-widget.component.scss`

### Dashboard Layout

Dashboard grid and responsive breakpoints can be modified in:
- `/src/app/pages/dashboard/dashboard.component.scss`

Look for the `.widgets-grid` class:

```scss
.widgets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 25px;
}
```

### Chart Colors

Chart colors are defined in the `DashboardWidgetComponent`:

```typescript
private chartColors = [
  'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
  'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
  'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
  'linear-gradient(135deg, #30cfd0 0%, #330867 100%)',
];
```

## Storage

Widgets are automatically persisted to `localStorage` with the key:
```
third-eye-dashboard-widgets
```

This ensures your dashboards remain available across browser sessions.

To clear storage programmatically:
```typescript
localStorage.removeItem('third-eye-dashboard-widgets');
```

## Best Practices

### Query Design

1. **Limit Rows**: Keep table results under 100 rows for performance
2. **Aggregate Data**: Use GROUP BY for better visualizations
3. **Use Friendly Names**: Set descriptive `friendly_name` in column definitions
4. **Type Correctly**: Ensure column types are accurate for proper formatting

### Widget Management

1. **Clear Old Widgets**: Regularly remove outdated widgets
2. **Organize by Topic**: Group related queries together
3. **Use Descriptive Prompts**: Write clear prompts for better widget titles

### Performance

1. **Lazy Loading**: Widgets load on-demand
2. **Virtual Scrolling**: Implemented for large tables
3. **Memoization**: Widget data is cached to prevent re-renders

## Troubleshooting

### Widget Not Generated

**Problem**: Chatbot doesn't generate a widget

**Solutions**:
1. Ensure "Auto-generate Dashboards" is checked
2. Verify the response contains `raw_data` with `columns` and `rows`
3. Check browser console for errors

---

### Incorrect Widget Type

**Problem**: Data displays as table when you want a chart

**Solutions**:
1. Ensure your data has time-series structure (date + numeric columns)
2. Keep row count between 2-50
3. Add date/time column to your query

---

### Widget Missing After Refresh

**Problem**: Widgets disappear after page refresh

**Solutions**:
1. Check localStorage is enabled in your browser
2. Verify localStorage quota isn't exceeded
3. Check browser console for storage errors

---

### Styling Issues

**Problem**: Widgets don't display correctly

**Solutions**:
1. Clear browser cache
2. Check for CSS conflicts
3. Verify all component stylesheets are imported

## Future Enhancements

Planned features for future releases:

- [ ] More chart types (line, pie, scatter)
- [ ] Widget drag-and-drop repositioning
- [ ] Export widgets to PDF/PNG
- [ ] Share widgets with team members
- [ ] Real-time data updates
- [ ] Custom widget templates
- [ ] Widget grouping and folders
- [ ] Advanced filtering and drill-down
- [ ] Integration with more data sources

## Examples

### Example 1: User Growth Metric

**Query**:
```sql
SELECT COUNT(*) as new_users 
FROM users 
WHERE created_at >= NOW() - INTERVAL 30 DAY;
```

**Result**: Metric widget showing "487 New Users"

---

### Example 2: Revenue by Product

**Query**:
```sql
SELECT 
  product_name,
  SUM(amount) as total_revenue,
  COUNT(*) as order_count
FROM orders o
JOIN products p ON o.product_id = p.id
WHERE o.created_at >= NOW() - INTERVAL 7 DAY
GROUP BY product_name
ORDER BY total_revenue DESC
LIMIT 5;
```

**Result**: Table widget with product names, revenues, and counts

---

### Example 3: Daily Active Users

**Query**:
```sql
SELECT 
  DATE(login_time) as date,
  COUNT(DISTINCT user_id) as active_users
FROM user_sessions
WHERE login_time >= NOW() - INTERVAL 14 DAY
GROUP BY DATE(login_time)
ORDER BY date;
```

**Result**: Chart widget showing trend line of daily active users

## Support

For issues or questions:
- Check the troubleshooting section above
- Review the code in `/src/app/services/dashboard.service.ts`
- Examine example responses from test endpoints
- Check browser console for detailed error messages

## License

This dashboard generation system is part of the Third-Eye platform and follows the same license terms.


