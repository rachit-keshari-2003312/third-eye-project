# Quick Start: Dashboard Generation

## 🚀 Get Started in 3 Minutes

This guide will help you quickly test the dashboard generation feature.

## Prerequisites

- Backend server running on `http://localhost:8000`
- Frontend running on `http://localhost:4200`

## Method 1: Using the Chatbot (Recommended)

### Step 1: Start the Application

```bash
cd third-eye-project
./start-both.sh
```

### Step 2: Open the Dashboard

1. Navigate to `http://localhost:4200/dashboard`
2. You'll see an empty dashboard state with a message: "No Dashboards Yet"

### Step 3: Open the Chatbot

1. Click the **"💬 Ask a Question"** button
2. The chatbot modal will open

### Step 4: Enable Dashboard Generation

1. Look for the checkbox **"📊 Auto-generate Dashboards"**
2. Make sure it's checked (it's enabled by default)

### Step 5: Test with Sample Data

Since the backend might not have real query endpoints yet, we'll use the browser console to simulate query results:

1. Open browser DevTools (F12 or Cmd+Option+I)
2. Go to the Console tab
3. Paste this code:

```javascript
// Get the dashboard service instance
const dashboardService = window.angular?.injector?.get?.('DashboardService');

// Or inject manually through the component
// This is a sample query result
const sampleResult = {
  "success": true,
  "prompt": "How many CKYC details were fetched in the last 30 days?",
  "analysis": {},
  "service": "redash",
  "action": "sql_query",
  "result": null,
  "raw_data": {
    "columns": [
      {
        "friendly_name": "CKYC Details Fetched",
        "type": "integer",
        "name": "ckyc_details_fetched"
      }
    ],
    "rows": [
      {
        "ckyc_details_fetched": 11871
      }
    ]
  },
  "answer": "In the last 30 days, 11,871 CKYC details have been fetched.",
  "sql": "SELECT COUNT(*) AS ckyc_details_fetched FROM ckyc_details WHERE updated_at >= NOW() - INTERVAL 30 DAY;",
  "explanation": "This query counts rows from the last 30 days.",
  "row_count": 1,
  "data_source_id": 79,
  "timestamp": new Date().toISOString()
};

// This will be automatically done when you receive a query response in the chatbot
console.log('Sample result ready for dashboard generation');
```

## Method 2: Using Test Endpoints (Easier!)

### Step 1: Create Test Buttons

I've added test endpoints to the backend. You can call them from any HTTP client:

**Test 1: Metric Widget**
```bash
curl -X POST http://localhost:8000/api/dashboard/test-query
```

**Test 2: Table Widget**
```bash
curl -X POST http://localhost:8000/api/dashboard/test-table-query
```

**Test 3: Chart Widget**
```bash
curl -X POST http://localhost:8000/api/dashboard/test-chart-query
```

### Step 2: Add Test Buttons to Dashboard

For easier testing, add these buttons to your dashboard temporarily. Edit the dashboard component template and add this section:

```typescript
<!-- Test Dashboard Generation -->
<div class="test-section" style="margin: 20px 0; padding: 20px; background: #f0f0f0; border-radius: 10px;">
  <h3>🧪 Test Dashboard Generation</h3>
  <div style="display: flex; gap: 10px; margin-top: 10px;">
    <button (click)="testMetricWidget()" style="padding: 10px 20px; background: #667eea; color: white; border: none; border-radius: 8px; cursor: pointer;">
      Generate Metric Widget
    </button>
    <button (click)="testTableWidget()" style="padding: 10px 20px; background: #f093fb; color: white; border: none; border-radius: 8px; cursor: pointer;">
      Generate Table Widget
    </button>
    <button (click)="testChartWidget()" style="padding: 10px 20px; background: #4facfe; color: white; border: none; border-radius: 8px; cursor: pointer;">
      Generate Chart Widget
    </button>
  </div>
</div>
```

And add these methods to your dashboard component:

```typescript
import { HttpClient } from '@angular/common/http';

constructor(
  public dashboardService: DashboardService,
  private http: HttpClient
) {}

async testMetricWidget() {
  try {
    const result = await firstValueFrom(
      this.http.post<any>('http://localhost:8000/api/dashboard/test-query', {})
    );
    const widget = this.dashboardService.generateWidgetFromQueryResult(result);
    if (widget) {
      this.dashboardService.addWidget(widget);
      alert('Metric widget generated!');
    }
  } catch (error) {
    console.error('Error generating widget:', error);
    alert('Error generating widget. Check console.');
  }
}

async testTableWidget() {
  try {
    const result = await firstValueFrom(
      this.http.post<any>('http://localhost:8000/api/dashboard/test-table-query', {})
    );
    const widget = this.dashboardService.generateWidgetFromQueryResult(result);
    if (widget) {
      this.dashboardService.addWidget(widget);
      alert('Table widget generated!');
    }
  } catch (error) {
    console.error('Error generating widget:', error);
    alert('Error generating widget. Check console.');
  }
}

async testChartWidget() {
  try {
    const result = await firstValueFrom(
      this.http.post<any>('http://localhost:8000/api/dashboard/test-chart-query', {})
    );
    const widget = this.dashboardService.generateWidgetFromQueryResult(result);
    if (widget) {
      this.dashboardService.addWidget(widget);
      alert('Chart widget generated!');
    }
  } catch (error) {
    console.error('Error generating widget:', error);
    alert('Error generating widget. Check console.');
  }
}
```

## Method 3: Manual Widget Creation

You can also create widgets manually in the browser console:

```javascript
// Access the dashboard component
// Note: This is pseudo-code, actual access depends on your Angular setup

const widget = {
  id: 'test-' + Date.now(),
  type: 'metric',
  title: 'Test Metric',
  description: 'This is a test metric widget',
  data: {
    value: 42,
    label: 'Test Value',
    type: 'integer'
  },
  metadata: {
    prompt: 'Show me test data',
    timestamp: new Date().toISOString()
  }
};

// Add to dashboard
// dashboardService.addWidget(widget);
```

## Testing Widget Types

### 1. Metric Widget Test

**Expected Result**: Large number (11,871) with label "CKYC Details Fetched"

**Characteristics**:
- Single value display
- Gradient text effect
- Large, prominent number
- Small descriptive label

### 2. Table Widget Test

**Expected Result**: Table with 5 rows showing user data

**Characteristics**:
- Scrollable table
- Sticky header
- Multiple columns (User ID, Username, Transaction Count, Total Amount)
- Hover effects on rows

### 3. Chart Widget Test

**Expected Result**: Bar chart showing 7 days of transaction data

**Characteristics**:
- Animated bars
- Multiple datasets (transaction count and total amount)
- Legend at bottom
- Date labels on X-axis
- Hover tooltips

## Verifying the Installation

### ✅ Checklist

- [ ] Backend server is running (`http://localhost:8000/api/health` returns 200)
- [ ] Frontend is running (`http://localhost:4200` loads)
- [ ] Dashboard page shows the empty state or widgets
- [ ] Chatbot opens when clicking "Start Chat"
- [ ] Test endpoints return JSON data
- [ ] Widgets appear after generation
- [ ] Widgets persist after page refresh
- [ ] Widget details modal opens
- [ ] Widgets can be removed
- [ ] "Clear All" button works

## Troubleshooting

### Backend Not Starting

```bash
cd backend
source ../venv/bin/activate  # or .\venv\Scripts\activate on Windows
pip install -r requirements.txt
python app.py
```

### Frontend Not Starting

```bash
npm install
npm start
```

### CORS Issues

Make sure the backend CORS settings include your frontend URL:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://127.0.0.1:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Widgets Not Appearing

1. Check browser console for errors
2. Verify localStorage is enabled
3. Check Network tab for API calls
4. Ensure DashboardService is properly injected

### Test Endpoints Not Working

```bash
# Test backend health first
curl http://localhost:8000/api/health

# Test dashboard endpoint
curl -X POST http://localhost:8000/api/dashboard/test-query

# If you get connection refused, make sure backend is running
ps aux | grep python  # Check if backend process is running
```

## Next Steps

After successfully testing the basic features:

1. **Integrate with Real Data**
   - Connect to your actual database
   - Create SQL query endpoints
   - Map your data models to the QueryResult format

2. **Customize Widgets**
   - Modify colors and styles
   - Add custom widget types
   - Implement additional chart types

3. **Enhance Chatbot**
   - Add natural language processing
   - Implement query parsing
   - Add query suggestions

4. **Deploy**
   - Set up production environment
   - Configure environment variables
   - Set up monitoring and logging

## Example Workflow

Here's a complete example workflow:

```bash
# 1. Start both servers
./start-both.sh

# 2. Wait for servers to start (about 10 seconds)

# 3. Open browser to http://localhost:4200/dashboard

# 4. Open browser console and test the endpoints:
curl -X POST http://localhost:8000/api/dashboard/test-query | jq

# 5. You should see JSON output with raw_data

# 6. In the application:
#    - Click "Ask a Question"
#    - Ensure "Auto-generate Dashboards" is checked
#    - (In production, ask a real question and get back query results)

# 7. For testing, use the test buttons or console to generate widgets

# 8. Verify widgets appear on the dashboard

# 9. Test interactions:
#    - Click info button to see details
#    - Click X to remove widget
#    - Refresh page to verify persistence
```

## Support

If you encounter issues:

1. Check the main README for general setup
2. Review DASHBOARD_GENERATION.md for detailed documentation
3. Check browser console for JavaScript errors
4. Check backend logs for Python errors
5. Verify all dependencies are installed

## Demo Data

You can use the following sample data structures for testing:

### Metric Data
```json
{
  "columns": [{"name": "count", "type": "integer", "friendly_name": "Count"}],
  "rows": [{"count": 12345}]
}
```

### Table Data
```json
{
  "columns": [
    {"name": "id", "type": "integer", "friendly_name": "ID"},
    {"name": "name", "type": "string", "friendly_name": "Name"},
    {"name": "value", "type": "float", "friendly_name": "Value"}
  ],
  "rows": [
    {"id": 1, "name": "Item 1", "value": 99.99},
    {"id": 2, "name": "Item 2", "value": 149.99}
  ]
}
```

### Chart Data
```json
{
  "columns": [
    {"name": "date", "type": "date", "friendly_name": "Date"},
    {"name": "count", "type": "integer", "friendly_name": "Count"}
  ],
  "rows": [
    {"date": "2025-11-01", "count": 100},
    {"date": "2025-11-02", "count": 120},
    {"date": "2025-11-03", "count": 115}
  ]
}
```

Happy dashboard generating! 🎉


