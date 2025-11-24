"""
NYC POI Concierge - MCP Agent Cloud Entry Point
Wraps the MCP server for cloud deployment
"""

import asyncio
from datetime import datetime

from mcp.server.fastmcp import FastMCP
from mcp_agent.app import MCPApp

from src.config import config
from src.resources import RESOURCE_MAP
from src.utils.mongodb import MongoDBClient
from src.utils.scoring import (
    combine_score_components,
    contextual_boost_expression,
    hybrid_score_expression,
)
from src.utils.tavily_enrichment import enrich_poi_live as tavily_enrich

# Initialize app
mcp_server = FastMCP(
    name="nyc-poi-concierge",
    instructions="Prestige-first NYC concierge with Tavily enrichment and MongoDB hybrid scoring.",
)
app = MCPApp(name="nyc-poi-concierge", mcp=mcp_server)


@mcp_server.resource(
    "nyc-poi://guides/neighborhoods",
    name=RESOURCE_MAP["nyc-poi://guides/neighborhoods"]["name"],
    description=RESOURCE_MAP["nyc-poi://guides/neighborhoods"]["description"],
    mime_type=RESOURCE_MAP["nyc-poi://guides/neighborhoods"]["mime_type"],
)
async def neighborhoods_resource():
    """Static guide cards for flagship neighborhoods."""
    return RESOURCE_MAP["nyc-poi://guides/neighborhoods"]["data"]


@mcp_server.resource(
    "nyc-poi://taxonomy/categories",
    name=RESOURCE_MAP["nyc-poi://taxonomy/categories"]["name"],
    description=RESOURCE_MAP["nyc-poi://taxonomy/categories"]["description"],
    mime_type=RESOURCE_MAP["nyc-poi://taxonomy/categories"]["mime_type"],
)
async def taxonomy_resource():
    """Prestige-first taxonomy referenced by the tools."""
    return RESOURCE_MAP["nyc-poi://taxonomy/categories"]["data"]

# Global MongoDB client
mongo_client = None

async def init_mongo():
    """Initialize MongoDB connection"""
    global mongo_client
    if not mongo_client:
        mongo_client = MongoDBClient()
        if not mongo_client.connect():
            raise RuntimeError("Failed to connect to MongoDB")
    return mongo_client

@app.tool
async def query_pois(
    latitude: float,
    longitude: float,
    radius_meters: int = 2000,
    category: str | None = None,
    min_prestige_score: int = 0,
    limit: int = 10,
    occasion: str | None = None,
    time_of_day: str | None = None,
    weather_condition: str | None = None,
) -> dict:
    """
    Search for NYC restaurants using a hybrid prestige + proximity + context score.
    """
    client = await init_mongo()
    
    pipeline = [
        {
            "$geoNear": {
                "near": {"type": "Point", "coordinates": [longitude, latitude]},
                "distanceField": "distance",
                "maxDistance": radius_meters,
                "spherical": True
            }
        }
    ]
    
    match_conditions = {"prestige.score": {"$gte": min_prestige_score}}
    categories = [category] if category else None
    if categories:
        match_conditions["category"] = {"$in": categories}
    
    if match_conditions:
        pipeline.append({"$match": match_conditions})
    
    hybrid_expr = hybrid_score_expression(
        radius_meters=radius_meters,
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
        {"$limit": limit}
    ])
    
    results = list(client.pois.aggregate(pipeline))
    
    for poi in results:
        poi["_id"] = str(poi["_id"])
    
    enriched_results = []
    for poi in results:
        context_reasons = []
        if occasion and occasion in poi.get("best_for", {}).get("occasions", []):
            context_reasons.append(occasion.replace("-", " "))
        if time_of_day and time_of_day in poi.get("best_for", {}).get("time_of_day", []):
            context_reasons.append(time_of_day)
        if weather_condition and weather_condition in poi.get("best_for", {}).get("weather", []):
            context_reasons.append(f"{weather_condition} friendly")
        poi["context_reasons"] = context_reasons
        enriched_results.append(poi)
    
    return {
        "pois": enriched_results,
        "count": len(enriched_results)
    }

@app.tool
async def get_contextual_recommendations(
    latitude: float,
    longitude: float,
    radius_meters: int = 3000,
    occasion: str | None = None,
    weather_condition: str | None = None,
    time_of_day: str | None = None,
    limit: int = 5,
    group_size: int = 2,
    budget: str | None = None,
) -> dict:
    """
    Rank POIs using prestige, proximity, and real-time context (occasion, weather, budget).
    """
    client = await init_mongo()
    
    if time_of_day is None:
        dt = datetime.utcnow() if config.is_production else datetime.now()
        hour = dt.hour
        time_of_day = "lunch" if 11 <= hour < 15 else "dinner" if 17 <= hour < 23 else "any"
    
    pipeline = [
        {
            "$geoNear": {
                "near": {"type": "Point", "coordinates": [longitude, latitude]},
                "distanceField": "distance",
                "maxDistance": radius_meters,
                "spherical": True
            }
        }
    ]
    
    match_conditions = []
    if budget and budget != "any":
        match_conditions.append({"experience.price_range": budget})
    if weather_condition and weather_condition != "any":
        match_conditions.append({
            "$or": [
                {"best_for.weather": {"$in": ["any", weather_condition]}},
                {"best_for.weather": {"$exists": False}}
            ]
        })
    
    if match_conditions:
        pipeline.append({"$match": {"$and": match_conditions}})
    
    hybrid_expr = hybrid_score_expression(radius_meters=radius_meters)
    context_expr = contextual_boost_expression(
        occasion=occasion,
        time_of_day=time_of_day if time_of_day != "any" else None,
        weather=weather_condition,
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
    
    results = list(client.pois.aggregate(pipeline))
    
    for poi in results:
        poi["_id"] = str(poi["_id"])
        poi["context_reasons"] = []
        if occasion and occasion in poi.get("best_for", {}).get("occasions", []):
            poi["context_reasons"].append(occasion.replace("-", " "))
        if time_of_day and time_of_day in poi.get("best_for", {}).get("time_of_day", []):
            poi["context_reasons"].append(time_of_day)
        if weather_condition and weather_condition in poi.get("best_for", {}).get("weather", []):
            poi["context_reasons"].append(f"{weather_condition} friendly")
        if budget and budget == poi.get("experience", {}).get("price_range"):
            poi["context_reasons"].append("matches budget")
    
    context_parts = []
    if occasion:
        context_parts.append(occasion.replace("-", " "))
    if weather_condition:
        context_parts.append(f"{weather_condition} weather")
    if time_of_day and time_of_day != "any":
        context_parts.append(time_of_day)
    if group_size:
        context_parts.append(f"{group_size} guests")
    if budget and budget != "any":
        context_parts.append(f"{budget} spend")
    
    explanation = (
        f"Based on {' · '.join(context_parts) if context_parts else 'your preferences'}, "
        "here are the top matches ranked by prestige, proximity, and context fit."
    )
    
    return {
        "pois": results,
        "explanation": explanation,
        "count": len(results)
    }


@app.tool
async def enrich_poi_live(
    poi_name: str,
    poi_address: str,
    category: str = "restaurant",
) -> dict:
    """
    Pull last-minute facts for a POI via Tavily trusted sources (Michelin, NYT, Eater, etc.).
    """
    try:
        report = await tavily_enrich(
            poi_name=poi_name,
            poi_address=poi_address,
            category=category,
        )
        return {"summary": report}
    except Exception as exc:  # pragma: no cover - network issues at runtime
        return {
            "summary": f"Failed to enrich {poi_name}: {exc}",
            "error": True,
        }


@app.tool
async def check_poi_freshness(poi_id: str) -> dict:
    """
    Check when a POI was last validated/updated.
    Returns freshness status and age in hours.
    """
    try:
        from bson import ObjectId
        
        client = await init_mongo()
        poi = client.pois.find_one({"_id": ObjectId(poi_id)})
        
        if not poi:
            return {"error": "POI not found", "is_fresh": False}
        
        last_validated = poi.get("last_validated")
        if not last_validated:
            return {
                "is_fresh": False,
                "age_hours": None,
                "updated_at": None,
                "message": "POI has never been validated"
            }
        
        age = datetime.now() - last_validated
        age_hours = age.total_seconds() / 3600
        
        return {
            "updated_at": last_validated.isoformat(),
            "age_hours": round(age_hours, 1),
            "is_fresh": age_hours < 24,
            "message": f"Last updated {age_hours:.1f} hours ago"
        }
    except Exception as e:
        return {"error": str(e), "is_fresh": False}


@app.tool
async def refresh_poi_data(poi_id: str, force: bool = False) -> dict:
    """
    Refresh POI data using Tavily to fetch latest information from the web.
    Updates contact info, hours, and social media, then saves to MongoDB.
    
    Args:
        poi_id: MongoDB ObjectId of the POI to refresh
        force: If True, refresh even if data is recent (<24h)
    
    Returns:
        Updated POI data with freshness info
    """
    try:
        from bson import ObjectId
        from src.utils.tavily_enrichment import refresh_poi_data as tavily_refresh_poi
        
        client = await init_mongo()
        poi = client.pois.find_one({"_id": ObjectId(poi_id)})
        
        if not poi:
            return {"error": "POI not found"}
        
        # Check if refresh needed
        if not force:
            last_validated = poi.get("last_validated")
            if last_validated:
                age = datetime.now() - last_validated
                if age.total_seconds() < 86400:  # 24 hours
                    poi["_id"] = str(poi["_id"])
                    return {
                        "message": "POI is fresh, no refresh needed",
                        "is_fresh": True,
                        "poi": poi
                    }
        
        # Refresh with Tavily
        updated_data = await tavily_refresh_poi(poi)
        
        # Update MongoDB
        update_fields = {"last_validated": datetime.now()}
        
        if updated_data.get("contact"):
            update_fields["contact"] = {**poi.get("contact", {}), **updated_data["contact"]}
        if updated_data.get("hours"):
            update_fields["hours"] = updated_data["hours"]
        if updated_data.get("social"):
            update_fields["social"] = {**poi.get("social", {}), **updated_data["social"]}
        
        client.pois.update_one(
            {"_id": ObjectId(poi_id)},
            {"$set": update_fields}
        )
        
        # Return updated POI
        updated_poi = client.pois.find_one({"_id": ObjectId(poi_id)})
        updated_poi["_id"] = str(updated_poi["_id"])
        
        return {
            "message": "POI refreshed successfully",
            "is_fresh": True,
            "poi": updated_poi,
            "updated_fields": list(update_fields.keys())
        }
    except Exception as e:
        return {"error": str(e), "message": "Refresh failed"}


# ============================================================================
# HTTP Routes for Mobile App Compatibility
# ============================================================================
# NOTE: These routes are commented out for MCP Cloud deployment compatibility.
# MCPApp only supports @app.tool decorators, not FastAPI-style @app.get/@app.post.
# For HTTP API access, use http_server.py which wraps the MCP tools with FastAPI.
# ============================================================================

# @app.get("/health")
# async def health_check():
#     """Health check endpoint for monitoring"""
#     return {
#         "status": "healthy",
#         "service": "nyc-poi-concierge",
#         "timestamp": datetime.now().isoformat()
#     }


# @app.post("/query-pois")
# async def http_query_pois(
#     latitude: float,
#     longitude: float,
#     radius_meters: int = 2000,
#     category: str | None = None,
#     min_prestige_score: int = 0,
#     limit: int = 10,
#     occasion: str | None = None,
#     time_of_day: str | None = None,
#     weather_condition: str | None = None,
# ):
#     """HTTP wrapper for query_pois MCP tool"""
#     return await query_pois(
#         latitude=latitude,
#         longitude=longitude,
#         radius_meters=radius_meters,
#         category=category,
#         min_prestige_score=min_prestige_score,
#         limit=limit,
#         occasion=occasion,
#         time_of_day=time_of_day,
#         weather_condition=weather_condition,
#     )


# @app.post("/recommendations")
# async def http_recommendations(
#     latitude: float,
#     longitude: float,
#     radius_meters: int = 3000,
#     occasion: str | None = None,
#     weather_condition: str | None = None,
#     time_of_day: str | None = None,
#     limit: int = 5,
#     group_size: int = 2,
#     budget: str | None = None,
# ):
#     """HTTP wrapper for get_contextual_recommendations MCP tool"""
#     return await get_contextual_recommendations(
#         latitude=latitude,
#         longitude=longitude,
#         radius_meters=radius_meters,
#         occasion=occasion,
#         weather_condition=weather_condition,
#         time_of_day=time_of_day,
#         limit=limit,
#         group_size=group_size,
#         budget=budget,
#     )


# @app.get("/poi/{poi_id}/freshness")
# async def http_check_freshness(poi_id: str):
#     """HTTP endpoint for POI freshness check"""
#     return await check_poi_freshness(poi_id)


# @app.post("/poi/{poi_id}/refresh")
# async def http_refresh_poi(poi_id: str, force: bool = False):
#     """HTTP endpoint for POI data refresh"""
#     return await refresh_poi_data(poi_id, force)



if __name__ == "__main__":
    asyncio.run(app.run())
