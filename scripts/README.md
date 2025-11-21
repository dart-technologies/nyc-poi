# Scripts Directory

Data processing and utility scripts for the hackathon.

## Scripts

### Curation
- **`curate_restaurants.py`** - Run Tavily searches and extract POIs
- **`enrich_pois.py`** - Enrich POIs with additional metadata
- **`validate_quality.py`** - Validate prestige markers

### MongoDB
- **`import_to_mongodb.py`** - Bulk import POIs to MongoDB Atlas
- **`create_indexes.py`** - Create geospatial and vector search indexes
- **`test_queries.py`** - Test MongoDB aggregation pipelines

### Embeddings
- **`generate_embeddings.py`** - Generate OpenAI embeddings for POIs
- **`batch_embed.py`** - Batch processing for cost efficiency

### Utilities
- **`geocode_addresses.py`** - Convert addresses to coordinates
- **`deduplicate_pois.py`** - Remove duplicate venues
- **`export_sample.py`** - Export sample data for testing

## Usage

```bash
# Example: Curate 30 Michelin restaurants
python scripts/curate_restaurants.py --category fine-dining --limit 30

# Example: Import to MongoDB
python scripts/import_to_mongodb.py --file data/processed/pois_final_100.json
```

## Note
Scripts are MVP-focused and may not have production-grade error handling.
