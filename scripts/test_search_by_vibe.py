#!/usr/bin/env python3
"""
Test search_by_vibe semantic search functionality.

This script tests the vector search implementation by:
1. Generating an embedding for a test vibe query
2. Performing vector search in MongoDB
3. Displaying results with similarity scores

Usage:
    python3 test_search_by_vibe.py
"""

import sys
import os
from openai import OpenAI
from pymongo import MongoClient
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../backend/mcp-server'))
from src.config import config

load_dotenv()


def test_vibe_search(vibe_query: str, limit: int = 5, min_score: float = 0.7):
    """Test semantic search with a vibe query"""
    
    print(f"🔮 Testing Vector Search")
    print(f"=" * 60)
    print(f"Query: \"{vibe_query}\"")
    print(f"Min Score: {min_score}")
    print(f"Limit: {limit}\n")
    
    # Initialize OpenAI
    print("🤖 Initializing OpenAI client...")
    openai_client = OpenAI(api_key=config.openai.api_key)
    
    # Generate embedding
    print(f"⚡ Generating embedding with {config.openai.embedding_model}...")
    response = openai_client.embeddings.create(
        model=config.openai.embedding_model,
        input=vibe_query,
        dimensions=config.openai.embedding_dimensions
    )
    query_vector = response.data[0].embedding
    print(f"✅ Generated {len(query_vector)}-dimensional vector\n")
    
    # Connect to MongoDB
    print("🔌 Connecting to MongoDB...")
    mongo_client = MongoClient(config.mongodb.uri)
    db = mongo_client[config.mongodb.database]
    pois = db[config.mongodb.pois_collection]
    print(f"✅ Connected to {config.mongodb.database}.{config.mongodb.pois_collection}\n")
    
    # Build vector search pipeline
    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "path": "embedding",
                "queryVector": query_vector,
                "numCandidates": 100,
                "limit": limit * 2
            }
        },
        {
            "$addFields": {
                "similarity_score": {"$meta": "vectorSearchScore"}
            }
        },
        {
            "$match": {
                "similarity_score": {"$gte": min_score}
            }
        },
        {
            "$project": {
                "name": 1,
                "category": 1,
                "subcategories": 1,
                "address.neighborhood": 1,
                "prestige.score": 1,
                "prestige.michelin_stars": 1,
                "experience.ambiance": 1,
                "experience.price_range": 1,
                "best_for.occasions": 1,
                "similarity_score": 1
            }
        },
        {"$sort": {"similarity_score": -1}},
        {"$limit": limit}
    ]
    
    # Execute search
    print("🔎 Executing vector search...")
    try:
        results = list(pois.aggregate(pipeline))
        print(f"✅ Found {len(results)} result(s)\n")
    except Exception as e:
        print(f"❌ Vector search failed: {e}\n")
        print("Make sure:")
        print("1. Vector search index 'vector_index' is created in Atlas")
        print("2. Embeddings are generated for POIs")
        print("3. Index is active and ready\n")
        return
    
    if not results:
        print("❌ No results found. Try:")
        print(f"  - Lowering min_score (current: {min_score})")
        print("  - Using different keywords")
        print("  - Checking if embeddings exist\n")
        return
    
    # Display results
    print("=" * 60)
    print("📊 RESULTS")
    print("=" * 60)
    
    for i, poi in enumerate(results, 1):
        stars = poi.get("prestige", {}).get("michelin_stars", 0)
        stars_str = "⭐" * stars if stars else "  "
        
        print(f"\n{i}. {poi['name']} {stars_str}")
        print(f"   🎯 Similarity: {poi['similarity_score']:.3f}")
        print(f"   📍 {poi.get('address', {}).get('neighborhood', 'N/A')}")
        print(f"   💰 {poi.get('experience', {}).get('price_range', 'N/A')}")
        
        cuisines = poi.get('subcategories', [])
        if cuisines:
            print(f"   🍽️  {', '.join(cuisines[:2])}")
        
        ambiance = poi.get('experience', {}).get('ambiance', [])
        if ambiance:
            print(f"   ✨ {', '.join(ambiance[:3])}")
        
        occasions = poi.get('best_for', {}).get('occasions', [])
        if occasions:
            print(f"   🎉 {', '.join(occasions[:2])}")
    
    print("\n" + "=" * 60)
    print("✅ Test complete!")
    
    mongo_client.close()


if __name__ == "__main__":
    # Test queries
    test_queries = [
        ("romantic and quiet with amazing views", 5, 0.7),
        ("lively spot for celebrating with friends", 5, 0.7),
        ("cozy rainy day comfort food", 5, 0.65),
        ("instagram-worthy brunch spot", 5, 0.65),
    ]
    
    print("\n" + "🧪 VECTOR SEARCH TEST SUITE" + "\n")
    
    for i, (query, limit, min_score) in enumerate(test_queries, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}/{len(test_queries)}")
        print(f"{'='*60}\n")
        test_vibe_search(query, limit, min_score)
        
        if i < len(test_queries):
            input("\n⏸️  Press Enter to continue to next test...")
    
    print("\n🎉 All tests complete!")
