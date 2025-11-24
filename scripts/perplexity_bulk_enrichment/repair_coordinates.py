#!/usr/bin/env python3
"""
Repair Coordinates Script
Uses Perplexity to find precise [longitude, latitude] for POIs in MongoDB
"""

import asyncio
import os
import sys
import json
import re
import httpx
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv(".env")

# Add parent directory to path to import from data_pipeline
sys.path.append(str(Path(__file__).parent.parent / "data_pipeline"))

try:
    from import_to_mongodb import MongoDBClient
except ImportError:
    # Fallback if running from different location
    sys.path.append(str(Path(__file__).parent.parent.parent / "scripts" / "data_pipeline"))
    from import_to_mongodb import MongoDBClient

class CoordinateRepair:
    PERPLEXITY_BASE_URL = "https://api.perplexity.ai"
    
    def __init__(self):
        self.api_key = os.getenv("PERPLEXITY_API_KEY")
        if not self.api_key:
            raise ValueError("PERPLEXITY_API_KEY environment variable required")
            
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.mongo = MongoDBClient()
        self.updated_count = 0
        
    async def get_coordinates(self, name: str, address: str) -> Optional[List[float]]:
        """Query Perplexity for precise coordinates"""
        
        prompt = f"""Find the precise GPS coordinates for:
Name: {name}
Address: {address}

Return ONLY a JSON object with the coordinates in this exact format:
{{
  "coordinates": [longitude, latitude]
}}

Example:
{{
  "coordinates": [-73.9851, 40.7580]
}}

Ensure high precision (at least 4 decimal places). Do not include any other text."""

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.PERPLEXITY_BASE_URL}/chat/completions",
                    headers=self.headers,
                    json={
                        "model": "sonar",
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a geospatial expert. Provide precise JSON coordinates."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.0,
                        "max_tokens": 100
                    }
                )
                
                if response.status_code != 200:
                    print(f"   ✗ API Error: {response.status_code}")
                    return None
                    
                content = response.json()["choices"][0]["message"]["content"]
                
                # Extract JSON
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group(0))
                    coords = data.get("coordinates")
                    
                    # Validate coordinates (NYC bounds)
                    # Longitude: -74.3 to -73.7
                    # Latitude: 40.5 to 40.9
                    if (coords and len(coords) == 2 and 
                        -74.5 < coords[0] < -73.5 and 
                        40.4 < coords[1] < 41.0):
                        return coords
                    else:
                        print(f"   ⚠️  Out of bounds or invalid: {coords}")
                        return None
                
                return None
                
        except Exception as e:
            print(f"   ✗ Error fetching coords: {e}")
            return None

    async def run(self):
        """Main execution loop"""
        print("="*70)
        print("📍 POI Coordinate Repair Tool")
        print("="*70)
        
        if not self.mongo.connect():
            return
            
        # Fetch POIs with [0,0] coordinates
        pois = list(self.mongo.pois.find({"location.coordinates": [0, 0]}))
        print(f"Found {len(pois)} POIs to check...")
        
        for i, poi in enumerate(pois, 1):
            name = poi.get("name")
            address = poi.get("address", {}).get("street", "")
            current_loc = poi.get("location", {}).get("coordinates", [0, 0])
            
            print(f"\n[{i}/{len(pois)}] Processing: {name}")
            print(f"   Current: {current_loc}")
            
            # Get precise coords
            new_coords = await self.get_coordinates(name, address)
            
            if new_coords:
                # Update MongoDB
                self.mongo.pois.update_one(
                    {"_id": poi["_id"]},
                    {
                        "$set": {
                            "location": {
                                "type": "Point",
                                "coordinates": new_coords
                            },
                            "geocoded_at": "2025-11-23T11:30:00"
                        }
                    }
                )
                print(f"   ✅ Updated: {new_coords}")
                self.updated_count += 1
            else:
                print("   ❌ Failed to get precise coords")
            
            # Rate limiting
            await asyncio.sleep(1.5)
            
        print("\n" + "="*70)
        print(f"✨ Repair Complete! Updated {self.updated_count}/{len(pois)} POIs")
        self.mongo.close()

if __name__ == "__main__":
    asyncio.run(CoordinateRepair().run())
