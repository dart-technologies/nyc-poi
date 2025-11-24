"""
NYC POI Concierge - HTTP API Server
Exposes MCP tools as RESTful HTTP endpoints for ngrok/mobile integration
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from backend/mcp-server directory
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
import asyncio
import time
import logging

from src.utils.mongodb import MongoDBClient
from src.config import config

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="NYC POI Concierge API",
    description="Prestige-first restaurant recommendations",
    version="1.0.0"
)

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log incoming request
    logger.info(f"🔵 INCOMING: {request.method} {request.url.path}")
    logger.info(f"   Headers: {dict(request.headers)}")
    logger.info(f"   Client: {request.client.host if request.client else 'unknown'}")
    
    # Process request
    try:
        response = await call_next(request)
        duration = time.time() - start_time
        
        # Log response
        logger.info(f"✅ RESPONSE: {request.method} {request.url.path} - Status: {response.status_code} - Duration: {duration:.2f}s")
        
        return response
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"❌ ERROR: {request.method} {request.url.path} - {str(e)} - Duration: {duration:.2f}s")
        raise

# Enable CORS for mobile app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global MongoDB client
mongo_client = None

async def get_mongo():
    """Get or create MongoDB connection"""
    global mongo_client
    if not mongo_client:
        mongo_client = MongoDBClient()
        if not mongo_client.connect():
            raise HTTPException(status_code=500, detail="Failed to connect to MongoDB")
    return mongo_client

# Request/Response Models
class QueryPOIsRequest(BaseModel):
    latitude: float
    longitude: float
    radius_meters: int = 2000
    category: Optional[str] = None
    subcategory: Optional[str] = None  # For breakfast, coffee, brunch, etc.
    min_prestige_score: int = 0
    limit: int = 10

class ContextualRecommendationsRequest(BaseModel):
    latitude: float
    longitude: float
    radius_meters: int = 3000
    occasion: Optional[str] = None
    weather_condition: Optional[str] = None
    time_of_day: Optional[str] = None
    limit: int = 5

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "NYC POI Concierge API",
        "status": "running",
        "version": "1.0.0",
        "endpoints": [
            "/query-pois",
            "/recommendations",
            "/health"
        ]
    }

@app.get("/health")
async def health_check():
    """Detailed health check with MongoDB connection status"""
    try:
        client = await get_mongo()
        poi_count = client.pois.count_documents({})
        return {
            "status": "healthy",
            "database": "connected",
            "poi_count": poi_count
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@app.post("/query-pois")
async def query_pois(request: QueryPOIsRequest):
    """
    Search for NYC restaurants with advanced filtering.
    
    Supports geospatial search, category filtering, and prestige filtering.
    Perfect for: "Find Michelin-starred restaurants near me"
    """
    logger.info(f"📍 Query POIs Request: lat={request.latitude}, lon={request.longitude}, radius={request.radius_meters}")
    logger.debug(f"   Filters: category={request.category}, min_prestige={request.min_prestige_score}, limit={request.limit}")
    
    try:
        client = await get_mongo()
        logger.debug("   MongoDB client obtained")
        
        # Build pipeline
        pipeline = [
            {
                "$geoNear": {
                    "near": {"type": "Point", "coordinates": [request.longitude, request.latitude]},
                    "distanceField": "distance",
                    "maxDistance": request.radius_meters,
                    "spherical": True
                }
            }
        ]
        
        # Add filters
        match_conditions = {"prestige.score": {"$gte": request.min_prestige_score}}
        if request.category:
            match_conditions["category"] = request.category
        if request.subcategory:
            match_conditions["subcategories"] = request.subcategory
        
        if match_conditions:
            pipeline.append({"$match": match_conditions})
        
        # Smart sorting: prioritize distance for casual queries, prestige for fine-dining
        if request.subcategory or request.category == 'casual-dining':
            # For coffee, breakfast, casual - people want nearby!
            sort_stage = {"$sort": {"distance": 1, "prestige.score": -1}}
        else:
            # For fine-dining, Michelin - people want quality!
            sort_stage = {"$sort": {"prestige.score": -1, "distance": 1}}
        
        pipeline.extend([
            sort_stage,
            {"$limit": request.limit}
        ])

        
        logger.debug(f"   Executing aggregation pipeline with {len(pipeline)} stages")
        
        # Execute
        results = list(client.pois.aggregate(pipeline))
        logger.info(f"✅ Found {len(results)} POIs")
        
        # Sanitize and validate coordinates
        valid_pois = []
        for poi in results:
            try:
                # Convert ObjectId to string
                poi["_id"] = str(poi["_id"])
                
                # Validate and sanitize coordinates
                if poi.get("location") and poi["location"].get("coordinates"):
                    coords = poi["location"]["coordinates"]
                    
                    # Ensure coordinates are valid numbers
                    if (isinstance(coords, list) and len(coords) >= 2 and
                        isinstance(coords[0], (int, float)) and isinstance(coords[1], (int, float)) and
                        not (isinstance(coords[0], float) and (coords[0] != coords[0])) and  # NaN check
                        not (isinstance(coords[1], float) and (coords[1] != coords[1])) and  # NaN check
                        -180 <= coords[0] <= 180 and  # longitude range
                        -90 <= coords[1] <= 90):  # latitude range
                        
                        # Force to float and round to reasonable precision
                        poi["location"]["coordinates"] = [
                            round(float(coords[0]), 6),  # longitude
                            round(float(coords[1]), 6)   # latitude
                        ]
                        valid_pois.append(poi)
                        logger.debug(f"   ✅ {poi['name']}: coords={poi['location']['coordinates']}")
                    else:
                        logger.warning(f"   ⚠️  Invalid coordinates for {poi.get('name', 'unknown')}: {coords}")
                else:
                    logger.warning(f"   ⚠️  Missing location data for {poi.get('name', 'unknown')}")
            except Exception as e:
                logger.error(f"   ❌ Error sanitizing POI {poi.get('name', 'unknown')}: {str(e)}")
        
        logger.info(f"✅ Returning {len(valid_pois)} POIs with valid coordinates (filtered {len(results) - len(valid_pois)})")
        
        return {
            "pois": valid_pois,
            "count": len(valid_pois)
        }
    except Exception as e:
        logger.error(f"❌ Query failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@app.post("/recommendations")
async def get_recommendations(request: ContextualRecommendationsRequest):
    """
    Get personalized restaurant recommendations based on context.
    
    Analyzes location, time, weather, and occasion for tailored suggestions.
    Perfect for: "Where should I go for a date night tonight?"
    """
    try:
        client = await get_mongo()
        
        # Build pipeline
        pipeline = [
            {
                "$geoNear": {
                    "near": {"type": "Point", "coordinates": [request.longitude, request.latitude]},
                        "distanceField": "distance",
                    "maxDistance": request.radius_meters,
                    "spherical": True
                }
            }
        ]
        
        # Add filters (using OR logic for flexibility, or no filter if POI data is incomplete)
        match_conditions = []
        if request.occasion:
            match_conditions.append({"best_for.occasions": request.occasion})
        if request.time_of_day:
            match_conditions.append({"best_for.time_of_day": request.time_of_day})
        if request.weather_condition:
            match_conditions.append({"best_for.weather": {"$in": ["any", request.weather_condition]}})
        
        # Only apply match if we have conditions, otherwise get all nearby POIs
        if match_conditions:
            pipeline.append({"$match": {"$or": match_conditions}})

        
        # Add relevance scoring
        pipeline.append({
            "$addFields": {
                "relevance_score": {
                    "$add": [
                        {"$multiply": ["$prestige.score", 0.4]},
                        {"$multiply": [{"$divide": [request.radius_meters, "$distance"]}, 30]}
                    ]
                }
            }
        })
        
        pipeline.extend([
            {"$sort": {"relevance_score": -1}},
            {"$limit": request.limit}
        ])
        
        # Execute
        results = list(client.pois.aggregate(pipeline))
        
        # Convert ObjectId to string
        for poi in results:
            poi["_id"] = str(poi["_id"])
        
        # Build explanation
        context_parts = []
        if request.occasion:
            context_parts.append(f"{request.occasion.replace('-', ' ')}")
        if request.weather_condition:
            context_parts.append(f"{request.weather_condition} weather")
        if request.time_of_day:
            context_parts.append(request.time_of_day)
        
        explanation = f"Based on {', '.join(context_parts) if context_parts else 'your preferences'}, here are my top recommendations:"
        
        return {
            "pois": results,
            "explanation": explanation,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendations failed: {str(e)}")

@app.get("/poi/{poi_id}/freshness")
async def check_poi_freshness(poi_id: str):
    """Check when POI was last validated"""
    try:
        client = await get_mongo()
        from bson import ObjectId
        
        poi = client.pois.find_one({"_id": ObjectId(poi_id)})
        
        if not poi:
            raise HTTPException(status_code=404, detail="POI not found")
        
        last_validated = poi.get("last_validated")
        if not last_validated:
            return {
                "is_fresh": False,
                "age_hours": None,
                "updated_at": None
            }
        
        from datetime import datetime
        age = datetime.now() - last_validated
        age_hours = age.total_seconds() / 3600
        
        return {
            "updated_at": last_validated.isoformat(),
            "age_hours": round(age_hours, 1),
            "is_fresh": age_hours < 24
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Freshness check failed: {str(e)}")

@app.post("/poi/{poi_id}/refresh")
async def refresh_poi(poi_id: str, force: bool = False):
    """Refresh POI data using Tavily"""
    try:
        from src.utils.tavily_enrichment import refresh_poi_data
        from bson import ObjectId
        from datetime import datetime
        
        client = await get_mongo()
        poi = client.pois.find_one({"_id": ObjectId(poi_id)})
        
        if not poi:
            raise HTTPException(status_code=404, detail="POI not found")
        
        # Check if refresh needed
        if not force:
            last_validated = poi.get("last_validated")
            if last_validated:
                age = datetime.now() - last_validated
                if age.total_seconds() < 86400:  # 24 hours
                    poi["_id"] = str(poi["_id"])
                    return {
                        "message": "POI is fresh, no refresh needed",
                        "poi": poi
                    }
        
        # Refresh with Tavily
        logger.info(f"🔄 Refreshing POI: {poi.get('name')}")
        updated_data = await refresh_poi_data(poi)
        
        # Update MongoDB
        update_fields = {
            "last_validated": datetime.now(),
        }
        
        # Merge updated data
        if updated_data.get("contact"):
            update_fields["contact"] = {**poi.get("contact", {}), **updated_data["contact"]}
        if updated_data.get("hours"):
            update_fields["hours"] = updated_data["hours"]
        if updated_data.get("social"):
            update_fields["social"] = {**poi.get("social", {}), **updated_data["social"]}
        
        # Store enrichment data for display (Tavily insights)
        if updated_data.get("enrichment_data"):
            update_fields["enrichment_data"] = updated_data["enrichment_data"]
        
        client.pois.update_one(
            {"_id": ObjectId(poi_id)},
            {"$set": update_fields}
        )
        
        # Return updated POI
        updated_poi = client.pois.find_one({"_id": ObjectId(poi_id)})
        
        logger.info(f"✅ POI refreshed: {updated_poi.get('name')}")
        
        # Convert ObjectId to string for JSON serialization
        updated_poi["_id"] = str(updated_poi["_id"])
        
        return {
            "message": "POI refreshed successfully",
            "poi": updated_poi,
            "updated_fields": list(update_fields.keys()),
            "enrichment_data": updated_data.get("enrichment_data")  # Include enrichment for frontend
        }
    except Exception as e:
        logger.error(f"❌ Refresh failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Refresh failed: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting NYC POI Concierge HTTP API Server...")
    print("📍 Local: http://localhost:8000")
    print("📖 Docs: http://localhost:8000/docs")
    print("🔧 Health: http://localhost:8000/health")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
