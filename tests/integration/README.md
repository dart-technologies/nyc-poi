# Integration Tests 🧪

End-to-end test suite for the NYC POI Concierge API.

## 🚀 Quick Start

### 1. Run Tests
```bash
python3 tests/integration/test_api_integration.py
```

### 2. Options
- `--local`: Test `localhost:8000` (default)
- `--url <URL>`: Test custom endpoint

## 📋 Coverage
- ✅ **Health Check**: API & DB status
- ✅ **POI Queries**: Filters & search
- ✅ **Geospatial**: Radius & distance
- ✅ **Context**: Weather/Time logic
- ✅ **Performance**: Latency checks

## 🔧 Troubleshooting
- **Failures?** Ensure backend is running:
  ```bash
  python3 backend/mcp-server/http_server.py
  ```
- **Timeouts?** Check MongoDB connection.
