# Integration Tests 🧪

End-to-end test suite for the NYC POI Concierge API and MCP server.

## 🚀 Quick Start

### Run All Tests
```bash
# MCP Cloud deployment tests
python3 tests/integration/test_mcp_cloud.py

# API integration tests
python3 tests/integration/test_api_integration.py

# Vector search tests (requires vector index)
python3 tests/integration/test_search_by_vibe.py
```

### Environment Variables
```bash
# Test against MCP Cloud (default: localhost:8000)
export MCP_SERVER_URL="https://your-mcp-cloud-url.com"
python3 tests/integration/test_search_by_vibe.py
```

## 📋 Test Coverage

### MCP Cloud Tests (`test_mcp_cloud.py`)
- ✅ **Health Check**: Server status
- ✅ **Tools List**: MCP tool discovery
- ✅ **Query POIs**: Geospatial search
- ✅ **Contextual Recommendations**: Context-aware suggestions
- ✅ **Database Connectivity**: MongoDB integration

### API Integration Tests (`test_api_integration.py`)
- ✅ **Health Check**: API & DB status
- ✅ **POI Queries**: Filters & search
- ✅ **Geospatial**: Radius & distance
- ✅ **Context**: Weather/Time logic
- ✅ **Performance**: Latency checks

### Vector Search Tests (`test_search_by_vibe.py`) ✨ **NEW**
- ✅ **Basic Semantic Search**: Natural language vibe queries
- ✅ **Celebration Vibe**: Different query types
- ✅ **Category Filter**: Fine-dining filtering
- ✅ **Low Threshold**: Tuning similarity scores

## 🔧 Troubleshooting

### Test Failures
- **Ensure backend is running:**
  ```bash
  python3 backend/mcp-server/http_server.py
  ```
- **Check MongoDB connection** in `.env`
- **Verify vector index** for search_by_vibe tests

### Vector Search Tests Failing
1. Verify Atlas Vector Search index is created
2. Index name must be `vector_index`
3. Embeddings must be generated for POIs
4. See `backend/mcp-server/VECTOR_SEARCH_SETUP.md`
