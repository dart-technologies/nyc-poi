# Perplexity POI Enrichment 🧠

Production-quality POI dataset generation using Perplexity Sonar API.

## 🚀 Usage

### 1. Setup
```bash
export PERPLEXITY_API_KEY=pplx-...
```

### 2. Run Discovery
```bash
cd scripts/perplexity_bulk_enrichment
python3 production_poi_enrichment.py
```

### 3. Import to MongoDB
```bash
cd ../../
python3 scripts/data_pipeline/import_to_mongodb.py --source production
```

## 📊 Features
- **Real-time Data**: Fresh info from last 30 days
- **Contextual**: Morning, Afternoon, Evening slots
- **Neighborhoods**: 10 key Manhattan areas
- **Rich Metadata**: Hours, price, signature dishes

## 💰 Cost
~$5.00 per 1,000 searches (efficient batching).
