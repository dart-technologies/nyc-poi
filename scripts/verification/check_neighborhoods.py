
import sys
from pathlib import Path
# Add backend/mcp-server to path
sys.path.append(str(Path(__file__).parent.parent.parent / "backend" / "mcp-server"))

from src.utils.mongodb import MongoDBClient
import os
from dotenv import load_dotenv
from collections import Counter

load_dotenv(".env")

client = MongoDBClient()
if client.connect():
    pois = client.pois.find({}, {"address.neighborhood": 1, "address.borough": 1})
    
    neighborhoods = Counter()
    boroughs = Counter()
    
    for poi in pois:
        addr = poi.get("address", {})
        neighborhoods[addr.get("neighborhood", "Unknown")] += 1
        boroughs[addr.get("borough", "Unknown")] += 1
    
    print("\n📊 Current Neighborhood Coverage:")
    for hood, count in neighborhoods.most_common():
        print(f"  {hood}: {count}")
        
    print("\n🏙️  Borough Breakdown:")
    for boro, count in boroughs.most_common():
        print(f"  {boro}: {count}")
        
    client.close()
