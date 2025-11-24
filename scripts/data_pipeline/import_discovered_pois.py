
import json
import os
from pathlib import Path
import sys
# Add backend/mcp-server to path
sys.path.append(str(Path(__file__).parent.parent.parent / "backend" / "mcp-server"))

from src.utils.mongodb import MongoDBClient
from dotenv import load_dotenv

load_dotenv(".env")

def import_discovered_pois():
    """Import discovered POIs from JSON to MongoDB"""
    
    # Load JSON
    json_path = Path("../../data/production/discovered_pois.json")
    if not json_path.exists():
        print(f"❌ File not found: {json_path}")
        return
        
    with open(json_path, 'r') as f:
        pois = json.load(f)
        
    print(f"📦 Loaded {len(pois)} POIs from {json_path}")
    
    # Connect to MongoDB
    client = MongoDBClient()
    if not client.connect():
        print("❌ Failed to connect to MongoDB")
        return
        
    # Import
    count = 0
    duplicates = 0
    errors = 0
    
    for poi in pois:
        try:
            # Upsert (update if exists, insert if new)
            client.pois.update_one(
                {"name": poi["name"]},
                {"$set": poi},
                upsert=True
            )
            count += 1
            
        except Exception as e:
            print(f"❌ Error importing {poi.get('name')}: {e}")
            errors += 1
            
    print("\n📊 Import Summary")
    print("="*30)
    print(f"✅ Imported: {count}")
    print(f"⚠️  Duplicates: {duplicates}")
    print(f"❌ Errors: {errors}")
    print("="*30)
    
    client.close()

if __name__ == "__main__":
    import_discovered_pois()
