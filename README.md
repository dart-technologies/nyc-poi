# NYC POI Concierge 🗽

**Prestige-first, context-aware restaurant discovery for NYC.**
Built for the MongoDB x Tavily x LastMile AI Hackathon (Nov 2025).

## 🚀 Overview
A mobile concierge that moves beyond generic recommendations. We use **Tavily** to curate Michelin-starred and award-winning spots, **MongoDB Atlas** for geospatial + vector search, and **LastMile AI's MCP** to power a context-aware chat interface.

## 🎥 Demo Video
**Watch the full walkthrough:**  
[![NYC POI Concierge Demo](https://img.youtube.com/vi/zJF-ZN2inig/maxresdefault.jpg)](https://youtu.be/zJF-ZN2inig)

🔗 **[Watch on YouTube](https://youtu.be/zJF-ZN2inig)**

## 🛠️ Tech Stack
- **Database:** MongoDB Atlas (Geospatial + Vector Search)
- **AI/Search:** Tavily API (Real-time enrichment), OpenAI GPT-4o
- **Backend:** LastMile AI MCP Server (Python)
- **Frontend:** Expo React Native (iOS)

## 📂 Structure
- `backend/mcp-server/`: MCP server implementation
- `frontend/expo-app/`: React Native mobile app
- `scripts/`: Data pipelines, verification, and ops tools
- `data/`: Curated and raw POI datasets

## ⚡ Quick Start

### 1. Backend (Local)
```bash
cd backend/mcp-server
pip install -r requirements.txt
python3 http_server.py
# Runs on http://localhost:8000
```

### 2. Frontend (Mobile)
```bash
cd frontend/expo-app
npm install
npx expo start
# Press 'i' for iOS simulator
```

## ☁️ Deployment
- **MCP Cloud:** Deployed and accessible via MCP Client.
- **Data:** 130+ curated POIs in MongoDB Atlas.

## 🧪 Testing
Run the verification suite:
```bash
python3 scripts/verification/check_fine_dining.py
```
