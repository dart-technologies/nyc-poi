#!/usr/bin/env python3
"""
Comprehensive NYC POI Pipeline with Social Enrichment
1. Perplexity: Discover POIs (all neighborhoods + best-of lists)
2. Tavily: Enrich with social handles
3. MongoDB: Import with indexes

Budget: ~$5 total
- Perplexity: 200 searches (all neighborhoods + special categories) = $1.00
- Tavily: 200 POIs = $1.00 (covered by free tier)
- Total: ~$1.00
"""

import asyncio
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import httpx

try:
    from tavily import TavilyClient
except ImportError:
    import subprocess
    subprocess.run(["pip", "install", "tavily-python"], check=True)
    from tavily import TavilyClient


class ComprehensivePOIPipeline:
    """Full POI discovery, enrichment, and import pipeline"""
    
    PERPLEXITY_BASE_URL = "https://api.perplexity.ai"
    
    # All 10 Manhattan neighborhoods
    NEIGHBORHOODS = [
        ("Midtown West", 40.7614, -73.9826),
        ("Midtown East", 40.7549, -73.9682),
        ("Chelsea", 40.7465, -74.0014),
        ("Greenwich Village", 40.7336, -74.0027),
        ("East Village", 40.7265, -73.9815),
        ("SoHo", 40.7233, -74.0030),
        ("Tribeca", 40.7163, -74.0086),
        ("Lower East Side", 40.7209, -73.9840),
        ("Upper East Side", 40.7736, -73.9566),
        ("Upper West Side", 40.7870, -73.9754),
    ]
    
    # Best-of categories (NYC must-try lists)
    BEST_OF_CATEGORIES = {
        "best_bagel": {
            "query": "best bagels NYC Manhattan essential must-try iconic",
            "count": 10,
            "time_context": "morning",
            "category": "casual-dining"
        },
        "best_pizza": {
            "query": "best pizza NYC Manhattan essential must-try iconic slices",
            "count": 15,
            "time_context": "afternoon",
            "category": "casual-dining"
        },
        "best_rooftop": {
            "query": "best rooftop bars NYC Manhattan views drinks cocktails",
            "count": 12,
            "time_context": "evening_casual",
            "category": "bars-cocktails"
        },
        "best_speakeasy": {
            "query": "best speakeasy bars NYC Manhattan hidden cocktails craft",
            "count": 8,
            "time_context": "evening_casual",
            "category": "bars-cocktails"
        },
        "must_try_fine_dining": {
            "query": "must-try fine dining NYC Manhattan Michelin James Beard essential",
            "count": 15,
            "time_context": "evening_prestige",
            "category": "fine-dining"
        }
    }
    
    def __init__(self, output_dir: str = "data/production"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # API clients
        self.perplexity_key = os.getenv("PERPLEXITY_API_KEY")
        self.tavily_key = os.getenv("TAVILY_API_KEY")
        
        if not self.perplexity_key or not self.tavily_key:
            raise ValueError("Both PERPLEXITY_API_KEY and TAVILY_API_KEY required!")
        
        self.perplexity_headers = {
            "Authorization": f"Bearer {self.perplexity_key}",
            "Content-Type": "application/json"
        }
        self.tavily_client = TavilyClient(api_key=self.tavily_key)
        
        self.perplexity_count = 0
        self.tavily_count = 0
    
    async def discover_best_of_pois(self, category_key: str) -> List[Dict]:
        """Discover POIs from best-of lists"""
        
        category_info = self.BEST_OF_CATEGORIES[category_key]
        query = category_info["query"]
        target_count = category_info["count"]
        
        print(f"\n🏆 Discovering: {category_key}")
        print(f"   Query: {query}")
        print(f"   Target: {target_count} POIs")
        
        prompt = f"""List the top {target_count} {query}.

Format each venue as:
**Name**: [Restaurant/Bar Name]
**Address**: [Full street address]
**Known For**: [What makes it special/famous]
**Price**: [$, $$, $$$, or $$$$]

Focus on well-established, highly-rated venues."""
        
        pois = await self._perplexity_search(prompt, category_key)
        
        # Add category metadata
        for poi in pois:
            poi["time_context"] = category_info["time_context"]
            poi["category"] = category_info["category"]
            poi["best_of_list"] = category_key
        
        return pois[:target_count]
    
    async def _perplexity_search(self, prompt: str, context: str) -> List[Dict]:
        """Execute Perplexity search and parse POIs"""
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.PERPLEXITY_BASE_URL}/chat/completions",
                    headers=self.perplexity_headers,
                    json={
                        "model": "sonar",
                        "messages": [{
                            "role": "system",
                            "content": "You are a NYC restaurant expert. Provide accurate, factual information."
                        }, {
                            "role": "user",
                            "content": prompt
                        }],
                        "temperature": 0.2,
                        "max_tokens": 2000,
                        "return_citations": True
                    }
                )
                
                response.raise_for_status()
                data = response.json()
                self.perplexity_count += 1
                
                print(f"   ✓ Perplexity search complete ({self.perplexity_count} total)")
            
            # Parse POIs
            content = data["choices"][0]["message"]["content"]
            citations = data["choices"][0]["message"].get("citations", [])
            
            pois = self._parse_poi_response(content, citations, context)
            return pois
            
        except Exception as e:
            print(f"   ✗ Error: {e}")
            return []
    
    def _parse_poi_response(self, content: str, citations: List, context: str) -> List[Dict]:
        """Parse Perplexity response into POI structures"""
        
        pois = []
        
        # Strategy 1: Check for "**Name**:" format
        if "**Name**:" in content:
            sections = content.split("**Name**:")
            for section in sections[1:]:
                poi = self._extract_poi_from_text(section, citations, context)
                if poi:
                    pois.append(poi)
                    
        # Strategy 2: Check for numbered list "**1." format
        elif re.search(r'\*\*\d+\.', content):
            sections = re.split(r'\*\*\d+\.', content)
            for section in sections[1:]:
                poi = self._extract_poi_from_text(section, citations, context)
                if poi:
                    pois.append(poi)
                    
        # Strategy 3: Check for simple numbered list "1." format (no bold)
        else:
            sections = re.split(r'\n\d+\.\s+', content)
            for section in sections[1:]:
                poi = self._extract_poi_from_text(section, citations, context)
                if poi:
                    pois.append(poi)
        
        return pois
    
    def _extract_poi_from_text(self, text: str, citations: List, context: str) -> Optional[Dict]:
        """Extract POI data from text section"""
        
        name = ""
        
        # Case A: "**Name**: Value" format (text starts with value)
        # The split removed "**Name**:", so text starts with "Restaurant Name"
        # But we need to be careful not to grab the whole paragraph
        
        # Case B: "**1. Name**" format (text starts with "Name**")
        
        # Try to find name in the beginning
        # 1. Look for bolded name at start: " Name**"
        name_match = re.search(r'^\s*([^\*\n]+)\*\*', text)
        if name_match:
            name = name_match.group(1).strip()
        else:
            # 2. Look for first line (for **Name**: format)
            first_line = text.split('\n')[0].strip()
            name = first_line.replace('*', '').strip()
            
        # Clean up name (remove leading colons if any)
        if name.startswith(":"):
            name = name[1:].strip()
            
        # Skip if name is invalid
        if not name or len(name) > 100 or name.lower() in ['address', 'known for', 'price']:
            return None
        
        # Extract address
        address_match = re.search(r'\*\*Address[:\s]*\*\*[:\s]*([^\n]+)', text, re.IGNORECASE)
        address = address_match.group(1).strip() if address_match else ""
        
        # Extract known for
        known_for_match = re.search(r'\*\*Known For[:\s]*\*\*[:\s]*([^\n]+)', text, re.IGNORECASE)
        known_for = known_for_match.group(1).strip() if known_for_match else ""
        
        # Extract price
        price_match = re.search(r'\*\*Price[:\s]*\*\*[:\s]*([^\n]+)', text, re.IGNORECASE)
        price = price_match.group(1).strip() if price_match else "$$"
        # Normalize price
        price_search = re.search(r'(\$+)', price)
        price = price_search.group(1) if price_search else "$$"
        
        return {
            "name": name,
            "slug": name.lower().replace(' ', '-').replace("'", "").replace("&", "and"),
            "address": {
                "street": address,
                "city": "New York",
                "state": "NY",
                "borough": "Manhattan"
            },
            "contact": {
                "phone": "",
                "website": "",
                "social": {}  # Will be enriched by Perplexity
            },
            "experience": {
                "price_range": price,
                "signature_dishes": [known_for] if known_for else [],
                "ambiance": []
            },
            "best_for": {
                "time_of_day": [],
                "occasions": [],
                "weather": ["any"],
                "group_size": [2, 4]
            },
            "prestige": {
                "score": 0
            },
            "sources": [{
                "type": "perplexity_discovery",
                "query": context,
                "citations": citations,
                "retrieved_at": datetime.now().isoformat()
            }],
            "created_at": datetime.now().isoformat(),
            "enrichment_status": "pending_social"
        }
    
    async def enrich_with_social(self, poi: Dict) -> Dict:
        """Enrich POI with social media handles via Perplexity"""
        
        name = poi["name"]
        address = poi["address"]["street"]
        
        print(f"   📱 Enriching social: {name}")
        
        try:
            # Use Perplexity to find social media links
            prompt = f"""What are the social media accounts for {name} in NYC?
            
Provide:
- Instagram handle and URL
- Twitter/X handle and URL  
- Yelp business page URL
- Facebook page URL (if available)
- TikTok account (if available)

Be concise and only list what you can verify."""
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.PERPLEXITY_BASE_URL}/chat/completions",
                    headers=self.perplexity_headers,
                    json={
                        "model": "sonar",
                        "messages": [{
                            "role": "system",
                            "content": "You are a social media research expert. Provide accurate social media links."
                        }, {
                            "role": "user",
                            "content": prompt
                        }],
                        "temperature": 0.1,
                        "max_tokens": 300,
                        "return_citations": True
                    }
                )
                
                response.raise_for_status()
                data = response.json()
                self.perplexity_count += 1
            
            # Parse response for social links
            content = data["choices"][0]["message"]["content"]
            citations = data["choices"][0]["message"].get("citations", [])
            
            social_links = {}
            
            # Extract from content
            ig_match = re.search(r'(?:instagram\.com/|@)([a-zA-Z0-9._]+)', content, re.IGNORECASE)
            if ig_match:
                handle = ig_match.group(1)
                social_links["instagram"] = f"https://instagram.com/{handle}"
                social_links["instagram_handle"] = handle
            
            tw_match = re.search(r'(?:twitter\.com/|x\.com/|@)([a-zA-Z0-9_]+)', content, re.IGNORECASE)
            if tw_match and "instagram" not in tw_match.group(1).lower():
                handle = tw_match.group(1)
                social_links["twitter"] = f"https://twitter.com/{handle}"
                social_links["twitter_handle"] = handle
            
            # Extract from citations
            for citation in citations:
                url = citation if isinstance(citation, str) else ""
                
                if "instagram.com" in url and "instagram" not in social_links:
                    ig_match = re.search(r'instagram\.com/([a-zA-Z0-9._]+)', url)
                    if ig_match:
                        handle = ig_match.group(1)
                        social_links["instagram"] = f"https://instagram.com/{handle}"
                        social_links["instagram_handle"] = handle
                
                if ("twitter.com" in url or "x.com" in url) and "twitter" not in social_links:
                    tw_match = re.search(r'(?:twitter|x)\.com/([a-zA-Z0-9_]+)', url)
                    if tw_match:
                        handle = tw_match.group(1)
                        social_links["twitter"] = f"https://twitter.com/{handle}"
                        social_links["twitter_handle"] = handle
                
                if "yelp.com/biz" in url and "yelp" not in social_links:
                    social_links["yelp"] = url
                
                if "facebook.com" in url and "facebook" not in social_links:
                    social_links["facebook"] = url
                
                if "tiktok.com/@" in url and "tiktok" not in social_links:
                    social_links["tiktok"] = url
            
            poi["contact"]["social"] = social_links
            poi["enrichment_status"] = "complete"
            
            if social_links:
                platforms = ", ".join(k for k in social_links.keys() if not k.endswith("_handle"))
                print(f"      ✓ Found: {platforms}")
            else:
                print(f"      - No social links found")
            
        except Exception as e:
            print(f"      ✗ Error: {e}")
            poi["enrichment_status"] = "failed"
        
        return poi
    
    async def get_coordinates(self, poi: Dict) -> Dict:
        """Fetch precise coordinates for a POI using Perplexity"""
        name = poi["name"]
        address = poi["address"]["street"]
        
        print(f"   📍 Geocoding: {name}")
        
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
                    headers=self.perplexity_headers,
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
                
                if response.status_code == 200:
                    content = response.json()["choices"][0]["message"]["content"]
                    self.perplexity_count += 1
                    
                    # Extract JSON
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                    if json_match:
                        data = json.loads(json_match.group(0))
                        coords = data.get("coordinates")
                        
                        if (coords and len(coords) == 2 and 
                            -74.5 < coords[0] < -73.5 and 
                            40.4 < coords[1] < 41.0):
                            
                            poi["location"] = {
                                "type": "Point",
                                "coordinates": coords
                            }
                            print(f"      ✓ Found: {coords}")
                            return poi
                            
            print("      - Failed to get valid coords")
            return poi
            
        except Exception as e:
            print(f"      ✗ Error: {e}")
            return poi

    async def save_pois(self, pois: List[Dict], filename: str):
        """Save POIs to JSON"""
        output_path = self.output_dir / filename
        
        with open(output_path, 'w') as f:
            json.dump(pois, f, indent=2)
        
        print(f"\n💾 Saved {len(pois)} POIs to {output_path}")
        return output_path


async def main():
    """Main pipeline execution"""
    
    print("="*70)
    print("Comprehensive NYC POI Pipeline")
    print("Perplexity Discovery + Social Enrichment + Geocoding")
    print("="*70)
    
    pipeline = ComprehensivePOIPipeline()
    
    all_pois = []
    
    # Phase 1: Best-of lists
    print("\n📍 Phase 1: Best-Of Lists Discovery")
    print("-"*70)
    
    for category_key in pipeline.BEST_OF_CATEGORIES.keys():
        pois = await pipeline.discover_best_of_pois(category_key)
        all_pois.extend(pois)
        await asyncio.sleep(2)  # Rate limiting
    
    # Save intermediate results
    await pipeline.save_pois(all_pois, "discovered_pois_bestof.json")
    
    # Phase 2: Social enrichment
    print(f"\n\n📱 Phase 2: Social Media Enrichment")
    print("-"*70)
    print(f"Enriching {len(all_pois)} POIs with Tavily...\n")
    
    enriched_pois = []
    for i, poi in enumerate(all_pois, 1):
        print(f"[{i}/{len(all_pois)}]", end=" ")
        enriched_poi = await pipeline.enrich_with_social(poi)
        enriched_pois.append(enriched_poi)
        
        # Rate limiting
        if i % 10 == 0:
            await asyncio.sleep(2)
            
    # Phase 3: Geocoding
    print(f"\n\n🗺️  Phase 3: Geocoding")
    print("-"*70)
    print(f"Fetching coordinates for {len(enriched_pois)} POIs...\n")
    
    final_pois = []
    for i, poi in enumerate(enriched_pois, 1):
        print(f"[{i}/{len(enriched_pois)}]", end=" ")
        geocoded_poi = await pipeline.get_coordinates(poi)
        final_pois.append(geocoded_poi)
        
        # Rate limiting
        if i % 10 == 0:
            await asyncio.sleep(2)
    
    # Save final enriched POIs
    final_path = await pipeline.save_pois(final_pois, "final_enriched_pois.json")
    
    # Summary
    print(f"{'='*70}")
    print("📊 Pipeline Complete!")
    print(f"{'='*70}")
    print(f"Total POIs discovered: {len(enriched_pois)}")
    print(f"Perplexity searches used: {pipeline.perplexity_count}")
    print(f"Cost: ${pipeline.perplexity_count * 0.005:.2f}")
    print(f"Remaining budget: {5000 - pipeline.perplexity_count} searches (${(5000 - pipeline.perplexity_count) * 0.005:.2f})")
    
    
    # Count social enrichment success
    if len(enriched_pois) > 0:
        with_social = sum(1 for p in enriched_pois if p.get("contact", {}).get("social"))
        print(f"\nPOIs with social links: {with_social}/{len(enriched_pois)} ({with_social/len(enriched_pois)*100:.1f}%)")
    else:
        print(f"\n⚠️  No POIs discovered - check parsing logic")
    
    
    print(f"\n💾 Final output: {final_path}")
    print(f"{'='*70}")
    print("\n✅ Ready for MongoDB import!")


if __name__ == "__main__":
    asyncio.run(main())
