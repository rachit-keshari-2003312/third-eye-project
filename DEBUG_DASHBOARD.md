# 🔍 Debug Dashboard Generation

## Issue: Dashboard widgets not appearing after clicking buttons

Follow these steps to diagnose and fix the issue:

## Step 1: Check Backend is Running

Open a new terminal and run:

```bash
curl http://localhost:8000/api/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "services": {...}
}
```

**If this fails:**
- Backend is not running
- Start it: `cd backend && source ../venv/bin/activate && python app.py`

## Step 2: Test the Dashboard Endpoints

```bash
# Test metric endpoint
curl -X POST http://localhost:8000/api/dashboard/test-query

# Test table endpoint  
curl -X POST http://localhost:8000/api/dashboard/test-table-query

# Test chart endpoint
curl -X POST http://localhost:8000/api/dashboard/test-chart-query
```

**Expected:** Each should return JSON with `raw_data`, `columns`, `rows`

**If these fail:**
- The endpoints don't exist in backend
- Check `backend/app.py` has the dashboard endpoints

## Step 3: Check Browser Console

1. Open the dashboard: `http://localhost:4200/dashboard`
2. Press **F12** (or **Cmd+Option+I** on Mac)
3. Go to **Console** tab
4. Click one of the test buttons
5. Look for errors

### Common Console Errors:

#### Error 1: CORS Error
```
Access to XMLHttpRequest at 'http://localhost:8000' from origin 'http://localhost:4200' has been blocked by CORS policy
```

**Fix:** Check backend CORS settings in `app.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://127.0.0.1:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### Error 2: 404 Not Found
```
POST http://localhost:8000/api/dashboard/test-query 404 (Not Found)
```

**Fix:** The endpoint doesn't exist. Make sure you saved `backend/app.py` with the new endpoints.

#### Error 3: Connection Refused
```
Failed to fetch
```

**Fix:** Backend is not running. Start it.

## Step 4: Check Network Tab

1. In DevTools, go to **Network** tab
2. Click a test button
3. Look for the POST request to `/api/dashboard/test-query`

**Check:**
- Does the request appear?
- What's the status code? (should be 200)
- What's the response?

## Step 5: Check Console Logs

After clicking a button, you should see:

```
✅ Metric widget generated: {id: "...", type: "metric", ...}
```

**If you see this but no widget appears:**
- The widget is being created but not displayed
- Check the template is correct

**If you DON'T see this:**
- Check for errors in console
- Widget generation failed

## Step 6: Check LocalStorage

In browser console, run:

```javascript
localStorage.getItem('third-eye-dashboard-widgets')
```

**If null:**
- No widgets have been saved
- Generation is failing

**If you see JSON:**
- Widgets are being saved
- Display issue in template

## Step 7: Manual Widget Test

In browser console, try creating a widget manually:

```javascript
// Get the component (this is a hack for testing)
const widget = {
  id: 'test-' + Date.now(),
  type: 'metric',
  title: 'Test Widget',
  description: 'Manual test',
  data: {
    value: 12345,
    label: 'Test Metric',
    type: 'integer'
  },
  metadata: {
    timestamp: new Date().toISOString()
  }
};

// Check localStorage
localStorage.setItem('third-eye-dashboard-widgets', JSON.stringify([widget]));

// Refresh the page
location.reload();
```

**If widget appears after refresh:**
- The service is working
- The API call is the problem

## Step 8: Check Template Rendering

Look at the page source. You should see:

```html
<!-- Test Dashboard Section (should always be visible) -->
<div class="test-dashboard-section">
  <h3>🧪 Test Dashboard Generation</h3>
  <button>Generate Metric</button>
  ...
</div>

<!-- This appears only when widgets exist -->
<div class="generated-dashboards-section" *ngIf="...">
```

## Quick Fix Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 4200
- [ ] No console errors
- [ ] API endpoints return 200 OK
- [ ] Network tab shows successful POST requests
- [ ] Console logs show "✅ widget generated"
- [ ] LocalStorage contains widgets
- [ ] Page is at `http://localhost:4200/dashboard`

## Common Solutions

### Solution 1: Restart Everything

```bash
# Kill all processes
pkill -f "python app.py"
pkill -f "ng serve"

# Start fresh
cd /Users/divyanshu.gaur/hackathon/third-eye-project
./start-both.sh
```

### Solution 2: Clear Browser Cache

1. Open DevTools (F12)
2. Right-click refresh button
3. Select "Empty Cache and Hard Reload"

### Solution 3: Check You're on Dashboard Page

Make sure you're at: `http://localhost:4200/dashboard`

NOT: `http://localhost:4200/` or other pages

### Solution 4: Verify Backend Endpoints Exist

```bash
grep -n "test-query" backend/app.py
```

Should show line numbers where endpoints are defined.

**If nothing found:** The endpoints weren't added. Check if `backend/app.py` was saved correctly.

## Advanced Debugging

### Enable Verbose Logging

Add this to the beginning of each test method:

```typescript
async testMetricWidget() {
  console.log('🔵 testMetricWidget called');
  console.log('🔵 API URL:', this.apiUrl);
  
  try {
    console.log('🔵 Making API call...');
    const result = await firstValueFrom(
      this.http.post<any>(`${this.apiUrl}/dashboard/test-query`, {})
    );
    console.log('🔵 API response:', result);
    
    console.log('🔵 Generating widget...');
    const widget = this.dashboardService.generateWidgetFromQueryResult(result);
    console.log('🔵 Generated widget:', widget);
    
    if (widget) {
      console.log('🔵 Adding widget to service...');
      this.dashboardService.addWidget(widget);
      console.log('🔵 Current widgets:', this.dashboardService.getWidgets());
    }
  } catch (error) {
    console.error('❌ Error:', error);
  }
}
```

### Check Service State

In console:

```javascript
// This won't work directly, but the service logs should show
// Check localStorage instead
JSON.parse(localStorage.getItem('third-eye-dashboard-widgets'))
```

## Still Not Working?

### Last Resort: Manual Endpoint Test

Create a simple HTML file to test the backend:

```html
<!DOCTYPE html>
<html>
<head><title>API Test</title></head>
<body>
  <button onclick="testAPI()">Test API</button>
  <pre id="result"></pre>
  
  <script>
    async function testAPI() {
      try {
        const response = await fetch('http://localhost:8000/api/dashboard/test-query', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: '{}'
        });
        const data = await response.json();
        document.getElementById('result').textContent = JSON.stringify(data, null, 2);
      } catch (error) {
        document.getElementById('result').textContent = 'Error: ' + error.message;
      }
    }
  </script>
</body>
</html>
```

Save as `test.html` and open in browser. If this works but Angular doesn't, it's an Angular/HTTP client issue.

## Contact Info

If none of these work, provide:
1. Browser console output (full)
2. Network tab screenshot
3. Backend terminal output
4. Result of `curl` commands above


