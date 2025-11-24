# Scripts Directory 🛠️

Operational and utility scripts for the NYC POI Concierge.

## 📂 Structure

### `data_pipeline/`
- **`import_pois.py`**: Direct import to MongoDB
- **`import_discovered_pois.py`**: Import Tavily-discovered data

### `verification/`
- **`check_fine_dining.py`**: Verify Michelin/prestige data
- **`check_neighborhoods.py`**: Analyze neighborhood coverage
- **`check_data.py`**: General data inspection

### `maintenance/`
- **`fix_prestige_scores.py`**: Patch prestige scores for top venues

### `ops/`
- **`diagnose_mcp_mongo.py`**: Full system diagnostic tool
- **`check-backend-config.sh`**: Verify backend URL configuration
- **`get_ngrok_url.sh`**: Retrieve current ngrok tunnel URL

### `deployment/`
- **`deploy_to_cloud.sh`**: Deploy MCP server to cloud

### `dev/`
- **`start_local_server.sh`**: Start local development server

## 🚀 Usage
Run scripts from the project root:
```bash
python3 scripts/verification/check_fine_dining.py
```
