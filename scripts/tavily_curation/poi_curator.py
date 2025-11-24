"""
NYC POI Curator - Tavily-Powered Restaurant Discovery
Phase 1: Curate 100 Manhattan restaurants with prestige markers

This script uses Tavily's AI-powered search to:
1. Discover high-quality restaurants from trusted sources
2. Extract prestige markers (Michelin stars, awards, accolades)
3. Validate data quality across multiple sources
4. Enrich POI metadata (location, hours, contact info)
"""

import asyncio
import json
import os
import re
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path

try:
    from tavily import TavilyClient
except ImportError:
    print("Installing tavily-python...")
    os.system("pip install tavily-python")
    from tavily import TavilyClient


@dataclass
class POICandidate:
    """Represents a discovered POI before full enrichment"""
    name: str
    category: str
    source_url: str
    mention_context: str
    extracted_at: str
    confidence_score: float = 0.0
    

@dataclass
class PrestigeMarkers:
    """Quality signals for a restaurant"""
    score: float = 0.0
    michelin_stars: Optional[int] = None
    michelin_since: Optional[int] = None
    michelin_bib_gourmand: bool = False
    james_beard_awards: List[str] = None
    nyt_stars: Optional[int] = None
    best_of_lists: List[Dict] = None
    celebrity_endorsements: List[str] = None
    
    def __post_init__(self):
        if self.james_beard_awards is None:
            self.james_beard_awards = []
        if self.best_of_lists is None:
            self.best_of_lists = []
        if self.celebrity_endorsements is None:
            self.celebrity_endorsements = []


class TavilyPOICurator:
    """Main curator class for discovering and validating POIs"""
    
    def __init__(self, api_key: str, output_dir: str = "data/raw"):
        self.client = TavilyClient(api_key=api_key)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Search configuration
        self.trusted_domains = [
            "guide.michelin.com",
            "ny.eater.com",
            "timeout.com",
            "nytimes.com",
            "theinfatuation.com",
            "zagat.com",
            "jamesbeard.org"
        ]
        
    async def discover_michelin_restaurants(self, target_count: int = 30) -> List[POICandidate]:
        """
        Priority 1: Discover Michelin-starred restaurants in Manhattan
        These are the highest prestige POIs
        """
        print(f"\n🌟 Phase 1a: Discovering Michelin-starred restaurants (target: {target_count})")
        
        queries = [
            "Michelin star restaurants Manhattan NYC 2025",
            "Michelin three star restaurants New York City",
            "Michelin two star restaurants Manhattan",
            "Michelin one star restaurants NYC",
            "Michelin Bib Gourmand restaurants Manhattan 2025"
        ]
        
        candidates = []
        
        for query in queries:
            print(f"  🔍 Searching: {query}")
            
            try:
                response = self.client.search(
                    query=query,
                    search_depth="advanced",
                    topic="general",
                    days=90,
                    include_domains=self.trusted_domains,
                    include_answer=True,
                    include_raw_content=True,
                    max_results=10
                )
                
                # Extract POI candidates from results
                extracted = self._extract_pois_from_response(response, "fine-dining")
                candidates.extend(extracted)
                
                print(f"    ✓ Found {len(extracted)} candidates")
                
                # Respect rate limits
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"    ✗ Error: {e}")
                continue
        
        # Deduplicate candidates
        unique_candidates = self._deduplicate_candidates(candidates)
        print(f"\n  📊 Total unique Michelin candidates: {len(unique_candidates)}")
        
        return unique_candidates[:target_count]
    
    async def discover_casual_dining(self, target_count: int = 50) -> List[POICandidate]:
        """
        Priority 2: Discover quality casual dining restaurants
        Focus on neighborhood gems and essential NYC spots
        """
        print(f"\n🍽️  Phase 1b: Discovering casual dining restaurants (target: {target_count})")
        
        queries = [
            "best restaurants Manhattan neighborhoods 2025 Eater essential",
            "best Italian restaurants Manhattan NYC",
            "best Asian restaurants Manhattan NYC 2025",
            "best Mexican restaurants Manhattan NYC",
            "essential NYC neighborhood restaurants Eater",
            "best new restaurants Manhattan 2025"
        ]
        
        candidates = []
        
        for query in queries:
            print(f"  🔍 Searching: {query}")
            
            try:
                response = self.client.search(
                    query=query,
                    search_depth="basic",  # Speed over depth for casual dining
                    include_domains=["ny.eater.com", "timeout.com", "theinfatuation.com"],
                    include_answer=True,
                    max_results=15
                )
                
                extracted = self._extract_pois_from_response(response, "casual-dining")
                candidates.extend(extracted)
                
                print(f"    ✓ Found {len(extracted)} candidates")
                
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"    ✗ Error: {e}")
                continue
        
        unique_candidates = self._deduplicate_candidates(candidates)
        print(f"\n  📊 Total unique casual dining candidates: {len(unique_candidates)}")
        
        return unique_candidates[:target_count]
    
    async def discover_bars_cocktails(self, target_count: int = 20) -> List[POICandidate]:
        """
        Priority 3: Discover notable cocktail bars and wine bars
        """
        print(f"\n🍸 Phase 1c: Discovering bars & cocktails (target: {target_count})")
        
        queries = [
            "best cocktail bars Manhattan NYC 2025",
            "best wine bars Manhattan NYC",
            "best rooftop bars Manhattan NYC",
            "World's 50 Best Bars New York"
        ]
        
        candidates = []
        
        for query in queries:
            print(f"  🔍 Searching: {query}")
            
            try:
                response = self.client.search(
                    query=query,
                    search_depth="basic",
                    include_answer=True,
                    max_results=10
                )
                
                extracted = self._extract_pois_from_response(response, "bars-cocktails")
                candidates.extend(extracted)
                
                print(f"    ✓ Found {len(extracted)} candidates")
                
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"    ✗ Error: {e}")
                continue
        
        unique_candidates = self._deduplicate_candidates(candidates)
        print(f"\n  📊 Total unique bar candidates: {len(unique_candidates)}")
        
        return unique_candidates[:target_count]
    
    async def validate_and_enrich_poi(self, candidate: POICandidate) -> Optional[Dict]:
        """
        Deep validation and enrichment for a single POI
        Runs multiple targeted searches to extract detailed information
        """
        print(f"\n  🔬 Validating: {candidate.name}")
        
        venue_name = candidate.name
        
        # Validation searches
        validation_queries = [
            f"{venue_name} NYC Michelin stars rating reviews",
            f"{venue_name} NYC address phone hours location",
            f"{venue_name} NYC awards accolades best of lists"
        ]
        
        validation_results = []
        
        for query in validation_queries:
            try:
                response = self.client.search(
                    query=query,
                    search_depth="advanced",
                    include_raw_content=True,
                    max_results=5
                )
                validation_results.append(response)
                await asyncio.sleep(0.5)
            except Exception as e:
                print(f"    ⚠️  Validation query failed: {e}")
                continue
        
        # Extract enriched data
        enriched_poi = self._build_enriched_poi(candidate, validation_results)
        
        # Calculate prestige score
        prestige = self._calculate_prestige_score(enriched_poi)
        enriched_poi["prestige"] = asdict(prestige)
        
        # Only include POIs with minimum quality threshold
        if prestige.score < 20:  # Minimum threshold
            print(f"    ✗ Below quality threshold (score: {prestige.score})")
            return None
        
        print(f"    ✓ Validated (prestige score: {prestige.score})")
        return enriched_poi
    
    def _extract_pois_from_response(self, response: Dict, category: str) -> List[POICandidate]:
        """Extract POI candidates from Tavily search response"""
        candidates = []
        
        # Parse answer field for structured data
        if response.get("answer"):
            answer_pois = self._parse_answer_for_venues(response["answer"], category)
            candidates.extend(answer_pois)
        
        # Parse individual results
        for result in response.get("results", []):
            content = result.get("content", "")
            title = result.get("title", "")
            url = result.get("url", "")
            
            # Extract restaurant names from content
            venue_mentions = self._extract_venue_mentions(content, title)
            
            for venue_name in venue_mentions:
                candidate = POICandidate(
                    name=venue_name,
                    category=category,
                    source_url=url,
                    mention_context=content[:200],
                    extracted_at=datetime.now().isoformat(),
                    confidence_score=result.get("score", 0.5)
                )
                candidates.append(candidate)
        
        return candidates
    
    def _parse_answer_for_venues(self, answer: str, category: str) -> List[POICandidate]:
        """Parse Tavily's answer field for restaurant names"""
        candidates = []
        
        # Pattern: Look for restaurant names (typically capitalized words/phrases)
        # Common patterns: "Le Bernardin", "Gramercy Tavern", "Death & Co"
        pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z&][a-z]+)*)\b'
        matches = re.findall(pattern, answer)
        
        # Filter for likely restaurant names (2+ words or special chars)
        for match in matches:
            if len(match.split()) >= 2 or '&' in match or "'" in match:
                candidate = POICandidate(
                    name=match,
                    category=category,
                    source_url="tavily_answer",
                    mention_context=answer[:200],
                    extracted_at=datetime.now().isoformat(),
                    confidence_score=0.8
                )
                candidates.append(candidate)
        
        return candidates
    
    def _extract_venue_mentions(self, content: str, title: str) -> List[str]:
        """Extract restaurant names from content text"""
        venues = []
        
        # Combine title and content
        text = f"{title} {content}"
        
        # Pattern for restaurant names
        pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z&\'][a-z]+)*)\b'
        matches = re.findall(pattern, text)
        
        # Filter for likely names
        for match in matches:
            # Skip common words
            skip_words = {"The", "Manhattan", "York", "City", "New", "Best", "Top"}
            if match in skip_words:
                continue
            
            # Include multi-word names or names with special chars
            if len(match.split()) >= 2 or any(char in match for char in ['&', "'"]):
                venues.append(match)
        
        return list(set(venues))[:5]  # Limit to top 5 per source
    
    def _deduplicate_candidates(self, candidates: List[POICandidate]) -> List[POICandidate]:
        """Remove duplicate POI candidates by name"""
        seen_names = set()
        unique = []
        
        for candidate in candidates:
            normalized_name = candidate.name.lower().strip()
            if normalized_name not in seen_names:
                seen_names.add(normalized_name)
                unique.append(candidate)
        
        return unique
    
    def _build_enriched_poi(self, candidate: POICandidate, validation_results: List[Dict]) -> Dict:
        """Build enriched POI document from candidate and validation data"""
        
        # Combine all content for extraction
        all_content = ""
        sources = []
        
        for result in validation_results:
            for item in result.get("results", []):
                all_content += f"\n{item.get('content', '')}"
                sources.append({
                    "type": "tavily_enrichment",
                    "url": item.get("url"),
                    "retrieved_at": datetime.now().isoformat()
                })
        
        # Extract structured data
        poi = {
            "name": candidate.name,
            "slug": self._slugify(candidate.name),
            "category": candidate.category,
            "subcategories": self._infer_subcategories(all_content, candidate.category),
            
            # Location data (to be geocoded later)
            "location": {
                "type": "Point",
                "coordinates": [0, 0]  # Placeholder
            },
            "address": self._extract_address(all_content),
            
            # Contact info
            "contact": self._extract_contact(all_content, candidate.name),
            
            # Hours (simplified for MVP)
            "hours": {},
            
            # Experience details
            "experience": {
                "price_range": self._extract_price_range(all_content),
                "signature_dishes": self._extract_signature_dishes(all_content),
                "ambiance": self._extract_ambiance(all_content),
                "dietary_accommodations": []
            },
            
            # Context
            "best_for": {
                "occasions": self._infer_occasions(candidate.category),
                "time_of_day": self._infer_time_of_day(candidate.category),
                "weather": ["any"],
                "group_size": [2, 4],
                "seasons": ["any"]
            },
            
            # Sources
            "sources": sources,
            
            # Metadata
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "validation_status": "pending",
            "data_quality_score": 0.0
        }
        
        return poi
    
    def _calculate_prestige_score(self, poi: Dict) -> PrestigeMarkers:
        """Calculate prestige score based on quality markers"""
        prestige = PrestigeMarkers()
        
        # Extract markers from content
        all_text = json.dumps(poi).lower()
        
        # Michelin stars (highest weight)
        if "three michelin star" in all_text or "3 michelin star" in all_text:
            prestige.michelin_stars = 3
            prestige.score += 100
        elif "two michelin star" in all_text or "2 michelin star" in all_text:
            prestige.michelin_stars = 2
            prestige.score += 75
        elif "one michelin star" in all_text or "1 michelin star" in all_text or "michelin starred" in all_text:
            prestige.michelin_stars = 1
            prestige.score += 50
        elif "bib gourmand" in all_text:
            prestige.michelin_bib_gourmand = True
            prestige.score += 30
        
        # James Beard
        if "james beard" in all_text:
            prestige.james_beard_awards.append("James Beard Recognition")
            prestige.score += 40
        
        # NYT stars
        if "four star" in all_text or "4 star" in all_text:
            prestige.nyt_stars = 4
            prestige.score += 40
        elif "three star" in all_text or "3 star" in all_text:
            prestige.nyt_stars = 3
            prestige.score += 30
        
        # Best of lists
        for source in ["eater", "timeout", "infatuation", "zagat"]:
            if source in all_text:
                prestige.best_of_lists.append({
                    "source": source.title(),
                    "retrieved_at": datetime.now().isoformat()
                })
                prestige.score += 5
        
        return prestige
    
    # Helper extraction methods
    def _slugify(self, name: str) -> str:
        """Convert name to URL-friendly slug"""
        return re.sub(r'[^\w\s-]', '', name.lower()).replace(' ', '-')
    
    def _infer_subcategories(self, content: str, category: str) -> List[str]:
        """Infer subcategories from content"""
        subcats = []
        content_lower = content.lower()
        
        cuisine_keywords = {
            "french": "french",
            "italian": "italian",
            "japanese": "japanese",
            "chinese": "chinese",
            "mexican": "mexican",
            "american": "american",
            "seafood": "seafood",
            "steakhouse": "steakhouse",
            "vegetarian": "vegetarian"
        }
        
        for keyword, subcat in cuisine_keywords.items():
            if keyword in content_lower:
                subcats.append(subcat)
        
        return subcats[:3]  # Limit to 3
    
    def _extract_address(self, content: str) -> Dict:
        """Extract address from content"""
        # Simple pattern for NYC addresses
        pattern = r'(\d+\s+[NESW]\.?\s+\d+(?:st|nd|rd|th)?\s+St(?:reet)?)'
        match = re.search(pattern, content, re.IGNORECASE)
        
        return {
            "street": match.group(1) if match else "",
            "city": "New York",
            "state": "NY",
            "zip": "",
            "neighborhood": "",
            "borough": "Manhattan"
        }
    
    def _extract_contact(self, content: str, name: str) -> Dict:
        """Extract contact information"""
        # Phone pattern
        phone_pattern = r'(\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})'
        phone_match = re.search(phone_pattern, content)
        
        # Website (simplified)
        website_pattern = r'https?://[^\s]+'
        website_match = re.search(website_pattern, content)
        
        return {
            "phone": phone_match.group(1) if phone_match else "",
            "website": website_match.group(0) if website_match else "",
            "reservations_url": "",
            "social": {}
        }
    
    def _extract_price_range(self, content: str) -> str:
        """Extract price range"""
        if "$$$$" in content or "expensive" in content.lower():
            return "$$$$"
        elif "$$$" in content:
            return "$$$"
        elif "$$" in content or "moderate" in content.lower():
            return "$$"
        else:
            return "$$"
    
    def _extract_signature_dishes(self, content: str) -> List[str]:
        """Extract signature dishes"""
        dishes = []
        # This is simplified - in production, use NER or GPT
        return dishes
    
    def _extract_ambiance(self, content: str) -> List[str]:
        """Extract ambiance descriptors"""
        ambiance_keywords = {
            "romantic", "elegant", "casual", "intimate", "lively",
            "modern", "cozy", "sophisticated", "rustic"
        }
        
        found = []
        content_lower = content.lower()
        
        for keyword in ambiance_keywords:
            if keyword in content_lower:
                found.append(keyword)
        
        return found[:3]
    
    def _infer_occasions(self, category: str) -> List[str]:
        """Infer suitable occasions based on category"""
        if category == "fine-dining":
            return ["date-night", "special-occasion", "business-dinner"]
        elif category == "casual-dining":
            return ["casual-meal", "family-dinner", "lunch"]
        elif category == "bars-cocktails":
            return ["date-night", "after-work", "celebration"]
        return ["casual-meal"]
    
    def _infer_time_of_day(self, category: str) -> List[str]:
        """Infer suitable times based on category"""
        if category == "bars-cocktails":
            return ["evening", "late-night"]
        else:
            return ["lunch", "dinner"]
    
    async def save_candidates(self, candidates: List[POICandidate], filename: str):
        """Save POI candidates to JSON file"""
        output_path = self.output_dir / filename
        
        data = [asdict(c) for c in candidates]
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"\n💾 Saved {len(candidates)} candidates to {output_path}")
    
    async def save_enriched_pois(self, pois: List[Dict], filename: str):
        """Save enriched POIs to JSON file"""
        output_path = self.output_dir / filename
        
        with open(output_path, 'w') as f:
            json.dump(pois, f, indent=2)
        
        print(f"\n💾 Saved {len(pois)} enriched POIs to {output_path}")


async def main():
    """Main curation workflow"""
    
    print("=" * 60)
    print("NYC POI Curator - Tavily-Powered Restaurant Discovery")
    print("MongoDB x Tavily x LastMile AI Hackathon")
    print("=" * 60)
    
    # Initialize curator
    api_key = os.getenv("TAVILY_API_KEY")
    
    if not api_key:
        print("❌ ERROR: TAVILY_API_KEY environment variable is required!")
        print("Set it with: export TAVILY_API_KEY='your_api_key_here'")
        return
    
    curator = TavilyPOICurator(api_key=api_key)
    
    # Phase 1: Discovery
    print("\n📍 Phase 1: POI Discovery")
    print("-" * 60)
    
    michelin_candidates = await curator.discover_michelin_restaurants(target_count=30)
    casual_candidates = await curator.discover_casual_dining(target_count=50)
    bar_candidates = await curator.discover_bars_cocktails(target_count=20)
    
    all_candidates = michelin_candidates + casual_candidates + bar_candidates
    
    # Save candidates
    await curator.save_candidates(all_candidates, "poi_candidates.json")
    
    # Phase 2: Validation & Enrichment
    print("\n\n🔬 Phase 2: Validation & Enrichment")
    print("-" * 60)
    print(f"Processing {len(all_candidates)} candidates...\n")
    
    enriched_pois = []
    
    for i, candidate in enumerate(all_candidates[:10], 1):  # Start with first 10 for testing
        print(f"[{i}/{min(10, len(all_candidates))}]", end="")
        
        enriched = await curator.validate_and_enrich_poi(candidate)
        
        if enriched:
            enriched_pois.append(enriched)
        
        # Rate limiting
        await asyncio.sleep(2)
    
    # Save enriched POIs
    await curator.save_enriched_pois(enriched_pois, "enriched_pois.json")
    
    # Summary
    print("\n\n" + "=" * 60)
    print("📊 Curation Summary")
    print("=" * 60)
    print(f"Total candidates discovered: {len(all_candidates)}")
    print(f"  - Michelin restaurants: {len(michelin_candidates)}")
    print(f"  - Casual dining: {len(casual_candidates)}")
    print(f"  - Bars & cocktails: {len(bar_candidates)}")
    print(f"\nEnriched POIs: {len(enriched_pois)}")
    print(f"Next step: Review data/raw/enriched_pois.json")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
