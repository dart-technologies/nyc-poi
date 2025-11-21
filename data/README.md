# Data Directory

Store POI data at various stages of the pipeline.

## Structure

```
data/
├── raw/              # Tavily search results (JSON)
│   └── .gitkeep
├── processed/        # Enriched POI data ready for MongoDB
│   └── .gitkeep
└── cache/            # Temporary curation cache
    └── .gitkeep
```

## Usage

### Raw Data
Store Tavily API responses for reproducibility:
```
raw/
├── michelin_manhattan_2025.json
├── casual_dining_eater.json
└── cocktail_bars_timeout.json
```

### Processed Data
Normalized POI documents ready for MongoDB import:
```
processed/
├── pois_batch_1.json
├── pois_batch_2.json
└── pois_final_100.json
```

### Cache
Temporary files during curation (ignored by git):
```
cache/
├── venue_validation_cache.json
└── geocoding_cache.json
```

## Note
Large JSON files (>1MB) are gitignored. Keep sample/schema files only.
