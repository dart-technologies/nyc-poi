#!/usr/bin/env python3
"""
Import Production Data to MongoDB
Merges discovered POIs and enriched POIs, then imports to MongoDB Atlas
"""

import json
import asyncio
import os
import sys
from pathlib import Path
from typing import List, Dict

# Add parent directory to path to import from data_pipeline
sys.path.append(str(Path(__file__).parent))

from import_to_mongodb import MongoDBClient, validate_poi_schema, enrich_pois_with_metadata

def load_production_data() -> List[Dict]:
    """Load and merge all production data files"""
    
    base_path = Path(__file__).parent.parent.parent / "data" / "production"
    
    files = [
        base_path / "discovered_pois.json",
        base_path / "final_enriched_pois.json"
    ]
    
    all_pois = []
    seen_slugs = set()
    
    print(f"📂 Loading production data from {base_path}...")
    
    for file_path in files:
        if not file_path.exists():
            print(f"⚠️  File not found: {file_path}")
            continue
            
        try:
            with open(file_path, 'r') as f:
                pois = json.load(f)
                
            print(f"   Loaded {len(pois)} POIs from {file_path.name}")
            
            for poi in pois:
                # Basic validation
                if not poi.get("name"):
                    continue
                
                # Generate slug if missing
                if "slug" not in poi:
                    poi["slug"] = poi["name"].lower().replace(" ", "-").replace("'", "").replace("&", "and")
                
                # Deduplicate by slug
                if poi["slug"] in seen_slugs:
                    continue
                
                seen_slugs.add(poi["slug"])
                all_pois.append(poi)
                
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON in {file_path.name}")
        except Exception as e:
            print(f"❌ Error loading {file_path.name}: {e}")
            
    print(f"✅ Total unique POIs loaded: {len(all_pois)}")
    return all_pois

# Neighborhood centroids for fallback geocoding
NEIGHBORHOOD_COORDS = {
    "Midtown": [-73.9840, 40.7549],
    "Chelsea": [-74.0014, 40.7465],
    "Greenwich Village": [-74.0027, 40.7336],
    "East Village": [-73.9815, 40.7265],
    "SoHo": [-74.0030, 40.7233],
    "Tribeca": [-74.0086, 40.7163],
    "Lower East Side": [-73.9840, 40.7209],
    "Upper East Side": [-73.9566, 40.7736],
    "Upper West Side": [-73.9754, 40.7870],
    "Harlem": [-73.9465, 40.8116],
    "Financial District": [-74.0090, 40.7074],
    "Times Square": [-73.9851, 40.7580],
    "Hell's Kitchen": [-73.9918, 40.7638],
    "Chinatown": [-73.9973, 40.7158],
    "Little Italy": [-73.9962, 40.7191],
    "NoHo": [-73.9924, 40.7256],
    "Flatiron": [-73.9897, 40.7411],
    "Gramercy": [-73.9837, 40.7367],
    "Murray Hill": [-73.9776, 40.7477]
}

def fix_coordinates(poi: Dict) -> Dict:
    """Attempt to fix [0,0] coordinates using address/neighborhood"""
    
    # Check if coordinates are missing or invalid
    loc = poi.get("location", {})
    coords = loc.get("coordinates", [0, 0])
    
    if coords == [0, 0] or not coords:
        # Try to find neighborhood in address or tags
        address_str = f"{poi.get('address', {}).get('street', '')} {poi.get('address', {}).get('neighborhood', '')}"
        
        found_coords = None
        for name, (lon, lat) in NEIGHBORHOOD_COORDS.items():
            if name.lower() in address_str.lower():
                # Add small random jitter to prevent overlap
                import random
                jitter_lat = random.uniform(-0.002, 0.002)
                jitter_lon = random.uniform(-0.002, 0.002)
                found_coords = [lon + jitter_lon, lat + jitter_lat]
                break
        
        if found_coords:
            poi["location"] = {
                "type": "Point",
                "coordinates": found_coords
            }
            print(f"   📍 Fixed coords for '{poi['name']}' -> {found_coords}")
        else:
            # Default to Midtown center if completely unknown
            poi["location"] = {
                "type": "Point",
                "coordinates": [-73.9851, 40.7580]
            }
            print(f"   ⚠️  Defaulted coords for '{poi['name']}' to Midtown")
            
    return poi

async def main():
    """Main import execution"""
    
    print("="*70)
    print("Production Data Import to MongoDB")
    print("="*70)
    
    # 1. Load Data
    pois = load_production_data()
    
    if not pois:
        print("❌ No data found to import!")
        return
        
    # 2. Fix Coordinates
    print("\n📍 Fixing Coordinates...")
    fixed_pois = [fix_coordinates(p) for p in pois]
    
    # 3. Validate (Lenient)
    print("\n🔍 Validating Schema...")
    # Skip strict validation in import_to_mongodb and just check essentials
    valid_pois = []
    for p in fixed_pois:
        if p.get("name"):
            valid_pois.append(p)
            
    print(f"   Valid POIs: {len(valid_pois)}/{len(pois)}")
    
    # 4. Enrich Metadata
    print("\n✨ Enriching Metadata...")
    enriched_pois = enrich_pois_with_metadata(valid_pois)
    
    # 5. Connect to MongoDB
    print("\n🔌 Connecting to MongoDB...")
    mongo = MongoDBClient()
    if not mongo.connect():
        return
        
    # 6. Setup Indexes
    mongo.setup_indexes()
    
    # 7. Import (Replace All)
    print("\n💾 Importing to MongoDB (Replacing existing collection)...")
    mongo.import_pois(enriched_pois, replace_all=True)
    
    # 7. Verify
    print("\n📊 Verification Stats:")
    stats = mongo.get_collection_stats()
    print(f"   Total Documents: {stats.get('total_pois', 0)}")
    
    mongo.close()
    print("\n✅ Import Complete!")

if __name__ == "__main__":
    asyncio.run(main())
