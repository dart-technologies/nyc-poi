
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
    pois = client.pois.find({}, {"name": 1, "prestige": 1})
    for poi in pois:
        print(f"Name: {poi.get('name')}, Score: {poi.get('prestige', {}).get('score')}")
    client.close()
