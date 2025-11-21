# NYC POI Concierge - Backend (MCP Server)

LastMile AI MCP server for NYC restaurant recommendations with MongoDB + Tavily integration.

## Tech Stack
- **Framework:** LastMile AI MCP Agent (Python or TypeScript)
- **Database:** MongoDB Atlas
- **APIs:** Tavily (curation), OpenAI (embeddings)

## Structure
```
backend/
├── src/
│   ├── server.py          # Main MCP server entry point
│   ├── tools/             # MCP tool implementations
│   │   ├── query_pois.py
│   │   └── recommendations.py
│   ├── resources/         # MCP resources (deferred)
│   ├── prompts/           # MCP prompt templates (deferred)
│   ├── utils/             # Shared utilities
│   │   ├── mongodb.py
│   │   ├── tavily.py
│   │   ├── embeddings.py
│   │   └── context.py
│   └── config.py          # Configuration management
├── tests/                 # Unit tests
├── requirements.txt       # Python dependencies
├── pyproject.toml         # Python project config
└── .env.example           # Environment variables template
```

## Setup

### 1. Install Dependencies
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Run Server
```bash
python -m src.server
```

## MCP Tools (MVP)

### 1. query_pois
Geospatial search with prestige filtering.

**Parameters:**
- `location`: { latitude, longitude, radius_meters }
- `categories`: string[]
- `min_prestige_score`: number
- `michelin_stars`: number[]

### 2. get_contextual_recommendations
Context-aware recommendations based on location, time, weather, and occasion.

**Parameters:**
- `location`: { latitude, longitude }
- `datetime`: ISO string
- `occasion`: enum (date-night, business-dinner, casual, etc.)
- `weather`: enum (sunny, rain, snow, any)
- `group_size`: number

## Environment Variables
```
MONGODB_URI=mongodb+srv://...
MONGODB_DATABASE=nyc_poi_concierge
TAVILY_API_KEY=tvly-...
OPENAI_API_KEY=sk-...
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```
