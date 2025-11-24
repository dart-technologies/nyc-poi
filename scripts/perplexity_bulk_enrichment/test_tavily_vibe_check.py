#!/usr/bin/env python3
"""
Test Tavily Real-time Enrichment with Social Media Vibe Check
"""

import asyncio
import sys
import os

# Add parent directory to path to import from utils
sys.path.insert(0, '../../backend/mcp-server/src')

from utils.tavily_enrichment import enrich_poi_live


async def test_vibe_check():
    """Test real-time enrichment on Levain Bakery"""
    
    print("="*70)
    print("🔥 TAVILY REAL-TIME VIBE CHECK TEST")
    print("="*70)
    print("\nTarget: Levain Bakery - Famous NYC cookies")
    print("Location: 167 W 74th St, New York, NY 10023")
    print("\n" + "-"*70)
    print("⏳ Querying Tavily for latest buzz, social links, and vibe...\n")
    
    try:
        result = await enrich_poi_live(
            poi_name="Levain Bakery",
            poi_address="167 W 74th St, New York, NY 10023",
            category="bakery"
        )
        
        print(result)
        print("\n" + "="*70)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Check for API key
    if not os.getenv("TAVILY_API_KEY"):
        print("❌ TAVILY_API_KEY not found in environment")
        print("Trying to load from backend .env file...")
        
        # Try to load from backend .env
        import subprocess
        result = subprocess.run(
            ["grep", "TAVILY_API_KEY", "../../backend/mcp-server/.env"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            key = result.stdout.strip().split("=")[1]
            os.environ["TAVILY_API_KEY"] = key
            print(f"✅ Loaded API key: {key[:10]}...")
        else:
            print("❌ Could not load API key")
            sys.exit(1)
    
    asyncio.run(test_vibe_check())
