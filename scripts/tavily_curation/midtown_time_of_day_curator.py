"""
Midtown Manhattan (1633 Broadway) Time-of-Day POI Curator
Enhanced Tavily curation with time-based contextualization

Demo scenario: Show different recommendations for:
- Morning: Best bagels
- Afternoon: Best pizza
- Evening: Happy hour vs Michelin dinner
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict

try:
    from tavily import TavilyClient
except ImportError:
    print("Installing tavily-python...")
    os.system("pip install tavily-python")
    from tavily import TavilyClient


class MidtownTimeOfDayCurator:
    """Curate POIs around 1633 Broadway with time-of-day context"""
    
    # 1633 Broadway coordinates (Times Square area)
    CENTER_LAT = 40.7614
    CENTER_LON = -73.9826
    
    def __init__(self, api_key: str, output_dir: str = "data/raw"):
        self.client = TavilyClient(api_key=api_key)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Time-of-day query templates
        self.queries_by_time = {
            "morning": {
                "time_range": "breakfast, 7am-11am",
                "queries": [
                    "best bagels near Times Square Manhattan 1633 Broadway",
                    "best breakfast spots Midtown West NYC",
                    "best coffee bakery near Times Square",
                    "essential NYC bagel shops Midtown Manhattan"
                ],
                "category": "casual-dining",
                "subcategories": ["breakfast", "bakery", "cafe"],
                "expected_count": 10
            },
            "afternoon": {
                "time_range": "lunch, 11am-3pm",
                "queries": [
                    "best pizza near Times Square Manhattan 1633 Broadway",
                    "famous NYC pizza slices Midtown",
                    "best lunch spots near Times Square quick",
                    "casual lunch restaurants Broadway Midtown"
                ],
                "category": "casual-dining",
                "subcategories": ["pizza", "sandwich", "quick-bite"],
                "expected_count": 15
            },
            "evening_casual": {
                "time_range": "happy hour, 5pm-7pm",
                "queries": [
                    "best happy hour near Times Square Manhattan 1633 Broadway",
                    "after-work bars Midtown West NYC",
                    "cocktail bars near Times Square specials",
                    "wine bars Midtown Manhattan"
                ],
                "category": "bars-cocktails",
                "subcategories": ["happy-hour", "cocktails", "wine-bar"],
                "expected_count": 12
            },
            "evening_prestige": {
                "time_range": "dinner, 6pm-10pm",
                "queries": [
                    "Michelin star restaurants near Times Square Manhattan",
                    "fine dining Midtown West NYC Broadway",
                    "best upscale restaurants near 1633 Broadway",
                    "special occasion dining Midtown Manhattan"
                ],
                "category": "fine-dining",
                "subcategories": ["michelin", "fine-dining", "upscale"],
                "expected_count": 8
            }
        }
    
    async def curate_by_time_of_day(self, time_slot: str) -> List[Dict]:
        """Curate POIs for a specific time of day"""
        
        if time_slot not in self.queries_by_time:
            raise ValueError(f"Unknown time slot: {time_slot}")
        
        config = self.queries_by_time[time_slot]
        
        print(f"\n{'='*60}")
        print(f"🕐 Curating for: {time_slot.upper()}")
        print(f"⏰ Time range: {config['time_range']}")
        print(f"📍 Location: 1633 Broadway, Midtown Manhattan")
        print(f"🎯 Target: {config['expected_count']} POIs")
        print(f"{'='*60}\n")
        
        all_candidates = []
        
        for query in config['queries']:
            print(f"🔍 Query: {query}")
            
            try:
                # Use different search depths based on category
                search_depth = "advanced" if config['category'] == "fine-dining" else "basic"
                
                response = self.client.search(
                    query=query,
                    search_depth=search_depth,
                    topic="general",
                    include_domains=[
                        "guide.michelin.com",
                        "ny.eater.com",
                        "timeout.com",
                        "theinfatuation.com",
                        "nytimes.com",
                        "yelp.com",
                        "foursquare.com",
                        "googleusercontent.com"  # Google Maps data
                    ],
                    include_answer=True,
                    include_raw_content=True,
                    max_results=10
                )
                
                # Extract POI candidates
                candidates = self._extract_pois_from_response(
                    response,
                    config['category'],
                    config['subcategories'],
                    time_slot
                )
                
                all_candidates.extend(candidates)
                print(f"  ✓ Found {len(candidates)} candidates\n")
                
                # Rate limiting
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"  ✗ Error: {e}\n")
                continue
        
        # Deduplicate and enrich
        unique_candidates = self._deduplicate_by_name(all_candidates)
        print(f"\n📊 Total unique candidates: {len(unique_candidates)}")
        
        return unique_candidates[:config['expected_count']]
    
    def _extract_pois_from_response(
        self,
        response: Dict,
        category: str,
        subcategories: List[str],
        time_slot: str
    ) -> List[Dict]:
        """Extract POI data from Tavily response with time context"""
        
        candidates = []
        
        # Parse results
        for result in response.get("results", []):
            content = result.get("content", "")
            title = result.get("title", "")
            url = result.get("url", "")
            
            # Extract venue names (simple regex for MVP)
            import re
            # Look for capitalized multi-word names
            pattern = r'\b([A-Z][a-zA-Z\'\&\-]+(?:\s+[A-Z\'\&][a-zA-Z\'\&\-]+)+)\b'
            matches = re.findall(pattern, f"{title} {content}")
            
            for venue_name in set(matches[:3]):  # Top 3 per result
                # Skip generic terms
                skip_terms = {
                    "Times Square", "New York", "Manhattan", "Midtown",
                    "The Best", "Top Ten", "Broadway"
                }
                if venue_name in skip_terms:
                    continue
                
                candidate = {
                    "name": venue_name,
                    "category": category,
                    "subcategories": subcategories,
                    "time_of_day": time_slot,
                    "source_url": url,
                    "mention_context": content[:300],
                    "extracted_at": datetime.now().isoformat(),
                    "location": {
                        "type": "Point",
                        "coordinates": [self.CENTER_LON, self.CENTER_LAT]  # Placeholder
                    },
                    "address": {
                        "city": "New York",
                        "state": "NY",
                        "borough": "Manhattan",
                        "neighborhood": "Midtown West"
                    },
                    "best_for": {
                        "time_of_day": [time_slot.split('_')[0]],  # "evening_casual" -> "evening"
                        "occasions": self._infer_occasions(category, time_slot),
                        "weather": ["any"],
                        "group_size": [2, 4]
                    }
                }
                
                candidates.append(candidate)
        
        # Also parse answer field
        if response.get("answer"):
            # Extract structured data from Tavily's answer
            answer_candidates = self._parse_answer_for_venues(
                response["answer"],
                category,
                subcategories,
                time_slot
            )
            candidates.extend(answer_candidates)
        
        return candidates
    
    def _parse_answer_for_venues(
        self,
        answer: str,
        category: str,
        subcategories: List[str],
        time_slot: str
    ) -> List[Dict]:
        """Parse Tavily answer for venue names"""
        import re
        
        candidates = []
        
        # Pattern for venue names
        pattern = r'\b([A-Z][a-zA-Z\'\&\-]+(?:\s+[A-Z\'\&][a-zA-Z\'\&\-]+)+)\b'
        matches = re.findall(pattern, answer)
        
        for venue_name in set(matches[:5]):  # Top 5 from answer
            candidate = {
                "name": venue_name,
                "category": category,
                "subcategories": subcategories,
                "time_of_day": time_slot,
                "source_url": "tavily_answer",
                "mention_context": answer[:200],
                "extracted_at": datetime.now().isoformat(),
                "location": {
                    "type": "Point",
                    "coordinates": [self.CENTER_LON, self.CENTER_LAT]
                },
                "address": {
                    "city": "New York",
                    "state": "NY",
                    "borough": "Manhattan",
                    "neighborhood": "Midtown West"
                },
                "best_for": {
                    "time_of_day": [time_slot.split('_')[0]],
                    "occasions": self._infer_occasions(category, time_slot),
                    "weather": ["any"],
                    "group_size": [2, 4]
                }
            }
            candidates.append(candidate)
        
        return candidates
    
    def _infer_occasions(self, category: str, time_slot: str) -> List[str]:
        """Infer suitable occasions based on category and time"""
        occasion_map = {
            ("casual-dining", "morning"): ["breakfast", "business-breakfast", "quick-bite"],
            ("casual-dining", "afternoon"): ["lunch", "business-lunch", "quick-bite"],
            ("bars-cocktails", "evening_casual"): ["after-work", "casual-drinks", "happy-hour"],
            ("fine-dining", "evening_prestige"): ["date-night", "special-occasion", "business-dinner"]
        }
        return occasion_map.get((category, time_slot), ["casual-meal"])
    
    def _deduplicate_by_name(self, candidates: List[Dict]) -> List[Dict]:
        """Remove duplicates by normalized name"""
        seen = set()
        unique = []
        
        for candidate in candidates:
            normalized = candidate["name"].lower().strip()
            if normalized not in seen:
                seen.add(normalized)
                unique.append(candidate)
        
        return unique
    
    async def save_candidates(self, candidates: List[Dict], time_slot: str):
        """Save POI candidates to JSON"""
        filename = f"midtown_{time_slot}_pois.json"
        output_path = self.output_dir / filename
        
        with open(output_path, 'w') as f:
            json.dump(candidates, f, indent=2)
        
        print(f"\n💾 Saved {len(candidates)} candidates to {output_path}")


async def main():
    """Main curation workflow"""
    
    print("="*60)
    print("Midtown Manhattan Time-of-Day POI Curator")
    print("Location: 1633 Broadway (Times Square area)")
    print("="*60)
    
    api_key = os.getenv("TAVILY_API_KEY")
    
    if not api_key:
        print("❌ ERROR: TAVILY_API_KEY environment variable required!")
        return
    
    curator = MidtownTimeOfDayCurator(api_key=api_key)
    
    # Curate for all time slots
    all_results = {}
    
    for time_slot in ["morning", "afternoon", "evening_casual", "evening_prestige"]:
        candidates = await curator.curate_by_time_of_day(time_slot)
        all_results[time_slot] = candidates
        await curator.save_candidates(candidates, time_slot)
        
        # Brief pause between time slots
        await asyncio.sleep(2)
    
    # Save consolidated dataset
    consolidated_path = curator.output_dir / "midtown_all_times.json"
    with open(consolidated_path, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n{'='*60}")
    print("📊 Curation Summary")
    print(f"{'='*60}")
    for time_slot, candidates in all_results.items():
        print(f"{time_slot.upper()}: {len(candidates)} POIs")
    print(f"\n💾 Consolidated file: {consolidated_path}")
    print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(main())
