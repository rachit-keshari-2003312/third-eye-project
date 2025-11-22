const express = require('express');
const cors = require('cors');
const axios = require('axios');

const app = express();
const PORT = 3001;

// Enable CORS for all origins
app.use(cors());
app.use(express.json());

// Proxy endpoint for analytics
app.post('/api/analytics/execute', async (req, res) => {
  try {
    console.log('Proxying analytics request:', req.body);
    
    const response = await axios.post(
      'https://mighty-bushes-unite.loca.lt/api/analytics/execute',
      req.body,
      {
        headers: {
          'Content-Type': 'application/json'
        },
        timeout: 30000
      }
    );
    
    console.log('Analytics response received');
    res.json(response.data);
    
  } catch (error) {
    console.error('Analytics proxy error:', error.message);
    res.status(500).json({ 
      error: 'Proxy error', 
      details: error.message 
    });
  }
});

// Note: Conversations will call external API directly
// Only Analytics uses proxy to avoid CORS

// Health check
app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    timestamp: new Date().toISOString(),
    proxy: 'running'
  });
});

app.listen(PORT, () => {
  console.log(`🔗 CORS Proxy Server running on http://localhost:${PORT}`);
  console.log(`📊 Analytics proxy: http://localhost:${PORT}/api/analytics/execute`);
  console.log(`💬 Conversations: Direct API calls (no proxy needed)`);
});
