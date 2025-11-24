#!/usr/bin/env python3
"""
Generate OpenAI embeddings for all POIs in MongoDB.

This script creates rich text descriptions from POI data and generates
embeddings using OpenAI's text-embedding-3-small model for semantic search.

Usage:
    python3 generate_embeddings.py
    python3 generate_embeddings.py --dry-run  # Preview without updating
"""

import os
import sys
import argparse
from typing import List, Dict, Any
from pymongo import MongoClient
from openai import OpenAI
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend/mcp-server'))
from src.config import config

load_dotenv()


def create_embedding_text(poi: Dict[str, Any]) -> str:
    """
    Create rich text description for embedding generation.
    
    Combines multiple POI fields to create a comprehensive description
    that captures the essence and vibe of the restaurant.
    """
    parts = []
    
    # Name and category
    parts.append(f"{poi.get('name', '')} is a {poi.get('category', 'restaurant')}")
    
    # Subcategories (cuisine types)
    subcategories = poi.get('subcategories', [])
    if subcategories:
        parts.append(f"specializing in {', '.join(subcategories)}")
    
    # Location/neighborhood
    address = poi.get('address', {})
    neighborhood = address.get('neighborhood', '')
    if neighborhood:
        parts.append(f"located in {neighborhood}")
    
    # Prestige markers
    prestige = poi.get('prestige', {})
    michelin_stars = prestige.get('michelin_stars', 0)
    if michelin_stars:
        parts.append(f"with {michelin_stars} Michelin star{'s' if michelin_stars > 1 else ''}")
    
    # Experience details
    experience = poi.get('experience', {})
    ambiance = experience.get('ambiance', [])
    if ambiance:
        parts.append(f"The ambiance is {', '.join(ambiance)}")
    
    noise_level = experience.get('noise_level', '')
    if noise_level:
        parts.append(f"with a {noise_level} noise level")
    
    price_range = experience.get('price_range', '')
    if price_range:
        parts.append(f"Price range: {price_range}")
    
    # Signature dishes
    signature_dishes = experience.get('signature_dishes', [])
    if signature_dishes:
        parts.append(f"Known for {', '.join(signature_dishes[:3])}")  # Top 3
    
    # Best for (occasions and vibes)
    best_for = poi.get('best_for', {})
    occasions = best_for.get('occasions', [])
    if occasions:
        parts.append(f"Perfect for {', '.join(occasions)}")
    
    # Join all parts into cohesive text
    embedding_text = '. '.join(parts) + '.'
    
    return embedding_text


def generate_embeddings(dry_run: bool = False) -> None:
    """
    Generate embeddings for all POIs in MongoDB.
    
    Args:
        dry_run: If True, preview embedding text without updating database
    """
    print("🔌 Connecting to MongoDB Atlas...")
    mongo_client = MongoClient(
        config.mongodb.uri,
        maxPoolSize=config.mongodb.max_pool_size,
        serverSelectionTimeoutMS=config.mongodb.server_selection_timeout_ms
    )
    
    db = mongo_client[config.mongodb.database]
    pois_collection = db[config.mongodb.pois_collection]
    
    # Fetch POIs that don't have embeddings
    query = {"embedding": {"$exists": False}}
    pois = list(pois_collection.find(query))
    total_pois = len(pois)
    
    print(f"📊 Found {total_pois} POIs without embeddings")
    
    if total_pois == 0:
        print("✅ All POIs already have embeddings!")
        return
    
    if dry_run:
        print("\n🔍 DRY RUN MODE - Previewing embedding text generation:\n")
        for i, poi in enumerate(pois[:5], 1):  # Show first 5
            embedding_text = create_embedding_text(poi)
            print(f"{i}. {poi.get('name', 'Unknown')}")
            print(f"   Text: {embedding_text[:200]}...")
            print()
        print(f"💡 Run without --dry-run to generate embeddings for all {total_pois} POIs")
        return
    
    print("🤖 Initializing OpenAI client...")
    openai_client = OpenAI(api_key=config.openai.api_key)
    
    print(f"⚡ Generating embeddings using {config.openai.embedding_model}...\n")
    
    success_count = 0
    error_count = 0
    
    for i, poi in enumerate(pois, 1):
        poi_id = poi.get('_id')
        poi_name = poi.get('name', 'Unknown')
        
        try:
            # Create embedding text
            embedding_text = create_embedding_text(poi)
            
            # Generate embedding
            response = openai_client.embeddings.create(
                model=config.openai.embedding_model,
                input=embedding_text,
                dimensions=config.openai.embedding_dimensions
            )
            
            embedding_vector = response.data[0].embedding
            
            # Update MongoDB document
            pois_collection.update_one(
                {"_id": poi_id},
                {
                    "$set": {
                        "embedding": embedding_vector,
                        "embedding_text": embedding_text,
                        "embedding_model": config.openai.embedding_model,
                        "embedding_dimensions": config.openai.embedding_dimensions
                    }
                }
            )
            
            success_count += 1
            print(f"✅ [{i}/{total_pois}] {poi_name}")
            
        except Exception as e:
            error_count += 1
            print(f"❌ [{i}/{total_pois}] {poi_name}: {str(e)}")
    
    print(f"\n🎉 Embedding generation complete!")
    print(f"   ✅ Success: {success_count}")
    print(f"   ❌ Errors: {error_count}")
    print(f"\n📝 Next steps:")
    print(f"   1. Create vector search index in MongoDB Atlas UI")
    print(f"   2. Index name: 'vector_index'")
    print(f"   3. Field path: 'embedding'")
    print(f"   4. Dimensions: {config.openai.embedding_dimensions}")
    print(f"   5. Similarity: cosine")
    
    mongo_client.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate embeddings for POIs")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview embedding text without updating database"
    )
    
    args = parser.parse_args()
    
    try:
        generate_embeddings(dry_run=args.dry_run)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)
