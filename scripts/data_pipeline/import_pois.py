#!/usr/bin/env python3
"""
Quick POI Import Script
Imports 7 curated POIs to MongoDB Atlas
"""

import json
import os
from pymongo import MongoClient, GEOSPHERE

print('=' * 70)
print('NYC POI MongoDB Import')
print('=' * 70)

# Load curated POIs
print('\n📂 Loading curated POIs...')
with open('data/curated/curated_pois.json') as f:
    pois = json.load(f)
print(f'✅ Loaded {len(pois)} curated POIs')

# Get MongoDB URI from environment
uri = os.getenv('MONGODB_URI')
if not uri:
    print('\n❌ ERROR: MONGODB_URI environment variable not set')
    print('Please run: export MONGODB_URI="your_mongodb_uri_here"')
    print('Or set it in your .env file')
    exit(1)

# Connect to MongoDB
print('\n🔌 Connecting to MongoDB Atlas...')
client = MongoClient(uri, serverSelectionTimeoutMS=10000)

try:
    # Test connection
    client.admin.command('ping')
    print('✅ Connected successfully')
    
    # Get database and collection
    db = client['nyc-poi']
    pois_collection = db['pois']
    
    # Clear existing data
    print('\n🗑️  Clearing existing POIs...')
    result = pois_collection.delete_many({})
    print(f'   Deleted {result.deleted_count} old POIs')
    
    # Create geospatial index
    print('\n📇 Creating geospatial index...')
    pois_collection.create_index([('location', GEOSPHERE)], name='location_2dsphere')
    print('   ✅ Index created')
    
    # Import POIs
    print(f'\n📥 Importing {len(pois)} POIs...')
    result = pois_collection.insert_many(pois)
    print(f'   ✅ Imported {len(result.inserted_ids)} POIs')
    
    # Verify
    count = pois_collection.count_documents({})
    print(f'\n📊 Verification: {count} POIs in database')
    
    # Test geospatial query (Times Square area)
    print('\n🗺️  Testing geospatial query (Times Square, 2km radius)...')
    pipeline = [
        {
            '$geoNear': {
                'near': {'type': 'Point', 'coordinates': [-73.9851, 40.7580]},
                'distanceField': 'distance',
                'maxDistance': 2000,
                'spherical': True
            }
        },
        {'$sort': {'prestige.score': -1}},
        {'$limit': 5}
    ]
    
    results = list(pois_collection.aggregate(pipeline))
    print(f'   Found {len(results)} POIs near Times Square:')
    print()
    
    for i, poi in enumerate(results, 1):
        stars = poi.get('prestige', {}).get('michelin_stars')
        stars_str = f" ({'⭐' * stars})" if stars else ''
        distance = poi.get('distance', 0)
        score = poi.get('prestige', {}).get('score', 0)
        print(f'   {i}. {poi["name"]}{stars_str}')
        print(f'      Distance: {distance:.0f}m | Prestige: {score}')
    
    client.close()
    
    print('\n' + '=' * 70)
    print('✨ Import Complete!')
    print('=' * 70)
    print(f'\n✅ {count} POIs successfully imported to MongoDB Atlas')
    print('🗄️  Database: nyc-poi')
    print('📦 Collection: pois')
    print('\n🚀 Ready for MCP server development!')
    print('=' * 70)
    
except Exception as e:
    print(f'\n❌ Error: {e}')
    import traceback
    traceback.print_exc()
    client.close()
    exit(1)
