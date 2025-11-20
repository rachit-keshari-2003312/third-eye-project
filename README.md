# Third-Eye - Agentic AI Platform

![Third-Eye Logo](https://img.shields.io/badge/Third--Eye-Agentic%20AI%20Platform-blue?style=for-the-badge&logo=eye)

A professional Agentic AI platform built with Angular frontend and Python FastAPI backend, integrating Amazon Bedrock models and Model Context Protocol (MCP) servers for enhanced AI capabilities.

## 🌟 Features

### Core Functionality
- **🤖 AI Agent Management** - Create, configure, and deploy custom AI agents
- **☁️ Amazon Bedrock Integration** - Access Claude 3, Nova, and other foundation models
- **🔗 MCP Server Integration** - Connect to filesystem, database, web scraping, and more
- **💬 Real-time Conversations** - WebSocket-based chat with AI agents
- **📊 Analytics Dashboard** - Monitor usage, performance, and costs
- **🎨 Modern UI** - Beautiful gradient-based design with responsive layout

### Technical Stack
- **Frontend**: Angular 20 with TypeScript, SCSS, and modern UI components
- **Backend**: Python FastAPI with async support and WebSocket
- **AI Integration**: Amazon Bedrock, MCP Protocol, OpenAI-compatible APIs
- **Database**: SQLite/PostgreSQL support with SQLAlchemy
- **Real-time**: WebSocket connections for live updates
- **Security**: JWT authentication, API key management

## 🚀 Quick Start

### Prerequisites
- **Node.js** 18+ and npm
- **Python** 3.8+ and pip
- **Git** (for MCP git server)
- **AWS Account** (for Bedrock integration)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd third-eye-project
   ```

2. **Make startup scripts executable**
   ```bash
   chmod +x start-frontend.sh start-backend.sh
   ```

3. **Option A: Start both servers together (Recommended)**
   ```bash
   ./start-both.sh
   ```
   This will:
   - Start both backend and frontend servers
   - Handle port conflicts automatically
   - Open the application in your browser
   - Press Ctrl+C to stop both servers

4. **Option B: Start servers individually**
   
   **Backend server (in terminal 1):**
   ```bash
   ./start-backend.sh
   ```
   
   **Frontend server (in terminal 2):**
   ```bash
   ./start-frontend.sh
   ```

5. **Open the application**
   Navigate to http://localhost:4200 in your browser

## 📖 User Guide

### Getting Started

1. **Login**
   - Use any email address
   - Enter an API key (minimum 8 characters for demo)
   - The app will remember your session

2. **Dashboard**
   - View system overview and statistics
   - Monitor AI agent activity
   - Check MCP server connections
   - Access quick actions

3. **AI Agents**
   - Create new agents with custom capabilities
   - Configure MCP connections per agent
   - Deploy/stop agents as needed
   - Monitor agent performance

4. **Amazon Bedrock**
   - Configure AWS credentials
   - Select from available models (Claude 3, Nova, etc.)
   - Chat with foundation models
   - Monitor usage and costs

5. **Integrations**
   - Connect built-in MCP servers
   - Add custom MCP endpoints
   - Test server connections
   - Monitor server status

### MCP Servers Available

#### Built-in Servers
- **📁 Filesystem** - File operations (read, write, list)
- **🗄️ Database** - SQL queries and schema inspection
- **🌐 Web Scraper** - HTML parsing and data extraction
- **📝 Git** - Repository operations and version control
- **💬 Slack** - Workspace integration and messaging

#### Additional MCP Servers
- **🔍 Brave Search** - Web search capabilities
- **🐘 PostgreSQL** - Advanced database operations
- **📊 SQLite** - Lightweight database operations
- **🤖 Puppeteer** - Browser automation and scraping
- **📧 GitHub** - Repository management and automation
- **🧠 Memory** - Persistent knowledge storage
- **⏰ Time** - Date/time operations and formatting

### AWS Bedrock Configuration

1. **Get AWS Credentials**
   - AWS Access Key ID
   - AWS Secret Access Key
   - (Optional) Session Token for temporary credentials

2. **Configure in App**
   - Go to AWS Bedrock page
   - Enter your credentials
   - Select your preferred region
   - Click "Connect to Bedrock"

3. **Available Models**
   - **Claude 3 Sonnet** - Balanced performance for complex tasks
   - **Claude 3 Haiku** - Fast and cost-effective
   - **Amazon Nova Pro** - Multimodal capabilities
   - **Jamba Instruct** - Long context understanding

## 🔧 Development

### Project Structure
```
third-eye-project/
├── src/                          # Angular frontend source
│   ├── app/
│   │   ├── pages/               # Page components
│   │   ├── app.ts               # Main app component
│   │   └── app.routes.ts        # Routing configuration
│   └── styles.scss              # Global styles
├── backend/                      # Python FastAPI backend
│   ├── app.py                   # Main FastAPI application
│   └── requirements.txt         # Python dependencies
├── mcp.json                     # MCP server configuration
├── start-frontend.sh            # Frontend startup script
├── start-backend.sh             # Backend startup script
└── README.md                    # This file
```

### API Endpoints

#### Health & Status
- `GET /health` - Health check
- `GET /api/analytics/usage` - Usage statistics

#### MCP Integration
- `GET /api/mcp/servers` - List MCP servers
- `POST /api/mcp/servers/{id}/call` - Call MCP server method
- `POST /api/mcp/servers/{id}/toggle` - Toggle server status

#### Bedrock Integration
- `POST /api/bedrock/connect` - Connect to AWS Bedrock
- `POST /api/bedrock/invoke` - Invoke Bedrock model

#### Agent Management
- `GET /api/agents` - List agents
- `POST /api/agents` - Create new agent
- `DELETE /api/agents/{id}` - Delete agent

#### Conversations
- `GET /api/conversations` - List conversations
- `POST /api/conversations/{id}/messages` - Send message

#### WebSocket
- `WS /ws/{client_id}` - Real-time communication

### Environment Variables

Create a `.env` file in the project root:

```bash
# AWS Bedrock
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# MCP Server API Keys
BRAVE_API_KEY=your_brave_api_key
GITHUB_PERSONAL_ACCESS_TOKEN=your_github_token
SLACK_BOT_TOKEN=your_slack_token
OPENWEATHER_API_KEY=your_weather_api_key

# Database
POSTGRES_CONNECTION_STRING=postgresql://user:pass@localhost/db

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
```

## 🎨 UI Design

The application features a modern, professional design with:

- **Gradient Color Scheme**: Red, purple, and blue gradients throughout
- **Responsive Layout**: Works on desktop, tablet, and mobile
- **Animated Elements**: Smooth transitions and hover effects
- **Eye Animation**: Blinking Third-Eye logo for brand identity
- **Glass Morphism**: Backdrop blur effects for modern aesthetics
- **Dark/Light Support**: Adapts to system preferences

## 🔒 Security

- **API Key Authentication**: Simple but secure authentication system
- **CORS Protection**: Configured for development and production
- **Input Validation**: Pydantic models for request/response validation
- **Environment Variables**: Sensitive data stored in environment
- **Rate Limiting**: Built-in FastAPI rate limiting (configurable)

## 📊 Monitoring

The platform includes comprehensive monitoring:

- **Real-time Metrics**: Request counts, response times, error rates
- **Usage Analytics**: Token consumption, cost tracking, model usage
- **System Health**: MCP server status, database connections
- **Performance Charts**: Visual representation of system performance

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # The startup scripts handle this automatically, but if needed:
   lsof -ti:4200 | xargs kill -9  # Kill frontend
   lsof -ti:8000 | xargs kill -9  # Kill backend
   ```

2. **Frontend Won't Start**
   ```bash
   # Try manual startup:
   ng analytics disable
   ng serve --host 0.0.0.0 --port 4200
   ```

3. **Backend Dependencies Issues**
   ```bash
   # Recreate virtual environment
   rm -rf venv
   python3 -m venv venv
   source venv/bin/activate
   pip install fastapi uvicorn boto3 httpx python-multipart
   ```

4. **Angular Build Issues**
   ```bash
   # Clear npm cache and reinstall
   npm cache clean --force
   rm -rf node_modules package-lock.json
   npm install
   ```

5. **Node.js Version Warning**
   - The warning about Node.js v25.2.1 is safe to ignore for development
   - For production, consider using an LTS version (18.x or 20.x)

6. **MCP Server Connection Issues**
   - MCP servers are optional for basic functionality
   - The app works without them for demonstration purposes
   - Check server logs in the browser console for details

### Getting Help

- Check the [Issues](../../issues) page for known problems
- Create a new issue if you encounter a bug
- Join our [Discord](https://discord.gg/thirdeye) for community support

## 🙏 Acknowledgments

- **Angular Team** - For the amazing frontend framework
- **FastAPI** - For the high-performance Python API framework
- **Amazon Bedrock** - For providing access to foundation models
- **MCP Protocol** - For the standardized AI tool integration
- **Open Source Community** - For the countless libraries and tools

---

**Built with ❤️ by the Third-Eye Team**

*Empowering the future of Agentic AI*