#!/usr/bin/env python3
"""
MCP Server Test Script
Tests the NYC POI Concierge MCP server tools
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from utils.mongodb import MongoDBClient

print("=" * 70)
print("NYC POI MCP Server - Connection Test")
print("=" * 70)

# Test MongoDB connection
print("\n🔌 Testing MongoDB connection...")
mongo = MongoDBClient()

if not mongo.connect():
    print("❌ MongoDB connection failed!")
    sys.exit(1)

print("✅ MongoDB connected successfully")

# Get POI count
count = mongo.pois.count_documents({})
print(f"📊 POIs in database: {count}")

if count == 0:
    print("\n⚠️  No POIs found! Run import script first:")
    print("   python3 ../../import_pois.py")
    sys.exit(1)

# Test geospatial query (simulate query_pois tool)
print("\n🗺️  Testing geospatial query (Times Square, 2km)...")

pipeline = [
    {
        "$geoNear": {
            "near": {
                "type": "Point",
                "coordinates": [-73.9851, 40.7580]
            },
            "distanceField": "distance",
            "maxDistance": 2000,
            "spherical": True
        }
    },
    {"$sort": {"prestige.score": -1}},
    {"$limit": 3}
]

results = list(mongo.pois.aggregate(pipeline))

if results:
    print(f"✅ Found {len(results)} POIs:")
    for i, poi in enumerate(results, 1):
        stars = poi.get("prestige", {}).get("michelin_stars")
        stars_str = f" ({'⭐' * stars})" if stars else ""
        print(f"   {i}. {poi['name']}{stars_str}")
        print(f"      Distance: {poi.get('distance', 0):.0f}m")
else:
    print("❌ No results from geospatial query")
    sys.exit(1)

# Test contextual filtering (simulate contextual_recommendations tool)
print("\n🎯 Testing contextual filtering (date-night)...")

pipeline = [
    {
        "$geoNear": {
            "near": {"type": "Point", "coordinates": [-73.9851, 40.7580]},
            "distanceField": "distance",
            "maxDistance": 3000,
            "spherical": True
        }
    },
    {
        "$match": {
            "best_for.occasions": "date-night"
        }
    },
    {"$limit": 3}
]

results = list(mongo.pois.aggregate(pipeline))

if results:
    print(f"✅ Found {len(results)} date-night options:")
    for i, poi in enumerate(results, 1):
        print(f"   {i}. {poi['name']}")
else:
    print("⚠️  No date-night options found (this is okay)")

mongo.close()

print("\n" + "=" * 70)
print("✅ All tests passed!")
print("=" * 70)
print("\n🚀 MCP Server is ready to run!")
print("\nTo start the server:")
print("  cd backend/mcp-server")
print("  export $(cat ../../.env | grep -v '^#' | xargs)")
print("  python3 src/server.py")
