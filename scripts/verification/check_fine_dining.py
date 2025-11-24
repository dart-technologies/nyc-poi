
import sys
from pathlib import Path
# Add backend/mcp-server to path
sys.path.append(str(Path(__file__).parent.parent.parent / "backend" / "mcp-server"))

from src.utils.mongodb import MongoDBClient
import os
from dotenv import load_dotenv

load_dotenv(".env")

client = MongoDBClient()
if client.connect():
    # Count total fine-dining
    total_fine_dining = client.pois.count_documents({"category": "fine-dining"})
    print(f"Total 'fine-dining' POIs: {total_fine_dining}")
    
    # Count with high prestige
    high_prestige = client.pois.count_documents({"prestige.score": {"$gte": 100}})
    print(f"POIs with prestige score >= 100: {high_prestige}")
    
    # Count with Michelin stars
    michelin = client.pois.count_documents({"prestige.michelin_stars": {"$gt": 0}})
    print(f"POIs with Michelin stars > 0: {michelin}")
    
    # List a few fine-dining examples
    print("\nSample 'fine-dining' POIs:")
    cursor = client.pois.find({"category": "fine-dining"}).limit(10)
    for poi in cursor:
        print(f"- {poi['name']}: Score={poi.get('prestige', {}).get('score')}, Stars={poi.get('prestige', {}).get('michelin_stars')}")
        print(f"  Coords: {poi.get('location', {}).get('coordinates')}")
        
    client.close()
