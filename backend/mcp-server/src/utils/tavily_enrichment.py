"""
Tavily-powered Real-time POI Enrichment
For last-minute sanity checks during demos
"""

import os
from typing import Dict, Any, Optional
from datetime import datetime

try:
    from tavily import TavilyClient
except ImportError:
    import subprocess
    subprocess.run(["pip", "install", "tavily-python"], check=True)
    from tavily import TavilyClient


class TavilyEnricher:
    """Real-time POI enrichment using Tavily for trusted source validation"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY environment variable required")
        
        self.client = TavilyClient(api_key=self.api_key)
    
    async def enrich_poi(
        self,
        poi_name: str,
        poi_address: str,
        category: str = "restaurant"
    ) -> Dict[str, Any]:
        """
        Get real-time enrichment for a POI using Tavily
        
        KILLER FEATURE: Captures real-time updates that Google Maps/Yelp miss:
        - Holiday hours (Thanksgiving, Christmas, NYE)
        - Special menus and prix fixe offerings
        - Recent chef changes or restaurant news
        - Social media buzz and trending dishes
        - Temporary closures or renovations
        - Current reservation availability
        
        Args:
            poi_name: Name of the restaurant/bar
            poi_address: Street address for specificity
            category: Type of POI
        
        Returns:
            Dict with enrichment data from trusted sources
        """
        
        # Check if it's near a major holiday
        now = datetime.now()
        upcoming_holiday = self._get_upcoming_holiday(now)
        
        # Build targeted queries for different aspects
        queries = [
            # Real-time hours (especially for holidays!)
            f"{poi_name} {poi_address} NYC hours {upcoming_holiday} Thanksgiving Christmas New Years holiday special",
            
            # Special events and menus (the killer feature!)
            f"{poi_name} NYC {upcoming_holiday} menu special prix fixe tasting menu seasonal",
            
            # Recent news and changes
            f"{poi_name} NYC {now.year} news chef change menu update reopening renovation",
            
            # Social media buzz (what's trending RIGHT NOW)
            f"{poi_name} NYC Instagram latest posts trending dishes must try {now.strftime('%B %Y')}",
            
            # Current availability
            f"{poi_name} NYC reservations OpenTable Resy availability {upcoming_holiday}",
            
            # Awards and recognition (recent)
            f"{poi_name} NYC Michelin {now.year} awards James Beard New York Times review latest"
        ]
        
        enrichment_data = {
            "poi_name": poi_name,
            "enriched_at": datetime.now().isoformat(),
            "source": "tavily_realtime",
            "holiday_hours": "",  # NEW: Critical for Thanksgiving demo!
            "special_events": "",  # NEW: Prix fixe menus, etc.
            "recent_news": "",  # NEW: Chef changes, reopenings
            "social_buzz": "",  # What people are posting NOW
            "current_availability": "",  # Booking status
            "latest_recognition": "",  # Recent awards
            "citations": []
        }
        
        # Run searches with trusted domain filtering
        trusted_domains = [
            "guide.michelin.com",
            "ny.eater.com",
            "timeout.com",
            "nytimes.com",
            "theinfatuation.com",
            "opentable.com",
            "resy.com",
            "instagram.com",  # For social buzz
            "exploretock.com"  # Reservation system
        ]
        
        # Execute the Tavily searches!
        for idx, query in enumerate(queries):
            try:
                response = self.client.search(
                    query=query,
                    search_depth="advanced",
                    include_domains=trusted_domains,
                    include_answer=True,
                    max_results=3
                )
                
                # Extract answer
                answer = response.get("answer", "")
                if answer:
                    # Categorize based on query index
                    if idx == 0:  # Holiday hours
                        enrichment_data["holiday_hours"] = answer
                    elif idx == 1:  # Special events
                        enrichment_data["special_events"] = answer
                    elif idx == 2:  # Recent news
                        enrichment_data["recent_news"] = answer
                    elif idx == 3:  # Social buzz
                        enrichment_data["social_buzz"] = answer
                    elif idx == 4:  # Availability
                        enrichment_data["current_availability"] = answer
                    elif idx == 5:  # Recognition
                        enrichment_data["latest_recognition"] = answer
                
                # Collect citations
                for result in response.get("results", [])[:2]:
                    enrichment_data["citations"].append({
                        "url": result.get("url"),
                        "title": result.get("title"),
                        "source": result.get("url", "").split("/")[2] if result.get("url") else "unknown"
                    })
                
            except Exception as e:
                print(f"Warning: Enrichment query {idx} failed: {e}")
                continue
        
        return enrichment_data
    
    
    def _get_upcoming_holiday(self, date: datetime) -> str:
        """Get the next upcoming holiday for context-aware queries"""
        month, day = date.month, date.day
        
        # Thanksgiving (4th Thursday of November)
        if month == 11 and 20 <= day <= 28:
            return "Thanksgiving"
        # Christmas/New Year
        elif month == 12 or (month == 1 and day <= 2):
            return "Christmas New Years Eve"
        # Valentine's Day
        elif month == 2 and 1 <= day <= 14:
            return "Valentine's Day"
        # Mother's/Father's Day
        elif month == 5:
            return "Mother's Day"
        elif month == 6:
            return "Father's Day"
        else:
            return ""


# Convenience function for MCP tool integration
async def enrich_poi_live(
    poi_name: str,
    poi_address: str,
    category: str = "restaurant"
) -> str:
    """
    MCP tool wrapper for POI enrichment using Tavily
    Returns formatted text for display in chat
    """
    
    enricher = TavilyEnricher()
    
    try:
        enrichment = await enricher.enrich_poi(
            poi_name=poi_name,
            poi_address=poi_address,
            category=category
        )
        
        # Format for display
        response = f"📍 **{poi_name}** - Real-time Updates\n\n"
        
        if enrichment.get("latest_buzz") and enrichment["latest_buzz"].strip():
            response += f"🔥 **Latest Buzz:**\n{enrichment['latest_buzz'].strip()}\n\n"
        
        if enrichment.get("menu_highlights") and enrichment["menu_highlights"].strip():
            response += f"🍽️ **Menu Highlights:**\n{enrichment['menu_highlights'].strip()}\n\n"
        
        if enrichment.get("availability_context") and enrichment["availability_context"].strip():
            response += f"⏰ **Reservations & Hours:**\n{enrichment['availability_context'].strip()}\n\n"
        
        if enrichment.get("social_vibe") and enrichment["social_vibe"].strip():
            response += f"📱 **Social Media Vibe:**\n{enrichment['social_vibe'].strip()}\n\n"
        
        # Add citations
        citations = enrichment.get("citations", [])
        if citations:
            response += f"📚 **Verified Sources:**\n"
            seen_sources = set()
            for citation in citations:
                source = citation.get("source", "")
                if source and source not in seen_sources:
                    seen_sources.add(source)
                    response += f"  • {source}\n"
        
        response += f"\n_✅ Verified via Tavily • {enrichment['enriched_at']}_"
        
        return response
        
    except Exception as e:
        return f"❌ Failed to enrich {poi_name}: {str(e)}\n\nThis tool requires TAVILY_API_KEY to be set in your environment."


async def refresh_poi_data(poi: Dict[str, Any]) -> Dict[str, Any]:
    """
    Refresh specific POI fields using Tavily for latest web data
    
    Args:
        poi: POI document from MongoDB
        
    Returns:
        Dict with updated fields: contact, hours, social, enrichment_data
    """
    enricher = TavilyEnricher()
    
    poi_name = poi.get("name", "")
    address = poi.get("address", {})
    street = address.get("street", "")
    
    # Call the enhanced enrich_poi method for full Thanksgiving data!
    print(f"🔍 Calling enrich_poi for {poi_name}...")
    enrichment = await enricher.enrich_poi(
        poi_name=poi_name,
        poi_address=street,
        category=poi.get("category", "restaurant")
    )
    print(f"✅ Enrichment received: {enrichment is not None}")
    if enrichment:
        print(f"   Keys: {enrichment.keys()}")
    
    # Build targeted queries for refreshable data
    queries = {
        "contact": f"{poi_name} {street} NYC phone number website contact",
        "hours": f"{poi_name} {street} NYC hours of operation current schedule",
        "social": f"{poi_name} NYC Instagram Twitter Facebook social media handles"
    }
    
    updated_data = {
        "contact": {},
        "hours": {},
        "social": {},
        "enrichment_data": enrichment  # Include full enrichment!
    }
    print(f"📦 Updated data keys: {updated_data.keys()}")
    print(f"📦 Has enrichment_data: {updated_data.get('enrichment_data') is not None}")
    
    for field, query in queries.items():
        try:
            response = enricher.client.search(
                query=query,
                search_depth="advanced",
                include_answer=True,
                max_results=3
            )
            
            answer = response.get("answer", "")
            
            if field == "contact":
                # Extract contact info from answer
                # This is a simple implementation - you could make it more sophisticated
                updated_data["contact"] = {
                    "phone": poi.get("contact", {}).get("phone"),  # Keep existing if not found
                    "website": poi.get("contact", {}).get("website"),
                    "info": answer  # Store the answer for reference
                }
                
            elif field == "hours":
                # Store hours info
                updated_data["hours"] = {
                    "summary": answer,
                    "last_updated": datetime.now().isoformat()
                }
                
            elif field == "social":
                # Extract social media handles from answer
                updated_data["social"] = {
                    "info": answer,
                    "last_updated": datetime.now().isoformat()
                }
                
        except Exception as e:
            print(f"Warning: Failed to refresh {field} for {poi_name}: {e}")
            continue
    
    return updated_data
