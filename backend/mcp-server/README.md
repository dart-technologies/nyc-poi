# NYC POI Concierge - MCP Server

LastMile AI MCP server for intelligent NYC restaurant recommendations.

## 🛠️ Features
- **Geospatial Search**: Radius-based POI discovery
- **Prestige Filtering**: Michelin stars, James Beard awards
- **Context Awareness**: Weather, time, and occasion-based recommendations
- **Live Enrichment**: Tavily integration for real-time data

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd backend/mcp-server
pip install -r requirements.txt
```

### 2. Configure Environment
Create `.env` with:
```bash
MONGODB_URI=mongodb+srv://...
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
OPENWEATHER_API_KEY=...
```

### 3. Run Server
```bash
# Start HTTP server (for mobile app)
python3 http_server.py
```

## 📚 API Endpoints
- `POST /query-pois`: Search with filters
- `POST /recommendations`: Contextual suggestions
- `GET /health`: Server status

## 🧪 Testing
```bash
# Run verification script
python3 ../../scripts/verification/check_fine_dining.py
```
