"""
Production-Quality POI Enrichment with Perplexity Sonar API
Budget: $25 (5,000 searches) for comprehensive Manhattan food spots

Strategy:
1. Phase 1: Discover ~500 Manhattan POIs (1,000 searches)
2. Phase 2: Deep enrichment for top 250 POIs (2,500 searches @ ~10/POI)
3. Phase 3: Import to MongoDB with quality filtering

Time-of-Day Contextualization:
- Morning: Bagels, coffee, breakfast (7am-11am)
- Afternoon: Pizza, lunch spots (11am-3pm)
- Evening Casual: Happy hour, bars (5pm-7pm)
- Evening Prestige: Michelin dinner (6pm-10pm)
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import httpx
from dotenv import load_dotenv

# Load .env file
load_dotenv(".env")


class ProductionPOIEnricher:
    """Perplexity-powered production POI enrichment"""
    
    BASE_URL = "https://api.perplexity.ai"
    
    # Manhattan neighborhoods to cover
    NEIGHBORHOODS = [
        ("Midtown West", 40.7614, -73.9826),  # Times Square/1633 Broadway
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
    
    # Time-of-day categories
    TIME_CATEGORIES = {
        "morning": {
            "time_range": "7am-11am",
            "keywords": ["bagels", "breakfast", "coffee", "bakery", "brunch"],
            "count_per_neighborhood": 5
        },
        "afternoon": {
            "time_range": "11am-3pm",
            "keywords": ["pizza", "lunch", "sandwich", "salad", "quick bite"],
            "count_per_neighborhood": 8
        },
        "evening_casual": {
            "time_range": "5pm-7pm",
            "keywords": ["happy hour", "cocktail bar", "wine bar", "after work"],
            "count_per_neighborhood": 6
        },
        "evening_prestige": {
            "time_range": "6pm-10pm",
            "keywords": ["fine dining", "Michelin star", "upscale restaurant", "special occasion"],
            "count_per_neighborhood": 6
        }
    }
    
    def __init__(self, api_key: str, output_dir: str = "data/production"):
        self.api_key = api_key
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        self.search_count = 0  # Track API usage
        self.budget_limit = 5000  # $25 budget
        
        print(f"✅ Perplexity client initialized")
        print(f"   Budget: {self.budget_limit} searches ($25.00)")
    
    async def discover_pois_by_context(
        self,
        neighborhood: str,
        lat: float,
        lon: float,
        time_slot: str
    ) -> List[Dict]:
        """Discover POIs for a specific neighborhood and time context"""
        
        category_info = self.TIME_CATEGORIES[time_slot]
        keywords = category_info["keywords"]
        target_count = category_info["count_per_neighborhood"]
        
        print(f"\n🔍 Discovering {time_slot} POIs in {neighborhood}")
        print(f"   Keywords: {', '.join(keywords)}")
        print(f"   Target: {target_count} POIs")
        
        # Build discovery prompt
        prompt = self._build_discovery_prompt(neighborhood, keywords, time_slot)
        
        # Call Perplexity
        pois = await self._search_and_extract(prompt, neighborhood, time_slot)
        
        return pois[:target_count]
    
    def _build_discovery_prompt(
        self,
        neighborhood: str,
        keywords: List[str],
        time_slot: str
    ) -> str:
        """Build discovery prompt for Perplexity"""
        
        keyword_str = ", ".join(keywords)
        
        return f"""List the best {keyword_str} in {neighborhood}, Manhattan, NYC.

Format each venue as:
**Name**: [Restaurant/Bar Name]
**Address**: [Full street address]
**Hours**: [Operating hours or "varies"]
**Phone**: [Phone number or "N/A"]
**Known For**: [1-2 signature items or specialties]
**Price**: [$, $$, $$$, or $$$$]

List 8-10 venues. Focus on popular, well-reviewed establishments."""
    
    async def _search_and_extract(
        self,
        prompt: str,
        neighborhood: str,
        time_slot: str
    ) -> List[Dict]:
        """Search Perplexity and extract structured POI data"""
        
        if self.search_count >= self.budget_limit:
            print(f"⚠️  Budget limit reached ({self.budget_limit} searches)")
            return []
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.BASE_URL}/chat/completions",
                    headers=self.headers,
                    json={
                        "model": "sonar",
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a NYC restaurant expert. Provide accurate, factual information with complete details."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.2,
                        "max_tokens": 1500,
                        "return_citations": True,
                        "search_recency_filter": "month"
                    }
                )
                
                response.raise_for_status()
                data = response.json()
                self.search_count += 1
                
                print(f"   ✓ Search complete ({self.search_count}/{self.budget_limit} used)")
            
            # Parse response into POI structures
            pois = self._parse_discovery_response(
                data,
                neighborhood,
                time_slot
            )
            
            return pois
            
        except Exception as e:
            print(f"   ✗ Error: {e}")
            return []
    
    def _parse_discovery_response(
        self,
        api_response: Dict,
        neighborhood: str,
        time_slot: str
    ) -> List[Dict]:
        """Parse Perplexity response into POI structures"""
        
        try:
            content = api_response["choices"][0]["message"]["content"]
            citations = api_response["choices"][0]["message"].get("citations", [])
            
            pois = []
            
            # Simple parsing: split by "**Name**:"
            sections = content.split("**Name**:")
            
            for section in sections[1:]:  # Skip first empty section
                poi = self._extract_poi_from_section(
                    section,
                    neighborhood,
                    time_slot,
                    citations
                )
                if poi:
                    pois.append(poi)
            
            return pois
            
        except Exception as e:
            print(f"   ⚠️  Parse error: {e}")
            return []
    
    def _extract_poi_from_section(
        self,
        section: str,
        neighborhood: str,
        time_slot: str,
        citations: List[str]
    ) -> Optional[Dict]:
        """Extract POI data from a section of text"""
        
        import re
        
        # Extract name
        name_match = re.search(r'^([^\n*]+)', section)
        if not name_match:
            return None
        name = name_match.group(1).strip()
        
        # Extract address
        address_match = re.search(r'\*\*Address\*\*:\s*([^\n]+)', section)
        address = address_match.group(1).strip() if address_match else ""
        
        # Extract hours
        hours_match = re.search(r'\*\*Hours\*\*:\s*([^\n]+)', section)
        hours = hours_match.group(1).strip() if hours_match else "varies"
        
        # Extract phone
        phone_match = re.search(r'\*\*Phone\*\*:\s*([^\n]+)', section)
        phone = phone_match.group(1).strip() if phone_match else "N/A"
        
        # Extract known for
        known_for_match = re.search(r'\*\*Known For\*\*:\s*([^\n]+)', section)
        known_for = known_for_match.group(1).strip() if known_for_match else ""
        
        # Extract price
        price_match = re.search(r'\*\*Price\*\*:\s*([^\n]+)', section)
        price = price_match.group(1).strip() if price_match else "$$"
        
        # Build POI document
        poi = {
            "name": name,
            "slug": name.lower().replace(' ', '-').replace("'", ""),
            "category": self._infer_category(time_slot),
            "subcategories": self._infer_subcategories(time_slot, known_for),
            "location": {
                "type": "Point",
                "coordinates": [0, 0]  # Will geocode later
            },
            "address": {
                "street": address,
                "city": "New York",
                "state": "NY",
                "zip": "",
                "neighborhood": neighborhood,
                "borough": "Manhattan"
            },
            "contact": {
                "phone": phone if phone != "N/A" else "",
                "website": "",
                "reservations_url": ""
            },
            "hours": {
                "note": hours
            },
            "experience": {
                "price_range": price,
                "signature_dishes": [known_for] if known_for else [],
                "ambiance": []
            },
            "best_for": {
                "time_of_day": [time_slot.split('_')[0]],
                "occasions": self._infer_occasions(time_slot),
                "weather": ["any"],
                "group_size": [2, 4]
            },
            "prestige": {
                "score": 0  # Will calculate after enrichment
            },
            "sources": [
                {
                    "type": "perplexity_discovery",
                    "query": f"{time_slot} in {neighborhood}",
                    "citations": citations,
                    "retrieved_at": datetime.now().isoformat()
                }
            ],
            "created_at": datetime.now().isoformat(),
            "time_context": time_slot
        }
        
        return poi
    
    def _infer_category(self, time_slot: str) -> str:
        """Infer category from time slot"""
        if time_slot == "evening_prestige":
            return "fine-dining"
        elif time_slot == "evening_casual":
            return "bars-cocktails"
        else:
            return "casual-dining"
    
    def _infer_subcategories(self, time_slot: str, known_for: str) -> List[str]:
        """Infer subcategories from time slot and description"""
        subcats = []
        
        keywords_map = {
            "bagel": "bagels",
            "coffee": "coffee",
            "breakfast": "breakfast",
            "pizza": "pizza",
            "sandwich": "sandwich",
            "bar": "cocktails",
            "wine": "wine-bar",
            "michelin": "michelin"
        }
        
        for keyword, subcat in keywords_map.items():
            if keyword in known_for.lower():
                subcats.append(subcat)
        
        return subcats[:3]
    
    def _infer_occasions(self, time_slot: str) -> List[str]:
        """Infer occasions from time slot"""
        occasion_map = {
            "morning": ["breakfast", "business-breakfast"],
            "afternoon": ["lunch", "business-lunch", "quick-bite"],
            "evening_casual": ["after-work", "casual-drinks", "happy-hour"],
            "evening_prestige": ["date-night", "special-occasion", "business-dinner"]
        }
        return occasion_map.get(time_slot, ["casual-meal"])
    
    async def save_pois(self, pois: List[Dict], filename: str):
        """Save POIs to JSON file"""
        output_path = self.output_dir / filename
        
        with open(output_path, 'w') as f:
            json.dump(pois, f, indent=2)
        
        print(f"\n💾 Saved {len(pois)} POIs to {output_path}")


async def main():
    """Main production enrichment workflow"""
    
    print("="*70)
    print("Production POI Enrichment with Perplexity Sonar API")
    print("Budget: $25 (5,000 searches)")
    print("="*70)
    
    api_key = os.getenv("PERPLEXITY_API_KEY")
    
    if not api_key:
        print("❌ ERROR: PERPLEXITY_API_KEY environment variable required!")
        print("Get your API key from: https://www.perplexity.ai/settings/api")
        return
    
    enricher = ProductionPOIEnricher(api_key=api_key)
    
    all_pois = []
    
    # Phase 1: Discovery (1,000 searches budget)
    print("\n📍 Phase 1: POI Discovery")
    print("-"*70)
    
    for neighborhood_name, lat, lon in enricher.NEIGHBORHOODS:  # Cover all defined neighborhoods
        for time_slot in enricher.TIME_CATEGORIES.keys():
            pois = await enricher.discover_pois_by_context(
                neighborhood_name,
                lat,
                lon,
                time_slot
            )
            all_pois.extend(pois)
            
            # Small delay between requests
            await asyncio.sleep(1)
    
    # Save discovered POIs
    await enricher.save_pois(all_pois, "discovered_pois.json")
    
    # Summary
    print(f"\n{'='*70}")
    print("📊 Discovery Summary")
    print(f"{'='*70}")
    print(f"Total POIs discovered: {len(all_pois)}")
    print(f"API searches used: {enricher.search_count}/5,000")
    print(f"Budget used: ${enricher.search_count * 0.005:.2f}/$25.00")
    print(f"Remaining budget: {5000 - enricher.search_count} searches")
    print(f"{'='*70}")


if __name__ == "__main__":
    asyncio.run(main())
