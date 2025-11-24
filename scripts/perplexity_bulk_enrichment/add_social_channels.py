#!/usr/bin/env python3
"""
Post-process discovered POIs to add social media channels
Extracts Instagram, Yelp, Google Maps, OpenTable, Resy links from citations
"""

import json
import sys
from pathlib import Path
from social_channel_extractor import SocialChannelExtractor, enrich_poi_with_social


def process_pois_file(input_file: str, output_file: str = None):
    """Process a POI JSON file and add social channels"""
    
    input_path = Path(input_file)
    
    if not input_path.exists():
        print(f"❌ File not found: {input_file}")
        sys.exit(1)
    
    # Load POIs
    with open(input_path, 'r') as f:
        pois = json.load(f)
    
    print(f"📄 Processing {len(pois)} POIs from {input_path.name}")
    print(f"{'='*60}\n")
    
    # Track statistics
    stats = {
        "instagram": 0,
        "yelp": 0,
        "google_maps": 0,
        "twitter": 0,
        "opentable": 0,
        "resy": 0,
        "total_with_social": 0
    }
    
    # Process each POI
    enriched_pois = []
    for i, poi in enumerate(pois, 1):
        # Enrich with social channels
        enriched_poi = enrich_poi_with_social(poi)
        
        # Update statistics
        social = enriched_poi.get("contact", {}).get("social", {})
        if social:
            stats["total_with_social"] += 1
            for platform in ["instagram", "yelp", "google_maps", "twitter", "opentable", "resy"]:
                if platform in social or f"{platform}_handle" in social:
                    stats[platform] += 1
        
        enriched_pois.append(enriched_poi)
        
        # Show progress every 20 POIs
        if i % 20 == 0:
            print(f"   Processed {i}/{len(pois)} POIs...")
    
    # Save enriched POIs
    if not output_file:
        output_file = str(input_path).replace('.json', '_with_social.json')
    
    output_path = Path(output_file)
    with open(output_path, 'w') as f:
        json.dump(enriched_pois, f, indent=2)
    
    # Print statistics
    print(f"\n{'='*60}")
    print(f"✅ Enrichment Complete!")
    print(f"{'='*60}")
    print(f"Total POIs processed: {len(enriched_pois)}")
    print(f"POIs with social links: {stats['total_with_social']} ({stats['total_with_social']/len(enriched_pois)*100:.1f}%)")
    print(f"\nPlatform Breakdown:")
    print(f"  Instagram: {stats['instagram']} POIs")
    print(f"  Yelp: {stats['yelp']} POIs")
    print(f"  Google Maps: {stats['google_maps']} POIs")
    print(f"  Twitter/X: {stats['twitter']} POIs")
    print(f"  OpenTable: {stats['opentable']} POIs")
    print(f"  Resy: {stats['resy']} POIs")
    print(f"\n💾 Saved to: {output_path}")
    print(f"{'='*60}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 add_social_channels.py <input_file.json> [output_file.json]")
        print("\nExample:")
        print("  python3 add_social_channels.py data/production/discovered_pois.json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    process_pois_file(input_file, output_file)
