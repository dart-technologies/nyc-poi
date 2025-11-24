# NYC POI Concierge - MCP Server

LastMile AI MCP server for intelligent NYC restaurant recommendations.

## 🛠️ Features
- **Geospatial Search**: Radius-based POI discovery with proximity scoring
- **Semantic Search**: Natural language vibe-based recommendations via vector search
- **Prestige Filtering**: Michelin stars, James Beard awards, best-of lists
- **Context Awareness**: Weather, time, and occasion-based recommendations
- **Live Enrichment**: Tavily integration for real-time trusted source validation

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
MONGODB_DATABASE=nyc-poi
MONGODB_POIS_COLLECTION=pois
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
OPENWEATHER_API_KEY=...
```

### 3. Run Server
```bash
# HTTP server (for mobile app)
python3 http_server.py

# MCP stdio server (for Claude/GPT)
python3 main.py
```

---

## 🎯 MCP Tools

### 1. query_pois
Search for POIs with geospatial and prestige filters.

**Parameters:**
- `latitude`, `longitude` (required): User location
- `radius_meters`: Search radius (default: 2000)
- `categories`: Filter by category (fine-dining, casual-dining, bars-cocktails)
- `michelin_stars`: Filter by Michelin stars [1, 2, 3]
- `min_prestige_score`: Minimum prestige score (0-150)
- `limit`: Max results (default: 10)

**Example:**
```json
{
  "latitude": 40.7580,
  "longitude": -73.9851,
  "radius_meters": 2000,
  "michelin_stars": [2, 3],
  "limit": 5
}
```

---

### 2. get_contextual_recommendations
Get personalized recommendations based on comprehensive context.

**Parameters:**
- `latitude`, `longitude` (required): User location
- `occasion`: date-night, business-dinner, celebration, etc.
- `weather`: sunny, rain, cold, snow
- `group_size`: Number of people (default: 2)
- `budget`: $, $$, $$$, $$$$
- `datetime`: ISO 8601 timestamp
- `limit`: Max results (default: 5)

**Example:**
```json
{
  "latitude": 40.7580,
  "longitude": -73.9851,
  "occasion": "date-night",
  "budget": "$$$",
  "weather": "rain",
  "group_size": 2
}
```

---

### 3. search_by_vibe ✨ **NEW**
Semantic search using natural language vibe descriptions.

**Parameters:**
- `vibe_query` (required): Natural language description
- `limit`: Max results (default: 10)
- `min_score`: Similarity threshold 0.0-1.0 (default: 0.7)
- `category`: Optional category filter

**Example Queries:**
```json
// Romantic ambiance
{
  "vibe_query": "romantic and quiet with amazing views",
  "limit": 5,
  "min_score": 0.7
}

// Celebration vibes
{
  "vibe_query": "lively spot for celebrating with friends",
  "category": "fine-dining"
}

// Comfort food
{
  "vibe_query": "cozy rainy day comfort food",
  "min_score": 0.65
}

// Instagram-worthy
{
  "vibe_query": "trendy instagram-worthy brunch spot"
}
```

**Response Format:**
```
🔮 Semantic Search Results

🎯 Vibe Query: "romantic and quiet with amazing views"
📊 Found 5 match(es) (min score: 0.7)

1. **Eleven Madison Park** ⭐⭐⭐
   📍 Flatiron District
   🎯 Similarity: 0.85 | Prestige: 150
   💰 $$$$ · contemporary american
   ✨ Ambiance: elegant, refined, sophisticated
   🎉 Best for: date-night, celebration
```

**Setup Requirements:**
1. Generate embeddings: `python3 scripts/data_pipeline/generate_embeddings.py`
2. Create Atlas Vector Search index (see `VECTOR_SEARCH_SETUP.md`)
3. Index must be named `vector_index` with 1536 dimensions (cosine similarity)

---

### 4. enrich_poi_live
Get real-time enrichment from Tavily trusted sources.

**Parameters:**
- `poi_name` (required): Restaurant name
- `poi_address` (required): Street address
- `category`: Type (default: "restaurant")

**Example:**
```json
{
  "poi_name": "Le Bernardin",
  "poi_address": "155 W 51st St",
  "category": "restaurant"
}
```

---

## 📚 HTTP API Endpoints

**Available at:** http://localhost:8000

- `POST /query-pois`: Geospatial search with filters
- `POST /recommendations`: Contextual suggestions
- `POST /search-by-vibe`: Semantic vibe search
- `GET /health`: Server health check

---

## 🧪 Testing

### Run All Tests
```bash
# MCP tool tests
python3 test_tools.py

# Integration tests
cd ../../tests/integration
python3 test_mcp_cloud.py
python3 test_search_by_vibe.py

# Vector search test
cd ../../scripts
python3 test_search_by_vibe.py
```

### Test Individual Tools
```bash
# Test semantic search
python3 scripts/test_search_by_vibe.py

# Verify fine dining data
python3 scripts/verification/check_fine_dining.py
```

---

## 📊 Data Statistics

- **POIs in Database:** 134
- **Michelin-Starred:** 50+
- **POIs with Embeddings:** 69
- **Embedding Model:** OpenAI text-embedding-3-small (1536-dim)
- **Vector Search:** MongoDB Atlas with cosine similarity

---

## 📖 Documentation

- `VECTOR_SEARCH_SETUP.md` - Vector search configuration guide
- `docs/INSPECTOR_GUIDE.md` - MCP Inspector usage
- `docs/TEST_RESULTS.md` - Test execution results
- `chatgpt_gpt/README.md` - ChatGPT custom GPT setup

---

## 🔧 Configuration

See `.env.template` for all available environment variables.

**Required:**
- MongoDB Atlas URI with geospatial index
- OpenAI API key (for embeddings)
- Tavily API key (for enrichment)
