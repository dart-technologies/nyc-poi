#!/usr/bin/env python3
"""
Quick script to add top Manhattan brunch POIs to the database  
Uses pymongo directly to avoid import issues
"""

import os
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../backend/mcp-server/.env')

# MongoDB connection
MONGO_URI = os.getenv('MONGODB_URI')

# Top Manhattan brunch spots
BRUNCH_POIS = [
    {
        "name": "Balthazar",
        "slug": "balthazar",
        "category": "casual-dining",
        "subcategories": ["brunch", "french"],
        "location": {
            "type": "Point",
            "coordinates": [-73.9977, 40.7223]  # SoHo
        },
        "address": {
            "street": "80 Spring St",
            "city": "New York",
            "state": "NY",
            "zip": "10012",
            "neighborhood": "SoHo",
            "borough": "Manhattan"
        },
        "contact": {
            "phone": "(212) 965-1414",
            "website": "https://balthazarny.com"
        },
        "experience": {
            "price_range": "$$$",
            "signature_dishes": ["French toast", "Eggs Benedict", "Bloody Mary"]
        },
        "prestige": {
            "score": 15
        },
        "best_for": {
            "occasions": ["brunch", "date"],
            "time_of_day": ["morning", "lunch"],
            "group_size": [2, 4]
        }
    },
    {
        "name": "Sarabeth's",
        "slug": "sarabeths",
        "category": "casual-dining",
        "subcategories": ["brunch", "breakfast"],
        "location": {
            "type": "Point",
            "coordinates": [-73.9795, 40.7831]  # Upper West Side
        },
        "address": {
            "street": "423 Amsterdam Ave",
            "city": "New York",
            "state": "NY",
            "zip": "10024",
            "neighborhood": "Upper West Side",
            "borough": "Manhattan"
        },
        "contact": {
            "phone": "(212) 496-6280",
            "website": "https://www.sarabethsrestaurants.com"
        },
        "experience": {
            "price_range": "$$",
            "signature_dishes": ["Lemon ricotta pancakes", "Eggs Florentine"]
        },
        "prestige": {
            "score": 10
        },
        "best_for": {
            "occasions": ["brunch", "family"],
            "time_of_day": ["morning", "lunch"],
            "group_size": [2, 4, 6]
        }
    },
    {
        "name": "Jack's Wife Freda",
        "slug": "jacks-wife-freda",
        "category": "casual-dining",
        "subcategories": ["brunch", "mediterranean"],
        "location": {
            "type": "Point",
            "coordinates": [-73.9976, 40.7226]  # SoHo
        },
        "address": {
            "street": "224 Lafayette St",
            "city": "New York",
            "state": "NY",
            "zip": "10012",
            "neighborhood": "SoHo",
            "borough": "Manhattan"
        },
        "contact": {
            "phone": "(212) 510-8550",
            "website": "https://jackswifefreda.com"
        },
        "experience": {
            "price_range": "$$",
            "signature_dishes": ["Green shakshuka", "Rosewater waffles"]
        },
        "prestige": {
            "score": 12
        },
        "best_for": {
            "occasions": ["brunch", "casual"],
            "time_of_day": ["morning", "lunch"],
            "group_size": [2, 4]
        }
    },
    {
        "name": "Clinton St. Baking Company",
        "slug": "clinton-st-baking-company",
        "category": "casual-dining",
        "subcategories": ["brunch", "breakfast"],
        "location": {
            "type": "Point",
            "coordinates": [-73.9835, 40.7211]  # Lower East Side
        },
        "address": {
            "street": "4 Clinton St",
            "city": "New York",
            "state": "NY",
            "zip": "10002",
            "neighborhood": "Lower East Side",
            "borough": "Manhattan"
        },
        "contact": {
            "phone": "(646) 602-6263",
            "website": "https://clintonstreetbaking.com"
        },
        "experience": {
            "price_range": "$$",
            "signature_dishes": ["Blueberry pancakes", "Biscuits and gravy"]
        },
        "prestige": {
            "score": 14
        },
        "best_for": {
            "occasions": ["brunch"],
            "time_of_day": ["morning", "lunch"],
            "group_size": [2, 4]
        }
    },
    {
        "name": "Sunday in Brooklyn",
        "slug": "sunday-in-brooklyn",
        "category": "casual-dining",
        "subcategories": ["brunch", "american"],
        "location": {
            "type": "Point",
            "coordinates": [-73.9571, 40.7247]  # Williamsburg
        },
        "address": {
            "street": "348 Wythe Ave",
            "city": "Brooklyn",
            "state": "NY",
            "zip": "11249",
            "neighborhood": "Williamsburg",
            "borough": "Brooklyn"
        },
        "contact": {
            "phone": "(347) 222-6722",
            "website": "https://www.sundayinbrooklyn.com"
        },
        "experience": {
            "price_range": "$$",
            "signature_dishes": ["Hazelnut praline pancake", "Malted pancake"]
        },
        "prestige": {
            "score": 16
        },
        "best_for": {
            "occasions": ["brunch", "date"],
            "time_of_day": ["morning", "lunch"],
            "group_size": [2, 4]
        }
    }
]


def main():
    """Add brunch POIs to MongoDB"""
    print("🥞 Adding top Manhattan brunch spots...")
    print()
    
    # Connect to MongoDB
    client = MongoClient(MONGO_URI)
    db = client['nyc-poi']
    collection = db['pois']
    
    print(f"✅ Connected to database: {db.name}")
    print(f"✅ Using collection: {collection.name}")
    print()
    
    # Add metadata
    now = datetime.now()
    for poi in BRUNCH_POIS:
        poi["created_at"] = now.isoformat()
        poi["updated_at"] = now.isoformat()
        poi["data_quality_score"] = 0.8
        poi["sources"] = [{
            "type": "manual_curation",
            "note": "Top Manhattan brunch spots",
            "curated_at": now.isoformat()
        }]
    
    # Insert
    try:
        result = collection.insert_many(BRUNCH_POIS)
        print(f"✅ Added {len(result.inserted_ids)} brunch POIs:")
        for poi in BRUNCH_POIS:
            print(f"   • {poi['name']} ({poi['address']['neighborhood']})")
        print()
        print("🎉 Brunch filter is now ready!")
        
    except Exception as e:
        print(f"❌ Error inserting POIs: {e}")


if __name__ == "__main__":
    main()
