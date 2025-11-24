"""
Data Processing Pipeline
Processes Tavily-curated POIs and imports them to MongoDB
"""

import json
import asyncio
from pathlib import Path
from typing import List, Dict, Optional
import sys
import os
from datetime import datetime

# MongoDB imports
try:
    from pymongo import MongoClient, GEOSPHERE, ASCENDING, DESCENDING
    from pymongo.errors import ConnectionFailure, OperationFailure
except ImportError:
    print("Installing pymongo...")
    os.system("python3 -m pip install pymongo")
    from pymongo import MongoClient, GEOSPHERE, ASCENDING, DESCENDING
    from pymongo.errors import ConnectionFailure, OperationFailure


# Embedded MongoDB Client
class MongoDBClient:
    """MongoDB Atlas client for POI data management"""
    
    def __init__(
        self,
        uri: str = None,
        database: str = "nyc-poi",
        collection: str = "pois"
    ):
        """Initialize MongoDB connection"""
        self.uri = uri or os.getenv("MONGODB_URI")
        
        if not self.uri:
            raise ValueError("MongoDB URI is required. Set MONGODB_URI environment variable or pass uri parameter.")
        
        self.database_name = database
        self.collection_name = collection
        
        # Connection
        self.client: Optional[MongoClient] = None
        self.db = None
        self.pois = None
        
    def connect(self) -> bool:
        """Establish connection to MongoDB Atlas"""
        try:
            print(f"🔌 Connecting to MongoDB Atlas...")
            
            self.client = MongoClient(
                self.uri,
                serverSelectionTimeoutMS=5000,
                maxPoolSize=10
            )
            
            # Test connection
            self.client.admin.command('ping')
            
            # Get database and collection
            self.db = self.client[self.database_name]
            self.pois = self.db[self.collection_name]
            
            print(f"✅ Connected to database: {self.database_name}")
            print(f"✅ Using collection: {self.collection_name}")
            
            return True
            
        except ConnectionFailure as e:
            print(f"❌ MongoDB connection failed: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
    
    def setup_indexes(self) -> bool:
        """Create required indexes for optimal query performance"""
        if self.pois is None:
            print("❌ Not connected to MongoDB")
            return False
        
        try:
            print("\n📇 Setting up indexes...")
            
            # 1. Geospatial Index (required for location queries)
            print("  Creating geospatial index on 'location'...")
            self.pois.create_index(
                [("location", GEOSPHERE)],
                name="location_2dsphere"
            )
            
            # 2. Category and Prestige Index
            print("  Creating category + prestige index...")
            self.pois.create_index(
                [
                    ("category", ASCENDING),
                    ("address.borough", ASCENDING),
                    ("prestige.score", DESCENDING)
                ],
                name="category_borough_prestige"
            )
            
            # 3. Prestige Ranking Index
            print("  Creating prestige ranking index...")
            self.pois.create_index(
                [("prestige.score", DESCENDING)],
                name="prestige_ranking"
            )
            
            # 4. Text Search Index
            print("  Creating text search index...")
            self.pois.create_index(
                [
                    ("name", "text"),
                    ("experience.signature_dishes", "text")
                ],
                name="text_search"
            )
            
            print("✅ Indexes created successfully")
            
            return True
            
        except OperationFailure as e:
            print(f"❌ Index creation failed: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
    
    def import_pois(self, pois: List[Dict], replace_all: bool = False) -> int:
        """Import POI documents to MongoDB"""
        if self.pois is None:
            print("❌ Not connected to MongoDB")
            return 0
        
        try:
            if replace_all:
                print("⚠️  Clearing existing POIs...")
                result = self.pois.delete_many({})
                print(f"  Deleted {result.deleted_count} existing POIs")
            
            print(f"\n📥 Importing {len(pois)} POIs...")
            
            # Add metadata
            for poi in pois:
                if "created_at" not in poi:
                    poi["created_at"] = datetime.now().isoformat()
                poi["updated_at"] = datetime.now().isoformat()
            
            # Bulk insert
            result = self.pois.insert_many(pois, ordered=False)
            
            inserted_count = len(result.inserted_ids)
            print(f"✅ Imported {inserted_count} POIs successfully")
            
            return inserted_count
            
        except Exception as e:
            print(f"❌ Import failed: {e}")
            return 0
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the POI collection"""
        if self.pois is None:
            return {}
        
        try:
            stats = self.db.command("collStats", self.collection_name)
            
            # Get category breakdown
            category_counts = {}
            for category in ["fine-dining", "casual-dining", "bars-cocktails"]:
                count = self.pois.count_documents({"category": category})
                category_counts[category] = count
            
            # Get prestige distribution
            michelin_counts = {}
            for stars in [1, 2, 3]:
                count = self.pois.count_documents({"prestige.michelin_stars": stars})
                michelin_counts[f"{stars}_star"] = count
            
            return {
                "total_pois": stats.get("count", 0),
                "size_bytes": stats.get("size", 0),
                "avg_obj_size": stats.get("avgObjSize", 0),
                "storage_size": stats.get("storageSize", 0),
                "indexes": stats.get("nindexes", 0),
                "category_breakdown": category_counts,
                "michelin_breakdown": michelin_counts
            }
            
        except Exception as e:
            print(f"⚠️  Could not fetch stats: {e}")
            return {}
    
    def test_geospatial_query(self, lat: float = 40.7580, lon: float = -73.9851, radius_meters: int = 2000) -> List[Dict]:
        """Test geospatial query (Times Square area by default)"""
        if not self.pois:
            print("❌ Not connected to MongoDB")
            return []
        
        try:
            print(f"\n🗺️  Testing geospatial query...")
            print(f"  Location: ({lat}, {lon})")
            print(f"  Radius: {radius_meters}m")
            
            pipeline = [
                {
                    "$geoNear": {
                        "near": {
                            "type": "Point",
                            "coordinates": [lon, lat]
                        },
                        "distanceField": "distance",
                        "maxDistance": radius_meters,
                        "spherical": True
                    }
                },
                {
                    "$sort": {"prestige.score": -1, "distance": 1}
                },
                {
                    "$limit": 5
                },
                {
                    "$project": {
                        "name": 1,
                        "category": 1,
                        "distance": 1,
                        "prestige.score": 1,
                        "prestige.michelin_stars": 1,
                        "address.street": 1
                    }
                }
            ]
            
            results = list(self.pois.aggregate(pipeline))
            
            print(f"✅ Found {len(results)} POIs")
            for i, poi in enumerate(results, 1):
                stars = poi.get("prestige", {}).get("michelin_stars")
                stars_str = f" ({'⭐' * stars})" if stars else ""
                print(f"  {i}. {poi['name']}{stars_str}")
                print(f"     {poi.get('address', {}).get('street', 'N/A')}")
                print(f"     Distance: {poi.get('distance', 0):.0f}m | Prestige: {poi.get('prestige', {}).get('score', 0)}")
            
            return results
            
        except Exception as e:
            print(f"❌ Query failed: {e}")
            return []
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            print("\n👋 MongoDB connection closed")


def load_mock_pois() -> List[Dict]:
    """Load mock POI data for testing"""
    mock_data_path = Path(__file__).parent.parent.parent.parent / "data" / "mock" / "sample_pois.json"
    
    print(f"📂 Loading mock data from: {mock_data_path}")
    
    with open(mock_data_path, 'r') as f:
        pois = json.load(f)
    
    print(f"✅ Loaded {len(pois)} mock POIs")
    return pois


def load_enriched_pois() -> List[Dict]:
    """Load enriched POIs from Tavily curation"""
    data_path = Path(__file__).parent.parent.parent.parent / "data" / "raw" / "enriched_pois.json"
    
    if not data_path.exists():
        print(f"⚠️  Enriched POIs not found at: {data_path}")
        print("   Using mock data instead...")
        return load_mock_pois()
    
    print(f"📂 Loading enriched POIs from: {data_path}")
    
    with open(data_path, 'r') as f:
        pois = json.load(f)
    
    print(f"✅ Loaded {len(pois)} enriched POIs")
    return pois


def validate_poi_schema(poi: Dict) -> bool:
    """Validate that POI has required fields"""
    required_fields = ["name", "category", "location", "address", "prestige"]
    
    for field in required_fields:
        if field not in poi:
            print(f"⚠️  POI '{poi.get('name', 'Unknown')}' missing field: {field}")
            return False
    
    # Validate location coordinates
    if not poi["location"].get("coordinates") or poi["location"]["coordinates"] == [0, 0]:
        print(f"⚠️  POI '{poi['name']}' has invalid coordinates")
        return False
    
    return True


def enrich_pois_with_metadata(pois: List[Dict]) -> List[Dict]:
    """Add additional metadata to POIs before import"""
    enriched = []
    
    for poi in pois:
        # Ensure all POIs have embedding placeholder
        if "embedding" not in poi:
            poi["embedding_text"] = f"{poi['name']} - {poi.get('category', '')} restaurant in {poi.get('address', {}).get('neighborhood', 'Manhattan')}"
            poi["embedding"] = None  # Will be generated later with OpenAI
        
        # Add data quality score
        if "data_quality_score" not in poi:
            score = 0.5
            # Increase score based on available data
            if poi.get("prestige", {}).get("michelin_stars"):
                score += 0.2
            if poi.get("contact", {}).get("phone"):
                score += 0.1
            if poi.get("experience", {}).get("signature_dishes"):
                score += 0.1
            if len(poi.get("sources", [])) > 1:
                score += 0.1
            
            poi["data_quality_score"] = min(score, 1.0)
        
        enriched.append(poi)
    
    return enriched


async def main():
    """Main import pipeline"""
    
    print("=" * 70)
    print("NYC POI Data Import Pipeline")
    print("MongoDB x Tavily x LastMile AI Hackathon")
    print("=" * 70)
    
    # Step 1: Load POI data
    print("\n📥 Step 1: Loading POI Data")
    print("-" * 70)
    
    use_mock = os.getenv("USE_MOCK_DATA", "true").lower() == "true"
    
    if use_mock:
        print("🎭 Using MOCK data for parallel development")
        pois = load_mock_pois()
    else:
        print("🌐 Using REAL data from Tavily curation")
        pois = load_enriched_pois()
    
    # Step 2: Validate schema
    print("\n✅ Step 2: Validating POI Schema")
    print("-" * 70)
    
    valid_pois = [poi for poi in pois if validate_poi_schema(poi)]
    print(f"Valid POIs: {len(valid_pois)}/{len(pois)}")
    
    if not valid_pois:
        print("❌ No valid POIs to import!")
        return
    
    # Step 3: Enrich metadata
    print("\n🔧 Step 3: Enriching POI Metadata")
    print("-" * 70)
    
    enriched_pois = enrich_pois_with_metadata(valid_pois)
    print(f"✅ Enriched {len(enriched_pois)} POIs")
    
    # Step 4: Connect to MongoDB
    print("\n🔌 Step 4: Connecting to MongoDB Atlas")
    print("-" * 70)
    
    mongo = MongoDBClient()
    
    if not mongo.connect():
        print("❌ Failed to connect to MongoDB! Check your connection string.")
        return
    
    # Step 5: Setup indexes
    print("\n📇 Step 5: Setting Up Database Indexes")
    print("-" * 70)
    
    mongo.setup_indexes()
    
    # Step 6: Import POIs
    print("\n💾 Step 6: Importing POIs to MongoDB")
    print("-" * 70)
    
    # Ask user if they want to replace all data
    replace_all = input("\n⚠️  Replace ALL existing POIs? (yes/no): ").lower() == "yes"
    
    imported_count = mongo.import_pois(enriched_pois, replace_all=replace_all)
    
    if imported_count == 0:
        print("❌ Import failed!")
        mongo.close()
        return
    
    # Step 7: Verify import with stats
    print("\n📊 Step 7: Verification - Collection Statistics")
    print("-" * 70)
    
    stats = mongo.get_collection_stats()
    
    print(f"Total POIs in database: {stats.get('total_pois', 0)}")
    print(f"Storage size: {stats.get('storage_size', 0) / 1024:.2f} KB")
    print(f"Avg document size: {stats.get('avg_obj_size', 0) / 1024:.2f} KB")
    print(f"Total indexes: {stats.get('indexes', 0)}")
    
    if stats.get('category_breakdown'):
        print("\nCategory Distribution:")
        for category, count in stats['category_breakdown'].items():
            print(f"  • {category}: {count} POIs")
    
    if stats.get('michelin_breakdown'):
        print("\nMichelin Star Distribution:")
        for level, count in stats['michelin_breakdown'].items():
            if count > 0:
                print(f"  • {level.replace('_', ' ').title()}: {count} restaurants")
    
    # Step 8: Test geospatial query
    print("\n🗺️  Step 8: Testing Geospatial Queries")
    print("-" * 70)
    
    # Times Square location
    mongo.test_geospatial_query(lat=40.7580, lon=-73.9851, radius_meters=2000)
    
    # Close connection
    mongo.close()
    
    # Summary
    print("\n" + "=" * 70)
    print("✨ Import Pipeline Complete!")
    print("=" * 70)
    print(f"\n✅ Successfully imported {imported_count} POIs to MongoDB Atlas")
    print(f"🗄️  Database: nyc-poi")
    print(f"📦 Collection: pois")
    print(f"\nNext steps:")
    print("  1. Generate OpenAI embeddings for semantic search")
    print("  2. Create vector search index in Atlas UI")
    print("  3. Build MCP server tools")
    print("  4. Integrate with Expo mobile app")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
