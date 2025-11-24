
import sys
from pathlib import Path
# Add backend/mcp-server to path
sys.path.append(str(Path(__file__).parent.parent.parent / "backend" / "mcp-server"))

from src.utils.mongodb import MongoDBClient
import os
from dotenv import load_dotenv

load_dotenv(".env")

# Map of POI names to prestige scores and michelin stars
UPDATES = {
    "Le Bernardin": {"score": 150, "michelin_stars": 3},
    "Jean-Georges": {"score": 100, "michelin_stars": 2},
    "Gabriel Kreuther": {"score": 100, "michelin_stars": 2},
    "Aquavit": {"score": 100, "michelin_stars": 2},
    "Sushi Noz": {"score": 100, "michelin_stars": 2},
    "Joo Ok": {"score": 50, "michelin_stars": 1},
    "Estela": {"score": 50, "michelin_stars": 1},
    "The Modern": {"score": 100, "michelin_stars": 2},
    "Per Se": {"score": 150, "michelin_stars": 3},
    "Eleven Madison Park": {"score": 150, "michelin_stars": 3},
    "Gramercy Tavern": {"score": 80, "michelin_stars": 1},
    "Balthazar": {"score": 40, "michelin_stars": 0},
    "Joe's Pizza": {"score": 25, "michelin_stars": 0},
    "Kossar’s Bialys": {"score": 20, "michelin_stars": 0},
    "Levain Bakery": {"score": 20, "michelin_stars": 0},
    "Carnegie Diner & Café": {"score": 10, "michelin_stars": 0}
}

client = MongoDBClient()
if client.connect():
    print("Updating prestige scores...")
    count = 0
    for name, data in UPDATES.items():
        result = client.pois.update_one(
            {"name": name},
            {"$set": {
                "prestige.score": data["score"],
                "prestige.michelin_stars": data["michelin_stars"]
            }}
        )
        if result.modified_count > 0:
            print(f"✅ Updated {name}: Score {data['score']}, Stars {data['michelin_stars']}")
            count += 1
        else:
            # Check if it exists but wasn't modified (already correct) or doesn't exist
            poi = client.pois.find_one({"name": name})
            if poi:
                print(f"ℹ️  {name} already up to date")
            else:
                print(f"⚠️  {name} not found in DB")
    
    print(f"\nTotal updated: {count}")
    client.close()
