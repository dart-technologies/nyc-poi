# Tavily POI Curation 🕵️‍♂️

AI-powered discovery of high-quality NYC restaurants.

## 🚀 Usage

### 1. Setup
```bash
cd scripts/tavily_curation
pip install -r requirements.txt
```

### 2. Run Curation
```bash
export TAVILY_API_KEY="your_key"
python poi_curator.py
```

## 📊 Output
- `data/raw/poi_candidates.json`: Raw candidates
- `data/raw/enriched_pois.json`: Validated POIs

## 🎯 Strategy
- **Michelin**: 3-star, 2-star, 1-star, Bib Gourmand
- **Casual**: Neighborhood gems, Eater essentials
- **Bars**: Craft cocktails, World's 50 Best

## 🏆 Scoring
Prestige score (0-150) based on:
- Michelin Stars (+50-100)
- James Beard (+40)
- NYT Stars (+40)
