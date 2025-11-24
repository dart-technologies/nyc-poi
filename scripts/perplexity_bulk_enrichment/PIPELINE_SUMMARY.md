# Comprehensive NYC POI Pipeline - Execution Summary

## Overview
Building production-ready NYC POI dataset with Perplexity discovery + social enrichment

## Pipeline Strategy

### Phase 1: Best-of Lists Discovery (Perplexity)
Discover POIs from curated NYC "best of" categories:

| Category | Count | Time Context | Type |
|----------|-------|--------------|------|
| Best Bagels | 10 | Morning | Casual Dining |
| Best Pizza | 15 | Afternoon | Casual Dining |
| Best Rooftop Bars | 12 | Evening Casual | Bars/Cocktails |
| Best Speakeasies | 8 | Evening Casual | Bars/Cocktails |
| Must-Try Fine Dining | 15 | Evening Prestige | Fine Dining |
| **TOTAL** | **60** | Mixed | Mixed |

### Phase 2: Social Media Enrichment (Perplexity)
For each POI discovered:
- Query Perplexity for social media accounts
- Extract Instagram, Twitter/X, Yelp, Facebook, TikTok links
- Parse from both response content AND citations
- Store in `contact.social` field

## Data Structure

Each POI includes:
```json
{
  "name": "Ess-a-Bagel",
  "slug": "ess-a-bagel",
  "address": {
    "street": "324 1st Ave, New York, NY 10009",
    "city": "New York",
    "state": "NY",
    "borough": "Manhattan"
  },
  "contact": {
    "phone": "",
   "website": "",
    "social": {
      "instagram": "https://instagram.com/essabagel",
      "instagram_handle": "essabagel",
      "twitter": "https://twitter.com/essabagel",
      "yelp": "https://yelp.com/biz/ess-a-bagel-new-york"
    }
  },
  "experience": {
    "price_range": "$$",
    "signature_dishes": ["Classic, perfectly chewy bagels"],
    "ambiance": []
  },
  "best_for": {
    "time_of_day": ["morning"],
    "occasions": [],
    "weather": ["any"],
    "group_size": [2, 4]
  },
  "prestige": {
    "score": 0
  },
  "best_of_list": "best_bagel",
  "time_context": "morning",
  "category": "casual-dining",
  "enrichment_status": "complete"
}
```

## Budget

| Phase | Searches | Cost | Purpose |
|-------|----------|------|---------|
| Discovery (5 categories) | 5 | $0.03 | Best-of lists |
| Social Enrichment (~60 POIs) | 60 | $0.30 | Instagram, Twitter, Yelp |
| **TOTAL ESTIMATED** | **65** | **$0.33** | Full pipeline |
| Remaining Budget | 4,935 | $24.68 | Future expansion |

## Output Files

1. **discovered_pois_bestof.json** - Raw POIs from discovery
2. **final_enriched_pois.json** - POIs with social media enrichment
3. **pipeline_output.log** - Execution log

## Next Steps

1. ✅ Run comprehensive pipeline
2. Review `final_enriched_pois.json` quality
3. Import to MongoDB with social links
4. Test MCP `enrich_poi_live` tool  
5. Update mobile app to display social handles

## Advantages of This Approach

✅ **Comprehensive Coverage**: 60 POIs across all meal times and occasions  
✅ **Social Media Ready**: Instagram, Twitter, Yelp handles pre-populated  
✅ **Time Contextualized**: Morning bagels, afternoon pizza, evening dining  
✅ **Budget Efficient**: ~$0.33 for production dataset  
✅ **Quality Focused**: "Best of" lists ensure high-quality POIs  
✅ **Demo Ready**: Perfect for showing time-based recommendations  

## Use Cases Covered

**Morning (7-11am)**
- "Best bagel near Times Square for breakfast"
- Returns: Ess-a-Bagel, Liberty Bagels, Absolute Bagels...

**Afternoon (11am-3pm)**
- "Quick pizza slice near Midtown"
- Returns: Joe's Pizza, Prince Street Pizza, John's...

**Evening Casual (5-7pm)**
- "Rooftop bar for after-work drinks"
- Returns: 230 Fifth, Westlight, The Press Lounge...

**Evening Prestige (6-10pm)**
- "Michelin restaurant for date night"
- Returns: Le Bernardin, Eleven Madison Park, Per Se...
