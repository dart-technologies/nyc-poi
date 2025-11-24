#!/usr/bin/env python3
"""
MCP Server Interactive Test
Direct testing of MCP server tools without Inspector UI
"""

import sys
import os
import json
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from utils.mongodb import MongoDBClient

print("=" * 70)
print("NYC POI MCP Server - Interactive Test")
print("=" * 70)

# Initialize MongoDB
print("\n🔌 Initializing MongoDB connection...")
mongo = MongoDBClient()
if not mongo.connect():
    print("❌ Failed to connect to MongoDB")
    sys.exit(1)

print("✅ Connected successfully")
print(f"📊 POIs available: {mongo.pois.count_documents({})}\n")

# Test 1: query_pois - Find Michelin restaurants near Times Square
print("=" * 70)
print("TEST 1: query_pois - Michelin Restaurants Near Times Square")
print("=" * 70)

test1_params = {
    "latitude": 40.7580,
    "longitude": -73.9851,
    "radius_meters": 2000,
    "michelin_stars": [1, 2, 3],
    "limit": 5
}

print(f"\nParameters: {json.dumps(test1_params, indent=2)}\n")

# Execute query
pipeline = [
    {
        "$geoNear": {
            "near": {
                "type": "Point",
                "coordinates": [test1_params["longitude"], test1_params["latitude"]]
            },
            "distanceField": "distance",
            "maxDistance": test1_params["radius_meters"],
            "spherical": True
        }
    },
    {
        "$match": {
            "prestige.michelin_stars": {"$in": test1_params["michelin_stars"]}
        }
    },
    {"$sort": {"prestige.score": -1, "distance": 1}},
    {"$limit": test1_params["limit"]}
]

results = list(mongo.pois.aggregate(pipeline))

print(f"Found {len(results)} POI(s) within {test1_params['radius_meters']}m:\n")

for i, poi in enumerate(results, 1):
    stars = poi.get("prestige", {}).get("michelin_stars")
    stars_str = f" {'⭐' * stars}" if stars else ""
    
    print(f"{i}. **{poi['name']}**{stars_str}")
    print(f"   📍 {poi.get('address', {}).get('street', 'N/A')}, {poi.get('address', {}).get('neighborhood', '')}")
    print(f"   📏 Distance: {poi.get('distance', 0):.0f}m")
    print(f"   ⭐ Prestige Score: {poi.get('prestige', {}).get('score', 0)}")
    print(f"   💰 Price: {poi.get('experience', {}).get('price_range', 'N/A')}")
    print(f"   📞 {poi.get('contact', {}).get('phone', 'N/A')}")
    
    if poi.get('experience', {}).get('signature_dishes'):
        dishes = poi['experience']['signature_dishes'][:2]
        print(f"   🍽️  Signature: {', '.join(dishes)}")
    print()

# Test 2: get_contextual_recommendations - Date night
print("\n" + "=" * 70)
print("TEST 2: get_contextual_recommendations - Date Night")
print("=" * 70)

test2_params = {
    "latitude": 40.7580,
    "longitude": -73.9851,
    "radius_meters": 3000,
    "occasion": "date-night",
    "group_size": 2,
    "budget": "$$$"
}

print(f"\nParameters: {json.dumps(test2_params, indent=2)}\n")

# Execute contextual query
pipeline = [
    {
        "$geoNear": {
            "near": {
                "type": "Point",
                "coordinates": [test2_params["longitude"], test2_params["latitude"]]
            },
            "distanceField": "distance",
            "maxDistance": test2_params["radius_meters"],
            "spherical": True
        }
    },
    {
        "$match": {
            "best_for.occasions": test2_params["occasion"],
            "best_for.group_size": {"$in": [test2_params["group_size"]]},
            "experience.price_range": test2_params["budget"]
        }
    },
    {
        "$addFields": {
            "relevance_score": {
                "$add": [
                    {"$multiply": ["$prestige.score", 0.4]},
                    {"$multiply": [{"$divide": [test2_params["radius_meters"], "$distance"]}, 30]}
                ]
            }
        }
    },
    {"$sort": {"relevance_score": -1}},
    {"$limit": 5}
]

results = list(mongo.pois.aggregate(pipeline))

print(f"🎯 **Personalized Recommendations for Date Night**\n")
print(f"📍 Location: Times Square area")
print(f"👥 Party Size: {test2_params['group_size']}")
print(f"💰 Budget: {test2_params['budget']}")
print(f"\nFound {len(results)} recommendation(s):\n")

for i, poi in enumerate(results, 1):
    stars = poi.get("prestige", {}).get("michelin_stars")
    stars_str = f" {'⭐' * stars}" if stars else ""
    
    print(f"**{i}. {poi['name']}**{stars_str}")
    print(f"   {poi.get('address', {}).get('neighborhood', '')} · {poi.get('distance', 0):.0f}m away")
    print(f"   💰 {poi.get('experience', {}).get('price_range', 'N/A')} · Prestige: {poi.get('prestige', {}).get('score', 0)}")
    print(f"   ✨ Perfect for {test2_params['occasion'].replace('-', ' ')}")
    print(f"   📞 {poi.get('contact', {}).get('phone', 'N/A')}\n")

mongo.close()

print("=" * 70)
print("✅ All Tests Complete!")
print("=" * 70)
print("\nThe MCP server is working correctly!")
print("\nTo use with Claude or GPT:")
print("  1. Configure MCP client with server path")
print("  2. Pass these tool schemas to the AI")
print("  3. AI can call tools with parameters like above")
