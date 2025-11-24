"""
NYC POI Concierge MCP Server
Model Context Protocol server with restaurant recommendation tools
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp import types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server

# Import our utilities
import sys

sys.path.append(str(Path(__file__).parent))

from config import config
from resources import RESOURCE_MAP
from utils.mongodb import MongoDBClient
from utils.scoring import (
    combine_score_components,
    contextual_boost_expression,
    hybrid_score_expression,
)
from utils.tavily_enrichment import enrich_poi_live


# Initialize server
server = Server("nyc-poi-concierge")

# Global MongoDB client
mongo_client: Optional[MongoDBClient] = None


@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """Expose static neighborhood guides and taxonomy resources."""
    resources = []
    for uri, payload in RESOURCE_MAP.items():
        resources.append(
            types.Resource(
                uri=uri,
                name=payload["name"],
                description=payload["description"],
                mimeType=payload["mime_type"],
            )
        )
    return resources


@server.read_resource()
async def handle_read_resource(uri: str) -> list[types.TextContent]:
    payload = RESOURCE_MAP.get(uri)
    if not payload:
        raise ValueError(f"Unknown resource URI: {uri}")
    body = json.dumps(payload["data"], indent=2)
    return [types.TextContent(type="text", text=body)]


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available MCP tools"""
    return [
        types.Tool(
            name="query_pois",
            description="""Search for NYC points of interest (restaurants, bars) with advanced filtering.
            
            Supports:
            - Geospatial search (find POIs near a location within a radius)
            - Category filtering (fine-dining, casual-dining, bars-cocktails)
            - Prestige filtering (minimum prestige score, Michelin stars)
            - Hybrid scoring that mixes prestige, proximity, and contextual hints
            
            Perfect for: "Find Michelin-starred restaurants near me" or "Show me cocktail bars in Manhattan"
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "latitude": {
                        "type": "number",
                        "description": "User's latitude (-90 to 90)",
                    },
                    "longitude": {
                        "type": "number",
                        "description": "User's longitude (-180 to 180)",
                    },
                    "radius_meters": {
                        "type": "number",
                        "description": "Search radius in meters (default: 2000)",
                        "default": 2000,
                    },
                    "categories": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by categories: fine-dining, casual-dining, bars-cocktails",
                    },
                    "min_prestige_score": {
                        "type": "number",
                        "description": "Minimum prestige score (0-150, default: 0)",
                        "default": 0,
                    },
                    "michelin_stars": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "Filter by Michelin stars: [1], [2], [3], or [1,2,3]",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results (default: 10)",
                        "default": 10,
                    },
                    "occasion": {
                        "type": "string",
                        "description": "Optional occasion to boost matches (e.g., date-night, celebration)",
                    },
                    "time_of_day": {
                        "type": "string",
                        "description": "Explicit time of day to prioritize (lunch, dinner, late-night)",
                    },
                    "weather_condition": {
                        "type": "string",
                        "description": "Weather context for patio-friendly vs cozy rooms",
                    },
                },
                "required": ["latitude", "longitude"],
            },
        ),
        types.Tool(
            name="get_contextual_recommendations",
            description="""Get personalized POI recommendations based on comprehensive context.
            
            Analyzes:
            - Current location and nearby options
            - Time of day and day of week (for hours matching)
            - Weather conditions (indoor/outdoor suitability)
            - Occasion type (date-night, business-dinner, casual, celebration)
            - Group size and party preferences
            - Budget constraints
            
            Returns ranked recommendations with relevance explanations tailored to the user's specific situation.
            
            Perfect for: "Where should I go for a date night tonight?" or "Best place for business lunch near my office"
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "latitude": {
                        "type": "number",
                        "description": "User's latitude",
                    },
                    "longitude": {
                        "type": "number",
                        "description": "User's longitude",
                    },
                    "radius_meters": {
                        "type": "number",
                        "description": "Search radius in meters (default: 3000)",
                        "default": 3000,
                    },
                    "datetime": {
                        "type": "string",
                        "description": "ISO 8601 datetime (e.g., '2025-11-22T19:00:00'). Defaults to now.",
                    },
                    "weather": {
                        "type": "string",
                        "description": "Current weather: sunny, rain, cold, snow, any",
                        "enum": ["sunny", "rain", "cold", "snow", "any"],
                    },
                    "occasion": {
                        "type": "string",
                        "description": "Type of occasion",
                        "enum": ["date-night", "business-dinner", "business-lunch", "casual-meal", 
                                "celebration", "family-dinner", "quick-bite", "after-work"],
                    },
                    "group_size": {
                        "type": "integer",
                        "description": "Number of people (default: 2)",
                        "default": 2,
                    },
                    "budget": {
                        "type": "string",
                        "description": "Budget level",
                        "enum": ["$", "$$", "$$$", "$$$$", "any"],
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of recommendations (default: 5)",
                        "default": 5,
                    },
                },
                "required": ["latitude", "longitude"],
            },
        ),
        types.Tool(
            name="enrich_poi_live",
            description="""Get real-time enrichment for a specific POI using Tavily trusted source validation.
            
            Provides:
            - Latest reviews and buzz from trusted sources (Michelin, Eater, NYT, Timeout)
            - Current menu highlights and signature dishes
            - Availability context (hours, reservations, wait times)
            - Verified information with source citations
            
            USE THIS AFTER providing initial recommendations for last-minute sanity checks.
            Perfect for: "Tell me more about [restaurant name]" or "What's the latest on [bar name]?"
            
            Note: Uses Tavily's trusted domain filtering for reliable, verified information.
            
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "poi_name": {
                        "type": "string",
                        "description": "Name of the POI to enrich (e.g., 'Le Bernardin')",
                    },
                    "poi_address": {
                        "type": "string",
                        "description": "Street address for specificity (e.g., '155 W 51st St')",
                    },
                    "category": {
                        "type": "string",
                        "description": "Type of POI: restaurant, bar, cafe, etc.",
                        "default": "restaurant",
                    },
                },
                "required": ["poi_name", "poi_address"],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool execution"""
    
    if not mongo_client:
        raise RuntimeError("MongoDB client not initialized")
    
    if name == "query_pois":
        return await query_pois_tool(arguments or {})
    elif name == "get_contextual_recommendations":
        return await contextual_recommendations_tool(arguments or {})
    elif name == "enrich_poi_live":
        return await enrich_poi_live_tool(arguments or {})
    else:
        raise ValueError(f"Unknown tool: {name}")


async def query_pois_tool(args: Dict[str, Any]) -> list[types.TextContent]:
    """Execute POI query with filters"""
    
    lat = args["latitude"]
    lon = args["longitude"]
    radius = args.get("radius_meters", 2000)
    categories = args.get("categories")
    min_prestige = args.get("min_prestige_score", 0)
    michelin_stars = args.get("michelin_stars")
    limit = args.get("limit", 10)
    occasion = args.get("occasion")
    time_of_day = args.get("time_of_day")
    weather_condition = args.get("weather_condition")
    
    # Build MongoDB aggregation pipeline
    pipeline = [
        {
            "$geoNear": {
                "near": {
                    "type": "Point",
                    "coordinates": [lon, lat]
                },
                "distanceField": "distance",
                "maxDistance": radius,
                "spherical": True
            }
        }
    ]
    
    # Add filters
    match_conditions = {"prestige.score": {"$gte": min_prestige}}
    
    if categories:
        match_conditions["category"] = {"$in": categories}
    
    if michelin_stars:
        match_conditions["prestige.michelin_stars"] = {"$in": michelin_stars}
    
    if match_conditions:
        pipeline.append({"$match": match_conditions})
    
    hybrid_expr = hybrid_score_expression(
        radius_meters=radius,
        categories=categories,
    )
    context_expr = contextual_boost_expression(
        occasion=occasion,
        time_of_day=time_of_day,
        weather=weather_condition,
    )
    composite_expr = combine_score_components(hybrid_expr, context_expr)
    
    pipeline.append({
        "$addFields": {
            "hybrid_score": hybrid_expr,
            "contextual_score": context_expr,
            "composite_score": composite_expr,
        }
    })
    
    pipeline.extend([
        {"$sort": {"composite_score": -1}},
        {"$limit": limit},
    ])
    
    # Execute query
    results = list(mongo_client.pois.aggregate(pipeline))
    
    # Format results
    if not results:
        return [types.TextContent(
            type="text",
            text="No POIs found matching your criteria. Try increasing the search radius or adjusting filters."
        )]
    
    # Build response
    response_text = f"Found {len(results)} POI(s) within {radius}m:\n\n"
    
    for i, poi in enumerate(results, 1):
        stars = poi.get("prestige", {}).get("michelin_stars")
        stars_str = f" {'⭐' * stars}" if stars else ""
        score = poi.get("composite_score") or poi.get("hybrid_score")
        context_reasons = []
        if occasion and occasion in poi.get("best_for", {}).get("occasions", []):
            context_reasons.append(occasion.replace("-", " "))
        if time_of_day and time_of_day in poi.get("best_for", {}).get("time_of_day", []):
            context_reasons.append(time_of_day)
        if weather_condition and weather_condition in poi.get("best_for", {}).get("weather", []):
            context_reasons.append(f"{weather_condition} friendly")
        
        response_text += f"{i}. **{poi['name']}**{stars_str}\n"
        response_text += f"   📍 {poi.get('address', {}).get('street', 'N/A')}, {poi.get('address', {}).get('neighborhood', '')}\n"
        response_text += f"   📏 Distance: {poi.get('distance', 0):.0f}m\n"
        response_text += f"   ⭐ Prestige Score: {poi.get('prestige', {}).get('score', 0)}\n"
        if score:
            response_text += f"   ⚖️ Hybrid Score: {score:.1f}\n"
        response_text += f"   💰 Price: {poi.get('experience', {}).get('price_range', 'N/A')}\n"
        response_text += f"   📞 {poi.get('contact', {}).get('phone', 'N/A')}\n"
        if context_reasons:
            response_text += f"   🎯 Context fit: {', '.join(context_reasons)}\n"
        
        if poi.get('experience', {}).get('signature_dishes'):
            dishes = poi['experience']['signature_dishes'][:2]
            response_text += f"   🍽️  Signature: {', '.join(dishes)}\n"
        
        response_text += "\n"
    
    return [types.TextContent(type="text", text=response_text)]


async def contextual_recommendations_tool(args: Dict[str, Any]) -> list[types.TextContent]:
    """Execute context-aware recommendations"""
    
    lat = args["latitude"]
    lon = args["longitude"]
    radius = args.get("radius_meters", 3000)
    datetime_str = args.get("datetime")
    weather = args.get("weather", "any")
    occasion = args.get("occasion")
    group_size = args.get("group_size", 2)
    budget = args.get("budget")
    limit = args.get("limit", 5)
    
    # Parse datetime
    if datetime_str:
        dt = datetime.fromisoformat(datetime_str)
    else:
        dt = datetime.now()
    
    hour = dt.hour
    time_of_day = "lunch" if 11 <= hour < 15 else "dinner" if 17 <= hour < 23 else "any"
    
    # Build pipeline
    pipeline = [
        {
            "$geoNear": {
                "near": {"type": "Point", "coordinates": [lon, lat]},
                "distanceField": "distance",
                "maxDistance": radius,
                "spherical": True
            }
        }
    ]
    
    # Build match conditions
    match_conditions: List[Dict[str, Any]] = []
    if budget and budget != "any":
        match_conditions.append({"experience.price_range": budget})
    if weather and weather != "any":
        match_conditions.append({
            "$or": [
                {"best_for.weather": {"$in": ["any", weather]}},
                {"best_for.weather": {"$exists": False}}
            ]
        })
    
    if match_conditions:
        pipeline.append({"$match": {"$and": match_conditions}})
    
    hybrid_expr = hybrid_score_expression(radius_meters=radius)
    context_expr = contextual_boost_expression(
        occasion=occasion,
        time_of_day=time_of_day if time_of_day != "any" else None,
        weather=weather,
        group_size=group_size,
        budget=budget,
    )
    relevance_expr = combine_score_components(hybrid_expr, context_expr)
    
    pipeline.append({
        "$addFields": {
            "hybrid_score": hybrid_expr,
            "contextual_score": context_expr,
            "relevance_score": relevance_expr
        }
    })
    
    pipeline.extend([
        {"$sort": {"relevance_score": -1}},
        {"$limit": limit}
    ])
    
    # Execute
    results = list(mongo_client.pois.aggregate(pipeline))
    
    if not results:
        return [types.TextContent(
            type="text",
            text=f"No recommendations found for {occasion or 'your occasion'} near you. Try adjusting your preferences."
        )]
    
    # Build contextual response
    response_text = f"🎯 **Personalized Recommendations**\n\n"
    response_text += f"📍 Location: {lat:.4f}, {lon:.4f}\n"
    response_text += f"🕐 Time: {dt.strftime('%A, %B %d at %I:%M %p')}\n"
    if occasion:
        response_text += f"🎉 Occasion: {occasion.replace('-', ' ').title()}\n"
    if weather and weather != "any":
        response_text += f"🌤️  Weather: {weather.title()}\n"
    response_text += f"👥 Party Size: {group_size}\n"
    if budget and budget != "any":
        response_text += f"💰 Budget: {budget}\n"
    response_text += f"\n---\n\n"
    
    for i, poi in enumerate(results, 1):
        stars = poi.get("prestige", {}).get("michelin_stars")
        stars_str = f" {'⭐' * stars}" if stars else ""
        score = poi.get("relevance_score") or poi.get("hybrid_score")
        
        response_text += f"**{i}. {poi['name']}**{stars_str}\n"
        response_text += f"   {poi.get('address', {}).get('neighborhood', '')} · {poi.get('distance', 0):.0f}m away\n"
        response_text += f"   💰 {poi.get('experience', {}).get('price_range', 'N/A')} · "
        response_text += f"Prestige: {poi.get('prestige', {}).get('score', 0)}"
        if score:
            response_text += f" · ⚖️ {score:.1f}"
        response_text += "\n"
        
        # Why this recommendation
        reasons = []
        if occasion and occasion in poi.get('best_for', {}).get('occasions', []):
            reasons.append(f"Perfect for {occasion.replace('-', ' ')}")
        if time_of_day and time_of_day in poi.get('best_for', {}).get('time_of_day', []):
            reasons.append(time_of_day.title())
        if weather and weather != "any" and weather in poi.get('best_for', {}).get('weather', []):
            reasons.append(f"{weather} friendly")
        if budget and budget == poi.get('experience', {}).get('price_range'):
            reasons.append("Budget match")
        if stars:
            reasons.append(f"{stars}-Michelin-star")
        if poi.get('distance', 0) < 1000:
            reasons.append("Very close")
        
        if reasons:
            response_text += f"   ✨ {' · '.join(reasons)}\n"
        
        response_text += f"   📞 {poi.get('contact', {}).get('phone', 'N/A')}\n\n"
    
    return [types.TextContent(type="text", text=response_text)]


async def enrich_poi_live_tool(args: Dict[str, Any]) -> list[types.TextContent]:
    """Execute real-time POI enrichment using Tavily trusted sources."""
    
    poi_name = args["poi_name"]
    poi_address = args.get("poi_address", "")
    category = args.get("category", "restaurant")
    
    try:
        # Call Tavily enrichment
        enriched_text = await enrich_poi_live(
            poi_name=poi_name,
            poi_address=poi_address,
            category=category
        )
        
        return [types.TextContent(type="text", text=enriched_text)]
        
    except Exception as e:
        error_text = f"❌ Failed to enrich {poi_name}: {str(e)}\n\n"
        error_text += "This tool requires TAVILY_API_KEY to be set in your environment."
        return [types.TextContent(type="text", text=error_text)]


async def init_mongo() -> bool:
    """Initialize MongoDB connection"""
    global mongo_client
    
    print("🔌 Connecting to MongoDB...", file=sys.stderr)
    mongo_client = MongoDBClient()
    
    if not mongo_client.connect():
        print("❌ Failed to connect to MongoDB", file=sys.stderr)
        return False
    
    print(f"✅ Connected to MongoDB: {mongo_client.database_name}", file=sys.stderr)
    print(f"📦 Collection: {mongo_client.collection_name}", file=sys.stderr)
    
    # Get POI count
    count = mongo_client.pois.count_documents({})
    print(f"🗄️  POIs available: {count}", file=sys.stderr)
    return True


async def main():
    """Main server entry point"""
    if not await init_mongo():
        sys.exit(1)
    
    print("\n🚀 NYC POI Concierge MCP Server starting...", file=sys.stderr)
    print("="*60, file=sys.stderr)
    
    # Run server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="nyc-poi-concierge",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
