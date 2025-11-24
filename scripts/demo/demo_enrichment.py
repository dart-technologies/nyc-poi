#!/usr/bin/env python3
"""
Standalone Tavily Enrichment Demo
Shows Thanksgiving-aware POI enrichment in action
"""

import asyncio
import sys
import os

# Add project to path
# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend" / "mcp-server"))

from src.utils.tavily_enrichment import TavilyEnricher
from datetime import datetime


async def demo_enrichment():
    """Demo the Tavily enrichment with rich output"""
    
    print("=" * 80)
    print("🦃 TAVILY REAL-TIME POI ENRICHMENT DEMO")
    print("=" * 80)
    print()
    
    # Create enricher
    enricher = TavilyEnricher()
    
    # Test POI
    poi_name = "Le Bernardin"
    poi_address = "155 W 51st St, New York, NY"
    
    print(f"📍 POI: {poi_name}")
    print(f"📮 Address: {poi_address}")
    print(f"⏰ Time: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    print()
    print("🔍 Searching the web with Tavily...")
    print()
    
    # Run enrichment
    result = await enricher.enrich_poi(
        poi_name=poi_name,
        poi_address=poi_address,
        category="fine-dining"
    )
    
    print("=" * 80)
    print("✅ ENRICHMENT COMPLETE")
    print("=" * 80)
    print()
    
    # Display results
    if result.get('holiday_hours'):
        print("🦃 HOLIDAY HOURS:")
        print(result['holiday_hours'])
        print()
    
    if result.get('special_events'):
        print("🍽️  SPECIAL EVENTS:")
        print(result['special_events'])
        print()
    
    if result.get('recent_news'):
        print("📰 RECENT NEWS:")
        print(result['recent_news'])
        print()
    
    if result.get('social_buzz'):
        print("📱 SOCIAL BUZZ:")
        print(result['social_buzz'])
        print()
    
    if result.get('current_availability'):
        print("🎫 RESERVATIONS:")
        print(result['current_availability'])
        print()
    
    if result.get('latest_recognition'):
        print("🏆 LATEST RECOGNITION:")
        print(result['latest_recognition'])
        print()
    
    print("=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)
    print(f"Enrichment fields populated: {sum(1 for k, v in result.items() if v and k != 'citations')}")
    print(f"Total citations: {len(result.get('citations', []))}")
    print()
    print("🎯 This is the LIVE DATA that Google Maps doesn't have!")
    print()


if __name__ == "__main__":
    print("\n\n")
    asyncio.run(demo_enrichment())
    print("\n\n")
