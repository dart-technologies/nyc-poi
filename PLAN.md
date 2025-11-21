# Project Plan: NYC POI Concierge System
**Hyperlocal Smart City Concierge with Tavily, MongoDB, LastMile AI & Expo**

## Executive Summary

**Hackathon MVP (Nov 21-24, 2025)**: This project creates an intelligent NYC restaurant recommendation system for the MongoDB x Tavily x LastMile AI hackathon. The MVP curates 100 high-quality Manhattan restaurants using Tavily's AI-powered search, stores enriched data in MongoDB Atlas with geospatial and vector search capabilities, exposes intelligence through a LastMile AI MCP server with 2 core tools, and delivers contextual recommendations via a mobile Expo app integrated with GPT-5.1.

**Core Value Proposition:** Move beyond generic recommendations to provide prestige-first, context-aware restaurant suggestions based on current location, time of day, weather conditions, and validated quality markers (Michelin stars, James Beard awards, "best of" list appearances).

**MVP Scope:**
- 100 curated Manhattan restaurants (fine dining, casual dining, bars)
- MongoDB Atlas with geospatial + vector search indexes
- 2 MCP tools: `query_pois` + `get_contextual_recommendations`
- Basic Expo mobile app with chat UI + map view
- Local demo deployment (no production infrastructure)

---

## System Architecture

### Component Overview

┌─────────────────────────────────────────────────────────────┐
│                    Mobile Layer (Expo)                       │
│  - React Native interface                                    │
│  - Location services & weather integration                   │
│  - GPT-5.1 conversational UI via MCP client                 │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│          LastMile AI MCP Server (Orchestration)              │
│  - Tools: query_pois, get_recommendations, search_by_vibe   │
│  - Resources: neighborhood_guides, category_taxonomies       │
│  - Prompts: contextual_recommendation_templates              │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ├─────────────────┬──────────────────────────┐
                 ▼                 ▼                          ▼
┌──────────────────────┐  ┌─────────────────┐  ┌────────────────────┐
│  MongoDB Atlas       │  │  Tavily API     │  │  Context Services  │
│  - POI documents     │  │  - Web search   │  │  - Weather API     │
│  - Vector embeddings │  │  - Curation     │  │  - Time logic      │
│  - Geospatial index  │  │  - Validation   │  │  - User prefs      │
└──────────────────────┘  └─────────────────┘  └────────────────────┘

---

## Phase 1: Data Curation with Tavily (Day 1-2)

### Objective
Build focused restaurant database (100 POIs, Manhattan only) with quality signals using Tavily's advanced search capabilities.

### 1.1 Category Taxonomy Design (MVP)

**Primary Categories (Restaurants Only):**
- **Fine Dining:** Michelin-starred, upscale special occasion (Target: 30 POIs)
- **Casual Dining:** Quality neighborhood spots, ethnic cuisine (Target: 50 POIs)
- **Bars & Cocktails:** Craft cocktail bars, wine bars, rooftop bars (Target: 20 POIs)

**Prestige Markers to Capture:**
- Michelin stars (1-3 stars, Bib Gourmand)
- James Beard Awards
- Celebrity chef/owner mentions
- "Best of NYC" list appearances (Eater, TimeOut, Infatuation, NYT)
- Notable clientele or endorsements
- Social media influence metrics
- Critical reviews and ratings

### 1.2 Tavily Curation Strategy (MVP Focus)

**Target: 100 Manhattan Restaurants in 2 Days**

**Search Pattern for MVP:**

# Priority 1: Michelin-starred restaurants (30 POIs)
tavily_queries = [
    {
        "query": "Michelin star restaurants Manhattan NYC 2025",
        "search_depth": "advanced",
        "topic": "general",
        "days": 90,  # Recent within 90 days
        "include_domains": [
            "guide.michelin.com",
            "ny.eater.com",
            "timeout.com",
            "nytimes.com"
        ],
        "include_answer": True,
        "include_raw_content": True,
        "max_results": 10
    },
    {
        "query": "James Beard Award winners NYC restaurants Manhattan",
        "search_depth": "advanced",
        "include_answer": True
    }
]

# Priority 2: Quality casual dining (50 POIs)
casual_queries = [
    {
        "query": "best restaurants Manhattan neighborhoods 2025 Eater essential",
        "search_depth": "basic",  # Speed over depth for MVP
        "include_domains": ["ny.eater.com", "timeout.com"],
        "max_results": 20
    }
]

# Priority 3: Notable bars (20 POIs)
bar_queries = [
    {
        "query": "best cocktail bars Manhattan NYC 2025",
        "search_depth": "basic",
        "max_results": 10
    }
]

**Multi-Source Validation Pattern:**

For each POI candidate, run multiple Tavily searches to cross-reference:

async def validate_poi_quality(venue_name, category):
    """
    Cross-reference venue across multiple sources
    """
    validation_searches = [
        f"{venue_name} NYC reviews Michelin",
        f"{venue_name} NYC best of lists",
        f"{venue_name} NYC celebrity mentions",
        f"{venue_name} NYC ratings awards"
    ]
    
    results = await tavily.search_async(validation_searches)
    
    # Extract quality signals
    quality_score = calculate_prestige_score(results)
    citations = extract_citations(results)
    
    return {
        "validated": quality_score > threshold,
        "prestige_markers": extract_markers(results),
        "source_citations": citations
    }

### 1.3 Data Extraction Pipeline

**Step 1: Initial Discovery (Day 1)**
- Run 10-15 Tavily searches focused on Manhattan restaurants
- Target Michelin Guide, James Beard, Eater essential lists
- Use `include_raw_content: True` to get full article text
- Goal: Extract 100 restaurant candidates

**Step 2: Entity Extraction**
import re
from typing import List, Dict

def extract_poi_from_tavily_content(tavily_result) -> List[Dict]:
    """
    Parse Tavily results for POI entities
    """
    pois = []
    
    # Use Tavily's answer field for structured data
    if tavily_result.get('answer'):
        pois.extend(parse_answer_for_venues(tavily_result['answer']))
    
    # Parse raw content for additional details
    for result in tavily_result.get('results', []):
        content = result.get('content', '')
        
        # Extract venue mentions with context
        venue_mentions = extract_venue_mentions(content)
        
        for venue in venue_mentions:
            poi = {
                "name": venue['name'],
                "category": infer_category(content, venue),
                "source_url": result['url'],
                "mention_context": venue['context'],
                "extracted_at": datetime.now()
            }
            pois.append(poi)
    
    return deduplicate_pois(pois)

**Step 3: Enrichment**
async def enrich_poi(poi_candidate):
    """
    Deep dive on each POI to extract prestige markers
    """
    venue_name = poi_candidate['name']
    
    # Targeted searches for specific attributes
    enrichment_queries = [
        f"{venue_name} NYC address phone hours",
        f"{venue_name} NYC Michelin stars rating",
        f"{venue_name} NYC chef owner background",
        f"{venue_name} NYC best dishes signature items",
        f"{venue_name} NYC dress code reservations"
    ]
    
    results = await tavily.search_async(
        enrichment_queries,
        search_depth="advanced",
        include_images=True  # Get venue photos
    )
    
    return {
        **poi_candidate,
        "address": extract_address(results),
        "phone": extract_phone(results),
        "hours": extract_hours(results),
        "michelin_stars": extract_michelin(results),
        "price_range": extract_price(results),
        "signature_dishes": extract_dishes(results),
        "ambiance": extract_ambiance(results),
        "chef_name": extract_chef(results),
        "awards": extract_awards(results),
        "best_for": extract_occasions(results),
        "images": extract_images(results)
    }

### 1.4 Prestige Scoring Algorithm

def calculate_prestige_score(enriched_poi) -> float:
    """
    Weighted scoring based on quality markers
    """
    score = 0.0
    
    # Michelin recognition (highest weight)
    michelin = enriched_poi.get('michelin_stars', 0)
    if michelin == 3:
        score += 100
    elif michelin == 2:
        score += 75
    elif michelin == 1:
        score += 50
    elif enriched_poi.get('michelin_bib_gourmand'):
        score += 30
    
    # James Beard Awards
    if enriched_poi.get('james_beard_award'):
        score += 40
    
    # "Best of" list appearances
    best_of_lists = enriched_poi.get('best_of_mentions', [])
    score += min(len(best_of_lists) * 5, 30)  # Cap at 30
    
    # Celebrity associations
    if enriched_poi.get('celebrity_chef'):
        score += 20
    if enriched_poi.get('celebrity_endorsements'):
        score += 10
    
    # Critical acclaim
    nyt_stars = enriched_poi.get('nyt_stars', 0)
    score += nyt_stars * 10
    
    # Recency bonus (rewards newer discoveries)
    if enriched_poi.get('opened_within_year'):
        score += 15
    
    return score

---

## Phase 2: MongoDB Atlas Storage (Day 2)

### Objective
Design schema and indexes for fast geospatial and semantic queries (vector search optional for MVP).

### 2.1 POI Document Schema

// pois collection
{
  _id: ObjectId("..."),
  
  // Basic Information
  name: "Le Bernardin",
  slug: "le-bernardin-midtown",
  category: "fine-dining",
  subcategories: ["french", "seafood", "special-occasion"],
  
  // Location Data (required for geospatial queries)
  location: {
    type: "Point",
    coordinates: [-73.9826, 40.7614]  // [longitude, latitude]
  },
  address: {
    street: "155 W 51st St",
    city: "New York",
    state: "NY",
    zip: "10019",
    neighborhood: "Midtown West",
    borough: "Manhattan"
  },
  
  // Prestige Markers
  prestige: {
    score: 125.5,  // From calculation algorithm
    michelin_stars: 3,
    michelin_since: 2005,
    james_beard_awards: ["Outstanding Restaurant 2023"],
    nyt_stars: 4,
    best_of_lists: [
      {
        source: "Eater NY",
        list: "Best Restaurants in NYC 2025",
        rank: 3,
        url: "https://..."
      },
      {
        source: "Michelin Guide",
        list: "Three Star Restaurants",
        year: 2025
      }
    ],
    celebrity_endorsements: [
      "Chef Eric Ripert (owner/chef)",
      "Featured on Chef's Table"
    ]
  },
  
  // Operational Details
  contact: {
    phone: "+1-212-554-1515",
    website: "https://le-bernardin.com",
    reservations_url: "https://resy.com/...",
    social: {
      instagram: "@lebernardinny"
    }
  },
  
  hours: {
    monday: { open: "12:00", close: "14:30", dinner: "17:00-22:00" },
    tuesday: { open: "12:00", close: "14:30", dinner: "17:00-22:00" },
    // ... other days
    sunday: { closed: true }
  },
  
  // Experience Details
  experience: {
    price_range: "$$$$",
    avg_meal_cost: 180,
    dress_code: "Business Casual",
    reservation_difficulty: "very-high",
    lead_time_days: 30,
    party_size_max: 8,
    accepts_walk_ins: false,
    noise_level: "quiet",
    ambiance: ["elegant", "romantic", "sophisticated"],
    signature_dishes: [
      "Tuna Carpaccio",
      "Barely Cooked Salmon",
      "Black Bass"
    ],
    dietary_accommodations: ["vegetarian", "gluten-free"]
  },
  
  // Context-Based Recommendations
  best_for: {
    occasions: ["date-night", "special-occasion", "business-dinner"],
    time_of_day: ["lunch", "dinner"],
    weather: ["any"],  // Indoor, weather-independent
    group_size: [2, 4],
    seasons: ["any"]
  },
  
  // Vector Embeddings for Semantic Search
  embedding: [0.023, -0.154, 0.087, ...],  // 1536-dim vector
  embedding_text: "Three Michelin star French seafood restaurant...",
  
  // Source Attribution
  sources: [
    {
      type: "tavily_search",
      query: "Michelin star restaurants Manhattan",
      url: "https://guide.michelin.com/...",
      retrieved_at: ISODate("2025-11-20T12:00:00Z")
    },
    {
      type: "tavily_enrichment",
      url: "https://ny.eater.com/...",
      retrieved_at: ISODate("2025-11-20T12:05:00Z")
    }
  ],
  
  // Metadata
  created_at: ISODate("2025-11-20T12:00:00Z"),
  updated_at: ISODate("2025-11-20T12:00:00Z"),
  last_validated: ISODate("2025-11-20T12:00:00Z"),
  validation_status: "verified",
  data_quality_score: 0.95
}

### 2.2 Index Strategy

// 1. Geospatial Index (required for location queries)
db.pois.createIndex(
  { location: "2dsphere" },
  { name: "location_2dsphere" }
);

// 2. Vector Search Index (for semantic similarity)
// Created via Atlas UI or API
{
  "name": "poi_semantic_search",
  "type": "vectorSearch",
  "definition": {
    "fields": [
      {
        "type": "vector",
        "path": "embedding",
        "numDimensions": 1536,
        "similarity": "cosine"
      },
      {
        "type": "filter",
        "path": "category"
      },
      {
        "type": "filter",
        "path": "address.borough"
      },
      {
        "type": "filter",
        "path": "prestige.michelin_stars"
      }
    ]
  }
}

// 3. Category and Borough Index
db.pois.createIndex(
  { category: 1, "address.borough": 1, "prestige.score": -1 },
  { name: "category_borough_prestige" }
);

// 4. Text Search Index (for name/description search)
db.pois.createIndex(
  { name: "text", "experience.signature_dishes": "text" },
  { name: "text_search" }
);

// 5. Prestige Score Index
db.pois.createIndex(
  { "prestige.score": -1 },
  { name: "prestige_ranking" }
);

// 6. Time-Based Operational Index
db.pois.createIndex(
  { "hours.monday.open": 1, "hours.monday.close": 1 },
  { name: "hours_monday" }
);
// Repeat for each day of week

### 2.3 Sample Queries

**Query 1: Find Michelin-Starred Restaurants Near User**

db.pois.aggregate([
  {
    $geoNear: {
      near: {
        type: "Point",
        coordinates: [-73.9851, 40.7580]  // User's location (Times Square)
      },
      distanceField: "distance",
      maxDistance: 2000,  // 2km radius
      spherical: true,
      query: {
        category: "fine-dining",
        "prestige.michelin_stars": { $gte: 1 }
      }
    }
  },
  {
    $match: {
      "hours.thursday.open": { $lte: "19:00" },  // Open by 7 PM
      "hours.thursday.close": { $gte: "21:00" }  // Still serving at 9 PM
    }
  },
  {
    $project: {
      name: 1,
      distance: 1,
      "address.street": 1,
      "prestige.michelin_stars": 1,
      "prestige.score": 1,
      "experience.price_range": 1,
      "contact.phone": 1
    }
  },
  {
    $sort: { "prestige.score": -1, distance: 1 }
  },
  {
    $limit: 10
  }
]);

**Query 2: Semantic Search with Geospatial Filter**

db.pois.aggregate([
  {
    $vectorSearch: {
      index: "poi_semantic_search",
      path: "embedding",
      queryVector: [0.012, -0.203, ...],  // User query embedding
      numCandidates: 200,
      limit: 20,
      filter: {
        $and: [
          { category: { $in: ["fine-dining", "casual-dining"] } },
          { "address.borough": "Manhattan" },
          { "prestige.score": { $gte: 50 } }
        ]
      }
    }
  },
  {
    $addFields: {
      semanticScore: { $meta: "vectorSearchScore" }
    }
  },
  {
    $geoNear: {
      near: {
        type: "Point",
        coordinates: [-73.9851, 40.7580]
      },
      distanceField: "distance",
      maxDistance: 5000,  // 5km
      spherical: true
    }
  },
  {
    $addFields: {
      combinedScore: {
        $add: [
          { $multiply: ["$semanticScore", 0.6] },
          { $multiply: [{ $divide: [5000, "$distance"] }, 0.2] },
          { $multiply: ["$prestige.score", 0.002] }  // Normalize prestige
        ]
      }
    }
  },
  {
    $sort: { combinedScore: -1 }
  },
  {
    $limit: 10
  }
]);

**Query 3: Context-Aware Recommendations**

function getContextualRecommendations(context) {
  const { location, time, weather, occasion, groupSize } = context;
  
  // Build dynamic query based on context
  const pipeline = [
    {
      $geoNear: {
        near: { type: "Point", coordinates: location },
        distanceField: "distance",
        maxDistance: 3000,
        spherical: true
      }
    },
    {
      $match: {
        "best_for.occasions": occasion,
        "best_for.group_size": { $in: [groupSize] },
        // Weather filtering
        ...(weather === "rain" && {
          "best_for.weather": { $in: ["any", "rain"] }
        }),
        // Time filtering (assuming dinner at 19:00)
        [`hours.${time.day}.open`]: { $lte: time.hour },
        [`hours.${time.day}.close`]: { $gte: time.hour }
      }
    },
    {
      $addFields: {
        relevanceScore: {
          $add: [
            { $multiply: ["$prestige.score", 0.5] },
            { $multiply: [{ $divide: [3000, "$distance"] }, 0.3] },
            { $multiply: [
              { $size: {
                $setIntersection: [
                  "$best_for.occasions",
                  [occasion]
                ]
              }},
              20  // Bonus for occasion match
            ]}
          ]
        }
      }
    },
    {
      $sort: { relevanceScore: -1 }
    },
    {
      $limit: 10
    }
  ];
  
  return db.pois.aggregate(pipeline);
}

---

## Phase 3: LastMile AI MCP Server (Day 2-3)

### Objective
Build MCP server with 2 core tools exposing restaurant intelligence to GPT-5.1 via standardized protocol.

**MVP Tools:**
1. `query_pois` - Geospatial search with prestige filtering
2. `get_contextual_recommendations` - Context-aware recommendations (location, time, weather, occasion)

**Deferred for Post-Hackathon:**
- `search_by_vibe` (semantic/vector search)
- `enrich_poi_live` (real-time Tavily enrichment)
- MCP Resources (neighborhood guides, category taxonomies)
- MCP Prompts (date night, business dinner templates)

### 3.1 MCP Server Architecture

**File Structure:**
nyc-poi-concierge-mcp/
├── src/
│   ├── server.py              # Main MCP server
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── query_pois.py      # POI search tools
│   │   ├── recommendations.py # Context-aware rec tools
│   │   └── enrichment.py      # Real-time Tavily enrichment
│   ├── resources/
│   │   ├── __init__.py
│   │   ├── neighborhoods.py   # Neighborhood guides
│   │   └── categories.py      # Category taxonomies
│   ├── prompts/
│   │   ├── __init__.py
│   │   └── templates.py       # Recommendation prompts
│   ├── utils/
│   │   ├── mongodb.py         # MongoDB connection
│   │   ├── tavily.py          # Tavily client
│   │   ├── embeddings.py      # OpenAI embeddings
│   │   └── context.py         # Context processing
│   └── config.py
├── pyproject.toml
├── README.md
└── .env.example

### 3.2 MCP Tools Definition

**Tool 1: query_pois**

from mcp_agent import Tool
from typing import List, Dict, Optional
import asyncio

@Tool(
    name="query_pois",
    description="""
    Search for NYC points of interest with advanced filtering.
    Supports geospatial, categorical, and prestige-based queries.
    """,
    input_schema={
        "type": "object",
        "properties": {
            "location": {
                "type": "object",
                "properties": {
                    "latitude": {"type": "number"},
                    "longitude": {"type": "number"},
                    "radius_meters": {"type": "number", "default": 2000}
                },
                "required": ["latitude", "longitude"]
            },
            "categories": {
                "type": "array",
                "items": {"type": "string"},
                "description": "POI categories to filter by"
            },
            "min_prestige_score": {
                "type": "number",
                "description": "Minimum prestige score (0-150)",
                "default": 0
            },
            "michelin_stars": {
                "type": "array",
                "items": {"type": "integer"},
                "description": "Filter by Michelin stars [1, 2, 3]"
            },
            "limit": {
                "type": "integer",
                "default": 10
            }
        },
        "required": ["location"]
    }
)
async def query_pois(
    location: Dict,
    categories: Optional[List[str]] = None,
    min_prestige_score: float = 0,
    michelin_stars: Optional[List[int]] = None,
    limit: int = 10
) -> List[Dict]:
    """
    Query POIs from MongoDB with filters
    """
    from .utils.mongodb import get_db
    
    db = get_db()
    
    # Build aggregation pipeline
    pipeline = [
        {
            "$geoNear": {
                "near": {
                    "type": "Point",
                    "coordinates": [location["longitude"], location["latitude"]]
                },
                "distanceField": "distance",
                "maxDistance": location.get("radius_meters", 2000),
                "spherical": True
            }
        }
    ]
    
    # Add filters
    match_conditions = {"prestige.score": {"$gte": min_prestige_score}}
    
    if categories:
        match_conditions["category"] = {"$in": categories}
    
    if michelin_stars:
        match_conditions["prestige.michelin_stars"] = {"$in": michelin_stars}
    
    if match_conditions:
        pipeline.append({"$match": match_conditions})
    
    # Sort and limit
    pipeline.extend([
        {"$sort": {"prestige.score": -1, "distance": 1}},
        {"$limit": limit},
        {
            "$project": {
                "name": 1,
                "category": 1,
                "distance": 1,
                "address": 1,
                "prestige": 1,
                "experience.price_range": 1,
                "experience.signature_dishes": 1,
                "contact": 1
            }
        }
    ])
    
    results = list(db.pois.aggregate(pipeline))
    
    # Format for readability
    return [format_poi_result(poi) for poi in results]


def format_poi_result(poi: Dict) -> Dict:
    """Format POI for MCP response"""
    return {
        "name": poi["name"],
        "category": poi["category"],
        "distance_meters": round(poi["distance"], 0),
        "address": f"{poi['address']['street']}, {poi['address']['neighborhood']}",
        "prestige": {
            "score": poi["prestige"]["score"],
            "michelin_stars": poi["prestige"].get("michelin_stars"),
            "awards": poi["prestige"].get("best_of_lists", [])[:3]  # Top 3
        },
        "price": poi["experience"]["price_range"],
        "signature_dishes": poi["experience"].get("signature_dishes", [])[:3],
        "phone": poi["contact"].get("phone"),
        "reservations": poi["contact"].get("reservations_url")
    }

**Tool 2: get_contextual_recommendations**

@Tool(
    name="get_contextual_recommendations",
    description="""
    Get personalized POI recommendations based on current context:
    location, time, weather, occasion, and group size.
    Uses hybrid ranking combining prestige, proximity, and contextual fit.
    """,
    input_schema={
        "type": "object",
        "properties": {
            "location": {
                "type": "object",
                "properties": {
                    "latitude": {"type": "number"},
                    "longitude": {"type": "number"}
                },
                "required": ["latitude", "longitude"]
            },
            "datetime": {
                "type": "string",
                "format": "date-time",
                "description": "ISO 8601 datetime for recommendation"
            },
            "weather": {
                "type": "string",
                "enum": ["sunny", "rain", "snow", "any"],
                "default": "any"
            },
            "occasion": {
                "type": "string",
                "enum": [
                    "date-night", "business-dinner", "casual",
                    "special-occasion", "quick-bite", "drinks"
                ]
            },
            "group_size": {
                "type": "integer",
                "minimum": 1,
                "maximum": 20
            },
            "price_preference": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": ["$", "$$", "$$$", "$$$$"]
                }
            },
            "limit": {"type": "integer", "default": 5}
        },
        "required": ["location", "datetime", "occasion"]
    }
)
async def get_contextual_recommendations(
    location: Dict,
    datetime: str,
    occasion: str,
    weather: str = "any",
    group_size: int = 2,
    price_preference: Optional[List[str]] = None,
    limit: int = 5
) -> List[Dict]:
    """
    Generate context-aware recommendations
    """
    from .utils.mongodb import get_db
    from .utils.context import parse_datetime, get_day_of_week, get_time_category
    import datetime as dt
    
    db = get_db()
    
    # Parse context
    dt_obj = parse_datetime(datetime)
    day_of_week = get_day_of_week(dt_obj)
    time_category = get_time_category(dt_obj.hour)
    hour_str = dt_obj.strftime("%H:%M")
    
    # Build context-aware query
    pipeline = [
        {
            "$geoNear": {
                "near": {
                    "type": "Point",
                    "coordinates": [location["longitude"], location["latitude"]]
                },
                "distanceField": "distance",
                "maxDistance": 3000,  # 3km for contextual search
                "spherical": True
            }
        },
        {
            "$match": {
                "best_for.occasions": occasion,
                f"hours.{day_of_week}.open": {"$lte": hour_str},
                f"hours.{day_of_week}.close": {"$gte": hour_str},
                "best_for.weather": {"$in": [weather, "any"]},
                "experience.party_size_max": {"$gte": group_size}
            }
        }
    ]
    
    # Add price filter if specified
    if price_preference:
        pipeline.append({
            "$match": {
                "experience.price_range": {"$in": price_preference}
            }
        })
    
    # Calculate contextual relevance score
    pipeline.extend([
        {
            "$addFields": {
                "relevance_score": {
                    "$add": [
                        # Prestige weight (50%)
                        {"$multiply": ["$prestige.score", 0.5]},
                        
                        # Proximity weight (30%)
                        {"$multiply": [
                            {"$divide": [3000, "$distance"]},
                            30
                        ]},
                        
                        # Occasion match bonus (20%)
                        {"$multiply": [
                            {"$size": {
                                "$setIntersection": [
                                    "$best_for.occasions",
                                    [occasion]
                                ]
                            }},
                            20
                        ]},
                        
                        # Group size optimization bonus
                        {"$cond": [
                            {"$and": [
                                {"$gte": ["$experience.party_size_max", group_size]},
                                {"$lte": ["$experience.party_size_max", group_size + 4]}
                            ]},
                            10,
                            0
                        ]}
                    ]
                }
            }
        },
        {
            "$sort": {"relevance_score": -1}
        },
        {
            "$limit": limit
        }
    ])
    
    results = list(db.pois.aggregate(pipeline))
    
    return [format_contextual_result(poi, dt_obj, occasion) for poi in results]


def format_contextual_result(poi: Dict, datetime: dt.datetime, occasion: str) -> Dict:
    """Format contextual recommendation with explanation"""
    return {
        **format_poi_result(poi),
        "relevance_score": round(poi["relevance_score"], 2),
        "why_recommended": generate_recommendation_reason(poi, occasion),
        "estimated_wait": estimate_wait_time(poi, datetime),
        "reservation_recommendation": get_reservation_advice(poi, datetime)
    }


def generate_recommendation_reason(poi: Dict, occasion: str) -> str:
    """Generate human-readable reason for recommendation"""
    reasons = []
    
    # Prestige
    michelin = poi["prestige"].get("michelin_stars")
    if michelin:
        reasons.append(f"{michelin} Michelin star{'s' if michelin > 1 else ''}")
    
    # Best for occasion
    if occasion in poi.get("best_for", {}).get("occasions", []):
        occasion_map = {
            "date-night": "Perfect for romantic dinners",
            "business-dinner": "Ideal for business meetings",
            "special-occasion": "Great for celebrations"
        }
        reasons.append(occasion_map.get(occasion, f"Recommended for {occasion}"))
    
    # Proximity
    distance = poi["distance"]
    if distance < 500:
        reasons.append(f"Only {int(distance)}m away")
    
    # Signature items
    dishes = poi.get("experience", {}).get("signature_dishes", [])
    if dishes:
        reasons.append(f"Known for {dishes[0]}")
    
    return " • ".join(reasons)

**Tool 3: search_by_vibe**

@Tool(
    name="search_by_vibe",
    description="""
    Semantic search for POIs based on natural language descriptions.
    Example: "romantic Italian spot with outdoor seating" or
    "trendy cocktail bar with live jazz"
    """,
    input_schema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Natural language description of desired vibe"
            },
            "location": {
                "type": "object",
                "properties": {
                    "latitude": {"type": "number"},
                    "longitude": {"type": "number"},
                    "radius_meters": {"type": "number", "default": 5000}
                }
            },
            "limit": {"type": "integer", "default": 5}
        },
        "required": ["query"]
    }
)
async def search_by_vibe(
    query: str,
    location: Optional[Dict] = None,
    limit: int = 5
) -> List[Dict]:
    """
    Semantic search using OpenAI embeddings + MongoDB vector search
    """
    from .utils.embeddings import get_embedding
    from .utils.mongodb import get_db
    
    # Generate embedding for user query
    query_embedding = await get_embedding(query)
    
    db = get_db()
    
    # Vector search pipeline
    pipeline = [
        {
            "$vectorSearch": {
                "index": "poi_semantic_search",
                "path": "embedding",
                "queryVector": query_embedding,
                "numCandidates": 100,
                "limit": limit * 2  # Get more candidates for filtering
            }
        },
        {
            "$addFields": {
                "semantic_score": {"$meta": "vectorSearchScore"}
            }
        }
    ]
    
    # Add geospatial filter if location provided
    if location:
        pipeline.append({
            "$geoNear": {
                "near": {
                    "type": "Point",
                    "coordinates": [location["longitude"], location["latitude"]]
                },
                "distanceField": "distance",
                "maxDistance": location.get("radius_meters", 5000),
                "spherical": True
            }
        })
        
        # Combine semantic and proximity scores
        pipeline.append({
            "$addFields": {
                "combined_score": {
                    "$add": [
                        {"$multiply": ["$semantic_score", 0.7]},
                        {"$multiply": [
                            {"$divide": [
                                location.get("radius_meters", 5000),
                                "$distance"
                            ]},
                            0.3
                        ]}
                    ]
                }
            }
        })
        pipeline.append({"$sort": {"combined_score": -1}})
    else:
        pipeline.append({"$sort": {"semantic_score": -1}})
    
    pipeline.append({"$limit": limit})
    
    results = list(db.pois.aggregate(pipeline))
    
    return [format_semantic_result(poi, query) for poi in results]


def format_semantic_result(poi: Dict, query: str) -> Dict:
    """Format semantic search result"""
    return {
        **format_poi_result(poi),
        "match_score": round(poi.get("semantic_score", poi.get("combined_score", 0)), 3),
        "vibe_match": extract_matching_attributes(poi, query)
    }

**Tool 4: real_time_enrichment**

@Tool(
    name="enrich_poi_live",
    description="""
    Get real-time updates about a POI using Tavily search.
    Useful for checking current status, recent reviews, or events.
    """,
    input_schema={
        "type": "object",
        "properties": {
            "poi_name": {"type": "string"},
            "info_type": {
                "type": "string",
                "enum": ["current-status", "recent-reviews", "upcoming-events", "menu-updates"]
            }
        },
        "required": ["poi_name", "info_type"]
    }
)
async def enrich_poi_live(poi_name: str, info_type: str) -> Dict:
    """
    Use Tavily to fetch real-time information about POI
    """
    from .utils.tavily import get_tavily_client
    
    tavily = get_tavily_client()
    
    # Craft targeted search query
    query_templates = {
        "current-status": f"{poi_name} NYC open now status today",
        "recent-reviews": f"{poi_name} NYC reviews 2025",
        "upcoming-events": f"{poi_name} NYC events special menu",
        "menu-updates": f"{poi_name} NYC new menu items seasonal"
    }
    
    query = query_templates[info_type]
    
    # Execute Tavily search with recent results
    result = await tavily.search(
        query=query,
        search_depth="advanced",
        days=30,  # Last 30 days only
        include_answer=True,
        include_domains=[
            "timeout.com",
            "ny.eater.com",
            "infatuation.com",
            "google.com/maps"
        ]
    )
    
    return {
        "poi_name": poi_name,
        "info_type": info_type,
        "summary": result.get("answer", "No recent information found"),
        "sources": [
            {
                "title": r["title"],
                "url": r["url"],
                "snippet": r["content"][:200]
            }
            for r in result.get("results", [])[:3]
        ],
        "last_updated": datetime.now().isoformat()
    }

### 3.3 MCP Resources

from mcp_agent import Resource

@Resource(
    name="neighborhood_guides",
    description="Comprehensive guides for NYC neighborhoods with POI highlights",
    mime_type="application/json"
)
async def get_neighborhood_guides() -> Dict:
    """
    Provide pre-computed neighborhood summaries
    """
    from .utils.mongodb import get_db
    
    db = get_db()
    
    neighborhoods = db.pois.distinct("address.neighborhood")
    
    guides = {}
    for neighborhood in neighborhoods:
        # Aggregate top POIs by category
        summary = db.pois.aggregate([
            {"$match": {"address.neighborhood": neighborhood}},
            {"$group": {
                "_id": "$category",
                "count": {"$sum": 1},
                "avg_prestige": {"$avg": "$prestige.score"},
                "top_pois": {
                    "$push": {
                        "name": "$name",
                        "prestige": "$prestige.score"
                    }
                }
            }},
            {"$sort": {"avg_prestige": -1}}
        ])
        
        guides[neighborhood] = list(summary)
    
    return guides


@Resource(
    name="category_taxonomy",
    description="Complete POI category hierarchy with descriptions",
    mime_type="application/json"
)
async def get_category_taxonomy() -> Dict:
    """
    Provide category structure for understanding POI types
    """
    return {
        "dining": {
            "description": "Food and beverage establishments",
            "subcategories": {
                "fine-dining": {
                    "description": "Upscale restaurants, often with Michelin recognition",
                    "typical_price": "$$$$",
                    "examples": ["Le Bernardin", "Eleven Madison Park"]
                },
                "casual-dining": {
                    "description": "Relaxed atmosphere, quality food",
                    "typical_price": "$$-$$$"
                },
                # ... more subcategories
            }
        },
        # ... more categories
    }

### 3.4 MCP Prompts

from mcp_agent import Prompt

@Prompt(
    name="date_night_recommendation",
    description="Generate romantic dinner recommendations based on context"
)
async def date_night_prompt(location: Dict, datetime: str, budget: str) -> str:
    """
    Template for date night recommendations
    """
    return f"""
You are helping plan a romantic date night in NYC.

Context:
- Location: {location['latitude']}, {location['longitude']}
- Date/Time: {datetime}
- Budget: {budget}

Please use the get_contextual_recommendations tool with:
- occasion: "date-night"
- Current location and time
- Filter for romantic ambiance

Then format recommendations highlighting:
1. Romantic atmosphere details
2. Signature dishes perfect for sharing
3. Reservation requirements
4. Nearby options for drinks after dinner

Focus on creating a memorable experience within budget.
"""


@Prompt(
    name="business_dinner",
    description="Find appropriate venues for professional dining"
)
async def business_dinner_prompt(location: Dict, datetime: str, group_size: int) -> str:
    """
    Template for business dinner planning
    """
    return f"""
You are helping arrange a business dinner in NYC.

Context:
- Location: {location['latitude']}, {location['longitude']}
- Date/Time: {datetime}
- Party Size: {group_size}

Use get_contextual_recommendations with:
- occasion: "business-dinner"
- Consider noise levels (prefer "quiet" or "moderate")
- Private dining availability for groups > 6

Highlight:
1. Professional atmosphere
2. Reservation lead time
3. Menu options suitable for dietary restrictions
4. Proximity to common business districts
"""

### 3.5 Main MCP Server Implementation

# src/server.py
import asyncio
from mcp_agent import MCPAgent
from mcp.server.stdio import stdio_server

from .tools.query_pois import query_pois
from .tools.recommendations import (
    get_contextual_recommendations,
    search_by_vibe
)
from .tools.enrichment import enrich_poi_live
from .resources.neighborhoods import get_neighborhood_guides
from .resources.categories import get_category_taxonomy
from .prompts.templates import date_night_prompt, business_dinner_prompt
from .utils.mongodb import init_mongodb
from .utils.tavily import init_tavily

# Initialize agent
agent = MCPAgent(
    name="nyc-poi-concierge",
    version="1.0.0",
    description="NYC Points of Interest Concierge with prestige curation"
)

# Register tools
agent.add_tool(query_pois)
agent.add_tool(get_contextual_recommendations)
agent.add_tool(search_by_vibe)
agent.add_tool(enrich_poi_live)

# Register resources
agent.add_resource(get_neighborhood_guides)
agent.add_resource(get_category_taxonomy)

# Register prompts
agent.add_prompt(date_night_prompt)
agent.add_prompt(business_dinner_prompt)


async def main():
    """Run MCP server"""
    # Initialize connections
    await init_mongodb()
    await init_tavily()
    
    # Start server
    async with stdio_server() as (read_stream, write_stream):
        await agent.run(read_stream, write_stream)


if __name__ == "__main__":
    asyncio.run(main())

### 3.6 Configuration

# src/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # MongoDB
    mongodb_uri: str
    mongodb_database: str = "nyc_poi_concierge"
    
    # Tavily
    tavily_api_key: str
    
    # OpenAI (for embeddings)
    openai_api_key: str
    openai_embedding_model: str = "text-embedding-3-small"
    
    # Server
    mcp_server_name: str = "nyc-poi-concierge"
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"

settings = Settings()

---

## Phase 4: Expo Mobile App Integration (Day 3-4)

### Objective
Build basic React Native mobile app with GPT-5.1 chat interface and map view.

**MVP Features:**
- Chat UI with GPT-5.1 + MCP integration
- Location services (expo-location)
- Basic weather context (OpenWeatherMap)
- POI cards with prestige badges (Michelin stars)
- Simple map view with POI markers

**Deferred Features:**
- Favorites/saved venues
- User profile/preferences
- Advanced filtering UI
- Reservation integration
- Push notifications

### 4.1 App Architecture

expo-nyc-concierge/
├── app/
│   ├── (tabs)/
│   │   ├── index.tsx          # Home/Chat screen
│   │   ├── discover.tsx       # Browse POIs
│   │   ├── favorites.tsx      # Saved venues
│   │   └── profile.tsx        # User preferences
│   ├── poi/
│   │   └── [id].tsx           # POI detail screen
│   └── _layout.tsx
├── components/
│   ├── Chat/
│   │   ├── MessageBubble.tsx
│   │   ├── ChatInput.tsx
│   │   └── POICard.tsx        # Inline POI display
│   ├── Map/
│   │   ├── MapView.tsx
│   │   └── POIMarker.tsx
│   └── POI/
│       ├── POIList.tsx
│       ├── POIDetail.tsx
│       └── PrestigeBadge.tsx
├── services/
│   ├── mcp-client.ts          # MCP client implementation
│   ├── gpt.ts                 # GPT-5.1 integration
│   ├── location.ts            # Location services
│   └── weather.ts             # Weather API
├── hooks/
│   ├── useLocation.ts
│   ├── useWeather.ts
│   └── useMCP.ts
├── types/
│   ├── poi.ts
│   └── mcp.ts
└── package.json

### 4.2 MCP Client Implementation

// services/mcp-client.ts
import { EventSource } from 'react-native-sse';

interface MCPTool {
  name: string;
  description: string;
  input_schema: object;
}

interface MCPCallToolRequest {
  method: 'tools/call';
  params: {
    name: string;
    arguments: Record<string, any>;
  };
}

class MCPClient {
  private serverUrl: string;
  private eventSource: EventSource | null = null;
  
  constructor(serverUrl: string) {
    this.serverUrl = serverUrl;
  }
  
  /**
   * Initialize connection to MCP server
   */
  async connect(): Promise<void> {
    this.eventSource = new EventSource(this.serverUrl);
    
    return new Promise((resolve, reject) => {
      this.eventSource!.addEventListener('open', () => {
        console.log('MCP connection established');
        resolve();
      });
      
      this.eventSource!.addEventListener('error', (error) => {
        console.error('MCP connection error:', error);
        reject(error);
      });
    });
  }
  
  /**
   * List available tools from MCP server
   */
  async listTools(): Promise<MCPTool[]> {
    const response = await fetch(`${this.serverUrl}/tools/list`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ method: 'tools/list' })
    });
    
    const data = await response.json();
    return data.result.tools;
  }
  
  /**
   * Call MCP tool
   */
  async callTool(name: string, args: Record<string, any>): Promise<any> {
    const request: MCPCallToolRequest = {
      method: 'tools/call',
      params: {
        name,
        arguments: args
      }
    };
    
    const response = await fetch(`${this.serverUrl}/tools/call`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    });
    
    const data = await response.json();
    return data.result;
  }
  
  /**
   * High-level: Get POI recommendations
   */
  async getRecommendations(context: {
    location: { latitude: number; longitude: number };
    datetime: string;
    occasion: string;
    weather?: string;
    groupSize?: number;
  }): Promise<any[]> {
    return this.callTool('get_contextual_recommendations', context);
  }
  
  /**
   * High-level: Search POIs by vibe
   */
  async searchByVibe(
    query: string,
    location?: { latitude: number; longitude: number }
  ): Promise<any[]> {
    return this.callTool('search_by_vibe', { query, location });
  }
  
  /**
   * High-level: Query POIs with filters
   */
  async queryPOIs(filters: {
    location: { latitude: number; longitude: number; radius_meters?: number };
    categories?: string[];
    min_prestige_score?: number;
    michelin_stars?: number[];
  }): Promise<any[]> {
    return this.callTool('query_pois', filters);
  }
}

export const mcpClient = new MCPClient(
  process.env.EXPO_PUBLIC_MCP_SERVER_URL || 'http://localhost:8000'
);

### 4.3 GPT-5.1 Integration with MCP Tools

// services/gpt.ts
import OpenAI from 'openai';
import { mcpClient } from './mcp-client';

const openai = new OpenAI({
  apiKey: process.env.EXPO_PUBLIC_OPENAI_API_KEY,
});

interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

interface ConversationContext {
  location?: { latitude: number; longitude: number };
  weather?: string;
  datetime?: string;
}

/**
 * Convert MCP tools to OpenAI function definitions
 */
async function getMCPToolsAsOpenAIFunctions() {
  const tools = await mcpClient.listTools();
  
  return tools.map(tool => ({
    type: 'function' as const,
    function: {
      name: tool.name,
      description: tool.description,
      parameters: tool.input_schema
    }
  }));
}

/**
 * Main chat function with MCP tool integration
 */
export async function chat(
  messages: Message[],
  context: ConversationContext
): Promise<{ message: string; toolResults?: any[] }> {
  // Get MCP tools as OpenAI functions
  const tools = await getMCPToolsAsOpenAIFunctions();
  
  // Add system prompt with context
  const systemMessage: Message = {
    role: 'system',
    content: `You are a NYC concierge assistant helping users discover amazing places.

Current Context:
- Location: ${context.location ? `${context.location.latitude}, ${context.location.longitude}` : 'Unknown'}
- Weather: ${context.weather || 'Unknown'}
- DateTime: ${context.datetime || new Date().toISOString()}

You have access to tools that query a curated database of NYC points of interest.
Use these tools to provide personalized, context-aware recommendations.

When recommending venues:
1. Highlight prestige markers (Michelin stars, awards, best-of lists)
2. Explain WHY each venue is recommended
3. Consider current context (location, time, weather)
4. Provide practical details (distance, price, reservations)

Be conversational and enthusiastic about NYC's incredible venues!`
  };
  
  // Make initial GPT call
  let response = await openai.chat.completions.create({
    model: 'gpt-5.1-turbo',
    messages: [systemMessage, ...messages],
    tools,
    tool_choice: 'auto',
  });
  
  let assistantMessage = response.choices[0].message;
  const toolResults: any[] = [];
  
  // Handle tool calls
  while (assistantMessage.tool_calls && assistantMessage.tool_calls.length > 0) {
    // Execute each tool call via MCP
    const toolCallPromises = assistantMessage.tool_calls.map(async (toolCall) => {
      const functionName = toolCall.function.name;
      const functionArgs = JSON.parse(toolCall.function.arguments);
      
      console.log(`Calling MCP tool: ${functionName}`, functionArgs);
      
      // Call MCP server
      const result = await mcpClient.callTool(functionName, functionArgs);
      
      toolResults.push({
        tool: functionName,
        args: functionArgs,
        result
      });
      
      return {
        tool_call_id: toolCall.id,
        role: 'tool' as const,
        name: functionName,
        content: JSON.stringify(result)
      };
    });
    
    const toolMessages = await Promise.all(toolCallPromises);
    
    // Continue conversation with tool results
    response = await openai.chat.completions.create({
      model: 'gpt-5.1-turbo',
      messages: [
        systemMessage,
        ...messages,
        assistantMessage,
        ...toolMessages
      ],
      tools,
      tool_choice: 'auto',
    });
    
    assistantMessage = response.choices[0].message;
  }
  
  return {
    message: assistantMessage.content || '',
    toolResults
  };
}

/**
 * Streaming chat for real-time responses
 */
export async function* chatStream(
  messages: Message[],
  context: ConversationContext
): AsyncGenerator<string> {
  const tools = await getMCPToolsAsOpenAIFunctions();
  
  const systemMessage: Message = {
    role: 'system',
    content: `You are a NYC concierge assistant...` // Same as above
  };
  
  const stream = await openai.chat.completions.create({
    model: 'gpt-5.1-turbo',
    messages: [systemMessage, ...messages],
    tools,
    stream: true,
  });
  
  for await (const chunk of stream) {
    const content = chunk.choices[0]?.delta?.content;
    if (content) {
      yield content;
    }
  }
}

### 4.4 Main Chat Screen

// app/(tabs)/index.tsx
import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  StyleSheet
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { chat } from '@/services/gpt';
import { mcpClient } from '@/services/mcp-client';
import { useLocation } from '@/hooks/useLocation';
import { useWeather } from '@/hooks/useWeather';

import MessageBubble from '@/components/Chat/MessageBubble';
import ChatInput from '@/components/Chat/ChatInput';
import POICard from '@/components/Chat/POICard';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  toolResults?: any[];
  timestamp: Date;
}

export default function ChatScreen() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const scrollViewRef = useRef<ScrollView>(null);
  
  // Get current context
  const { location, error: locationError } = useLocation();
  const { weather } = useWeather(location);
  
  // Initialize MCP connection
  useEffect(() => {
    mcpClient.connect().catch(console.error);
  }, []);
  
  // Welcome message
  useEffect(() => {
    if (location) {
      setMessages([{
        id: 'welcome',
        role: 'assistant',
        content: `Hey! I'm your NYC concierge. I can help you discover amazing restaurants, bars, cultural venues, and more based on where you are and what you're looking for. What brings you out today?`,
        timestamp: new Date()
      }]);
    }
  }, [location]);
  
  const handleSendMessage = async (text: string) => {
    if (!text.trim() || isLoading) return;
    
    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: text,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    
    try {
      // Get context
      const context = {
        location: location ? {
          latitude: location.coords.latitude,
          longitude: location.coords.longitude
        } : undefined,
        weather: weather?.condition,
        datetime: new Date().toISOString()
      };
      
      // Call GPT with MCP tools
      const response = await chat(
        messages.map(m => ({
          role: m.role,
          content: m.content
        })).concat([{ role: 'user', content: text }]),
        context
      );
      
      // Add assistant response
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.message,
        toolResults: response.toolResults,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, assistantMessage]);
      
      // Scroll to bottom
      setTimeout(() => {
        scrollViewRef.current?.scrollToEnd({ animated: true });
      }, 100);
      
    } catch (error) {
      console.error('Chat error:', error);
      
      // Show error message
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date()
      }]);
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <KeyboardAvoidingView
        style={styles.keyboardAvoid}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}
      >
        <ScrollView
          ref={scrollViewRef}
          style={styles.scrollView}
          contentContainerStyle={styles.messagesContainer}
        >
          {messages.map(message => (
            <View key={message.id}>
              <MessageBubble
                role={message.role}
                content={message.content}
                timestamp={message.timestamp}
              />
              
              {/* Render POI cards if tool results present */}
              {message.toolResults?.map((toolResult, index) => (
                <View key={index} style={styles.toolResultContainer}>
                  {Array.isArray(toolResult.result) && 
                   toolResult.result.map((poi: any, poiIndex: number) => (
                    <POICard
                      key={poiIndex}
                      poi={poi}
                      onPress={() => {
                        // Navigate to POI detail
                        // router.push(`/poi/${poi.id}`);
                      }}
                    />
                  ))}
                </View>
              ))}
            </View>
          ))}
          
          {isLoading && (
            <MessageBubble
              role="assistant"
              content="..."
              timestamp={new Date()}
              isLoading
            />
          )}
        </ScrollView>
        
        <ChatInput
          onSend={handleSendMessage}
          disabled={isLoading || !location}
          placeholder={
            !location 
              ? "Waiting for location..."
              : "Ask about restaurants, bars, culture..."
          }
        />
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  keyboardAvoid: {
    flex: 1,
  },
  scrollView: {
    flex: 1,
  },
  messagesContainer: {
    padding: 16,
  },
  toolResultContainer: {
    marginTop: 8,
    gap: 8,
  }
});

### 4.5 POI Card Component

// components/Chat/POICard.tsx
import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Image } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface POI {
  name: string;
  category: string;
  distance_meters: number;
  address: string;
  prestige: {
    score: number;
    michelin_stars?: number;
    awards: string[];
  };
  price: string;
  signature_dishes?: string[];
  phone?: string;
}

interface POICardProps {
  poi: POI;
  onPress: () => void;
}

export default function POICard({ poi, onPress }: POICardProps) {
  const distanceText = poi.distance_meters < 1000
    ? `${Math.round(poi.distance_meters)}m`
    : `${(poi.distance_meters / 1000).toFixed(1)}km`;
  
  return (
    <TouchableOpacity
      style={styles.card}
      onPress={onPress}
      activeOpacity={0.7}
    >
      <View style={styles.header}>
        <View style={styles.titleContainer}>
          <Text style={styles.name}>{poi.name}</Text>
          
          {/* Michelin Stars */}
          {poi.prestige.michelin_stars && (
            <View style={styles.michelinBadge}>
              <Text style={styles.michelinText}>
                {'⭐'.repeat(poi.prestige.michelin_stars)}
              </Text>
            </View>
          )}
        </View>
        
        <View style={styles.distanceContainer}>
          <Ionicons name="walk" size={14} color="#666" />
          <Text style={styles.distance}>{distanceText}</Text>
        </View>
      </View>
      
      <Text style={styles.address}>{poi.address}</Text>
      
      {/* Price and Category */}
      <View style={styles.metaRow}>
        <Text style={styles.price}>{poi.price}</Text>
        <Text style={styles.separator}>•</Text>
        <Text style={styles.category}>
          {poi.category.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())}
        </Text>
      </View>
      
      {/* Signature Dishes */}
      {poi.signature_dishes && poi.signature_dishes.length > 0 && (
        <View style={styles.dishesContainer}>
          <Text style={styles.dishesLabel}>Known for:</Text>
          <Text style={styles.dishes}>
            {poi.signature_dishes.join(', ')}
          </Text>
        </View>
      )}
      
      {/* Awards */}
      {poi.prestige.awards.length > 0 && (
        <View style={styles.awardsContainer}>
          <Ionicons name="trophy" size={12} color="#D4AF37" />
          <Text style={styles.awards}>
            {poi.prestige.awards[0]}
            {poi.prestige.awards.length > 1 && ` +${poi.prestige.awards.length - 1} more`}
          </Text>
        </View>
      )}
      
      {/* Action Buttons */}
      <View style={styles.actions}>
        {poi.phone && (
          <TouchableOpacity style={styles.actionButton}>
            <Ionicons name="call" size={16} color="#007AFF" />
            <Text style={styles.actionText}>Call</Text>
          </TouchableOpacity>
        )}
        
        <TouchableOpacity style={styles.actionButton}>
          <Ionicons name="navigate" size={16} color="#007AFF" />
          <Text style={styles.actionText}>Directions</Text>
        </TouchableOpacity>
        
        <TouchableOpacity style={styles.actionButton}>
          <Ionicons name="bookmark-outline" size={16} color="#007AFF" />
          <Text style={styles.actionText}>Save</Text>
        </TouchableOpacity>
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#f9f9f9',
    borderRadius: 12,
    padding: 16,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: '#e0e0e0',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 4,
  },
  titleContainer: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  name: {
    fontSize: 18,
    fontWeight: '600',
    color: '#000',
    flex: 1,
  },
  michelinBadge: {
    backgroundColor: '#FFE5E5',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 8,
  },
  michelinText: {
    fontSize: 12,
  },
  distanceContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  distance: {
    fontSize: 14,
    color: '#666',
  },
  address: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  metaRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 8,
  },
  price: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  separator: {
    color: '#ccc',
  },
  category: {
    fontSize: 14,
    color: '#666',
  },
  dishesContainer: {
    marginBottom: 8,
  },
  dishesLabel: {
    fontSize: 12,
    color: '#999',
    marginBottom: 2,
  },
  dishes: {
    fontSize: 14,
    color: '#333',
    fontStyle: 'italic',
  },
  awardsContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    marginBottom: 12,
  },
  awards: {
    fontSize: 12,
    color: '#666',
    flex: 1,
  },
  actions: {
    flexDirection: 'row',
    gap: 12,
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
    paddingTop: 12,
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  actionText: {
    fontSize: 14,
    color: '#007AFF',
    fontWeight: '500',
  },
});

### 4.6 Location & Weather Hooks

// hooks/useLocation.ts
import { useState, useEffect } from 'react';
import * as Location from 'expo-location';

export function useLocation() {
  const [location, setLocation] = useState<Location.LocationObject | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    (async () => {
      try {
        const { status } = await Location.requestForegroundPermissionsAsync();
        
        if (status !== 'granted') {
          setError('Location permission denied');
          return;
        }
        
        const currentLocation = await Location.getCurrentPositionAsync({
          accuracy: Location.Accuracy.Balanced,
        });
        
        setLocation(currentLocation);
        
        // Watch for location updates
        Location.watchPositionAsync(
          {
            accuracy: Location.Accuracy.Balanced,
            timeInterval: 30000, // Update every 30s
            distanceInterval: 50, // Or when moved 50m
          },
          (newLocation) => {
            setLocation(newLocation);
          }
        );
        
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Location error');
      }
    })();
  }, []);
  
  return { location, error };
}

// hooks/useWeather.ts
import { useState, useEffect } from 'react';
import * as Location from 'expo-location';

interface Weather {
  condition: 'sunny' | 'rain' | 'snow' | 'cloudy';
  temperature: number;
  description: string;
}

export function useWeather(location: Location.LocationObject | null) {
  const [weather, setWeather] = useState<Weather | null>(null);
  
  useEffect(() => {
    if (!location) return;
    
    // Call weather API (e.g., OpenWeatherMap)
    const fetchWeather = async () => {
      try {
        const { latitude, longitude } = location.coords;
        
        const response = await fetch(
          `https://api.openweathermap.org/data/2.5/weather?lat=${latitude}&lon=${longitude}&appid=${process.env.EXPO_PUBLIC_WEATHER_API_KEY}&units=imperial`
        );
        
        const data = await response.json();
        
        // Map weather condition
        const condition = mapWeatherCondition(data.weather[0].main);
        
        setWeather({
          condition,
          temperature: Math.round(data.main.temp),
          description: data.weather[0].description
        });
        
      } catch (error) {
        console.error('Weather fetch error:', error);
      }
    };
    
    fetchWeather();
    
    // Refresh every 15 minutes
    const interval = setInterval(fetchWeather, 15 * 60 * 1000);
    
    return () => clearInterval(interval);
  }, [location]);
  
  return { weather };
}

function mapWeatherCondition(main: string): Weather['condition'] {
  const conditions: Record<string, Weather['condition']> = {
    'Clear': 'sunny',
    'Clouds': 'cloudy',
    'Rain': 'rain',
    'Drizzle': 'rain',
    'Snow': 'snow',
    'Thunderstorm': 'rain',
  };
  
  return conditions[main] || 'sunny';
}

---

## Phase 5: Testing & Demo (Day 4)

### 5.1 Testing Strategy (MVP Focus)

**Data Quality Testing:**
# tests/test_curation.py
def test_michelin_data_accuracy():
    """Verify Michelin star data matches official guide"""
    pois = db.pois.find({"prestige.michelin_stars": {"$gte": 1}})
    
    for poi in pois:
        # Cross-check with Tavily
        result = tavily.search(
            f"{poi['name']} NYC Michelin stars 2025 official",
            include_domains=["guide.michelin.com"]
        )
        
        assert verify_michelin_status(result, poi)

def test_prestige_score_consistency():
    """Ensure prestige scores are calculated consistently"""
    sample_pois = db.pois.aggregate([{"$sample": {"size": 100}}])
    
    for poi in sample_pois:
        recalculated = calculate_prestige_score(poi)
        assert abs(recalculated - poi["prestige"]["score"]) < 1.0

**MCP Server Testing:**
# tests/test_mcp.py
import pytest
from src.tools.recommendations import get_contextual_recommendations

@pytest.mark.asyncio
async def test_contextual_recommendations():
    """Test contextual recommendation logic"""
    result = await get_contextual_recommendations(
        location={"latitude": 40.7580, "longitude": -73.9855},
        datetime="2025-11-23T19:00:00Z",
        occasion="date-night",
        weather="sunny",
        group_size=2
    )
    
    assert len(result) > 0
    assert all("relevance_score" in poi for poi in result)
    assert result[0]["relevance_score"] >= result[-1]["relevance_score"]

@pytest.mark.asyncio
async def test_semantic_search():
    """Test vibe-based search"""
    result = await search_by_vibe(
        query="romantic Italian with outdoor seating",
        location={"latitude": 40.7580, "longitude": -73.9855}
    )
    
    assert len(result) > 0
    assert all("italian" in poi["category"].lower() or 
               "italian" in poi.get("subcategories", [])
               for poi in result)

**Mobile App Testing:**
// __tests__/chat.test.ts
import { chat } from '@/services/gpt';
import { mcpClient } from '@/services/mcp-client';

describe('Chat Integration', () => {
  beforeAll(async () => {
    await mcpClient.connect();
  });
  
  it('should handle basic recommendation request', async () => {
    const result = await chat(
      [
        { role: 'user', content: 'Find me a Michelin star restaurant nearby' }
      ],
      {
        location: { latitude: 40.7580, longitude: -73.9855 },
        datetime: new Date().toISOString()
      }
    );
    
    expect(result.message).toBeTruthy();
    expect(result.toolResults).toHaveLength(1);
    expect(result.toolResults[0].tool).toBe('query_pois');
  });
  
  it('should handle conversational context', async () => {
    const result = await chat(
      [
        { role: 'user', content: 'I want Italian food' },
        { role: 'assistant', content: 'Here are some great Italian spots...' },
        { role: 'user', content: 'What about the first one? Is it expensive?' }
      ],
      {
        location: { latitude: 40.7580, longitude: -73.9855 },
        datetime: new Date().toISOString()
      }
    );
    
    expect(result.message).toContain('price');
  });
});

### 5.2 Deployment Architecture (MVP: Local Demo Only)

**Backend (MCP Server):**
# Local development only - NO production deployment for hackathon
# Run MCP server locally
python -m src.server  # or npm run dev

# MongoDB Atlas (cloud)
# Use free M0 tier for demo
# Connection string in .env

**Mobile App (Expo):**
# Development mode only
npx expo start

# Test on physical device via Expo Go app
# Scan QR code from terminal

**Demo Environment:**
- MCP server running on localhost:3000
- MongoDB Atlas M0 free tier (cloud)
- Expo app via Expo Go on iPhone/Android
- All API keys in local .env files

---

## Timeline & Milestones (HACKATHON: Nov 21-24)

### Friday Nov 21 (4-8pm): Kickoff + Data Foundation
- **Hour 1-2:** Team setup, MongoDB Atlas provisioning, Tavily API key setup
- **Hour 2-4:** Implement Tavily search pipeline, extract first 30 Michelin restaurants
- **Goal:** 30 POIs curated, MongoDB schema defined

### Saturday Nov 22 (Remote Hacking): Complete Dataset + MCP Core
- **Morning:** Complete 100 POI dataset (expand to casual dining + bars)
- **Afternoon:** Generate embeddings (if time allows), bulk import to MongoDB
- **Evening:** Scaffold MCP server, implement `query_pois` tool
- **Goal:** 100 POIs in MongoDB, 1 working MCP tool

### Sunday Nov 23 (Remote Hacking): MCP + Mobile App
- **Morning:** Implement `get_contextual_recommendations` tool, test with MCP inspector
- **Afternoon:** Scaffold Expo app, implement chat UI with GPT-5.1 + MCP client
- **Evening:** Add location services, weather context, POI cards, basic map
- **Goal:** Working end-to-end demo: chat → recommendations → map view

### Monday Nov 24 (Judging Day): Polish & Demo
- **Morning:** Bug fixes, UI polish, test on physical device
- **Midday:** Record 1-min demo video, prepare presentation deck
- **Afternoon:** Submit project, present to judges
- **Goal:** Polished demo showcasing MongoDB, Tavily, and MCP integration

---

## Success Metrics (MVP)

### Data Quality
- **Coverage:** 100 curated Manhattan restaurants
- **Prestige Validation:** 30+ Michelin/James Beard restaurants verified
- **Freshness:** All data validated within 90 days via Tavily

### Technical Performance
- **Query Latency:** <500ms for MongoDB geospatial queries (acceptable for demo)
- **MCP Response Time:** <2s for tool calls
- **Chat Latency:** <5s for GPT-5.1 responses with MCP tools (acceptable for demo)

### User Experience
- **Core Flow Works:** User can ask for recommendations and see results
- **Context Awareness:** Location, time, and weather factored into recommendations
- **Visual Polish:** Clean UI with Michelin star badges, map markers

### Hackathon Judging
- **MongoDB Usage:** Demonstrates geospatial search + aggregations (vector search nice-to-have)
- **Tavily Integration:** Shows prestige curation with multi-source validation
- **MCP Architecture:** Clean tool definitions, proper GPT-5.1 integration
- **Differentiation:** Prestige-first approach vs generic Yelp/Google Maps

---

## Competitive Advantages for Hackathon

### 1. **Prestige-First Curation**
Unlike generic map apps, every POI is validated for quality markers (Michelin, awards, best-of lists) via Tavily's advanced search.

### 2. **True Contextual Intelligence**
Recommendations factor in real-time location, time of day, weather, occasion, and group size—not just proximity.

### 3. **Production-Ready MCP Architecture**
Follows LastMile AI best practices with composable tools, resources, and prompts—deployable as standalone server.

### 4. **Conversational Discovery**
GPT-5.1 integration enables natural language exploration ("romantic Italian with outdoor seating") rather than rigid filters.

### 5. **Hybrid Search**
Combines vector similarity (semantic meaning), geospatial proximity, and prestige scoring in single query.

---

## Future Enhancements

### Post-Hackathon Roadmap