# Data Directory 📊

POI data at various stages of the pipeline.

## 📂 Structure

### `curated/`
- **`curated_pois.json`**: High-quality, manually verified POIs (Production).

### `mock/`
- **`sample_pois.json`**: Small dataset for testing and development.

### `raw/`
- **`poi_candidates.json`**: Raw output from Tavily discovery.
- **`enriched_pois.json`**: Intermediate enriched data.

## 📝 Note
Use `curated/curated_pois.json` for the most reliable data during development.
