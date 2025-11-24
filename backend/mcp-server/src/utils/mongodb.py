"""
MongoDB Atlas Integration for NYC POI Concierge
Handles connection, schema creation, and data operations
"""

import os
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from pymongo import MongoClient, GEOSPHERE, ASCENDING, DESCENDING
    from pymongo.errors import ConnectionFailure, OperationFailure
except ImportError:
    logger.info("Installing pymongo...")
    os.system("python3 -m pip install pymongo")
    from pymongo import MongoClient, GEOSPHERE, ASCENDING, DESCENDING
    from pymongo.errors import ConnectionFailure, OperationFailure


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
            logger.info(f"🔌 Connecting to MongoDB Atlas...")
            
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
            
            logger.info(f"✅ Connected to database: {self.database_name}")
            logger.info(f"✅ Using collection: {self.collection_name}")
            
            return True
            
        except ConnectionFailure as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            return False
    
    def setup_indexes(self) -> bool:
        """Create required indexes for optimal query performance"""
        if not self.pois:
            logger.error("❌ Not connected to MongoDB")
            return False
        
        try:
            logger.info("\n📇 Setting up indexes...")
            
            # 1. Geospatial Index (required for location queries)
            logger.info("  Creating geospatial index on 'location'...")
            self.pois.create_index(
                [("location", GEOSPHERE)],
                name="location_2dsphere"
            )
            
            # 2. Category and Prestige Index
            logger.info("  Creating category + prestige index...")
            self.pois.create_index(
                [
                    ("category", ASCENDING),
                    ("address.borough", ASCENDING),
                    ("prestige.score", DESCENDING)
                ],
                name="category_borough_prestige"
            )
            
            # 3. Prestige Ranking Index
            logger.info("  Creating prestige ranking index...")
            self.pois.create_index(
                [("prestige.score", DESCENDING)],
                name="prestige_ranking"
            )
            
            # 4. Text Search Index
            logger.info("  Creating text search index...")
            self.pois.create_index(
                [
                    ("name", "text"),
                    ("experience.signature_dishes", "text")
                ],
                name="text_search"
            )
            
            # 5. Validation Status Index
            logger.info("  Creating validation status index...")
            self.pois.create_index(
                [("validation_status", ASCENDING)],
                name="validation_status"
            )
            
            logger.info("✅ All indexes created successfully")
            
            # List all indexes
            indexes = list(self.pois.list_indexes())
            logger.info(f"\n📊 Total indexes: {len(indexes)}")
            for idx in indexes:
                logger.info(f"  - {idx['name']}")
            
            return True
            
        except OperationFailure as e:
            logger.error(f"❌ Index creation failed: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            return False
    
    def import_pois(self, pois: List[Dict], replace_all: bool = False) -> int:
        """Import POI documents to MongoDB"""
        if not self.pois:
            logger.error("❌ Not connected to MongoDB")
            return 0
        
        try:
            if replace_all:
                logger.warning("⚠️  Clearing existing POIs...")
                result = self.pois.delete_many({})
                logger.info(f"  Deleted {result.deleted_count} existing POIs")
            
            logger.info(f"\n📥 Importing {len(pois)} POIs...")
            
            # Add metadata
            for poi in pois:
                if "created_at" not in poi:
                    poi["created_at"] = datetime.now().isoformat()
                poi["updated_at"] = datetime.now().isoformat()
            
            # Bulk insert
            result = self.pois.insert_many(pois, ordered=False)
            
            inserted_count = len(result.inserted_ids)
            logger.info(f"✅ Imported {inserted_count} POIs successfully")
            
            return inserted_count
            
        except Exception as e:
            logger.error(f"❌ Import failed: {e}")
            return 0
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the POI collection"""
        if not self.pois:
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
            logger.warning(f"⚠️  Could not fetch stats: {e}")
            return {}
    
    def test_geospatial_query(self, lat: float = 40.7580, lon: float = -73.9851, radius_meters: int = 2000) -> List[Dict]:
        """Test geospatial query (Times Square area by default)"""
        if not self.pois:
            logger.error("❌ Not connected to MongoDB")
            return []
        
        try:
            logger.info(f"\n🗺️  Testing geospatial query...")
            logger.info(f"  Location: ({lat}, {lon})")
            logger.info(f"  Radius: {radius_meters}m")
            
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
            
            logger.info(f"✅ Found {len(results)} POIs")
            for i, poi in enumerate(results, 1):
                stars = poi.get("prestige", {}).get("michelin_stars")
                stars_str = f" ({'⭐' * stars})" if stars else ""
                logger.info(f"  {i}. {poi['name']}{stars_str}")
                logger.info(f"     {poi.get('address', {}).get('street', 'N/A')}")
                logger.info(f"     Distance: {poi.get('distance', 0):.0f}m | Prestige: {poi.get('prestige', {}).get('score', 0)}")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Query failed: {e}")
            return []
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("\n👋 MongoDB connection closed")


def main():
    """Test MongoDB connection and setup"""
    
    print("=" * 60)
    print("NYC POI MongoDB Atlas Setup")
    print("=" * 60)
    
    # Initialize client
    mongo = MongoDBClient()
    
    # Connect
    if not mongo.connect():
        return
    
    # Setup indexes
    mongo.setup_indexes()
    
    # Get stats
    stats = mongo.get_collection_stats()
    
    print("\n📊 Collection Statistics")
    print("-" * 60)
    print(f"Total POIs: {stats.get('total_pois', 0)}")
    print(f"Storage size: {stats.get('storage_size', 0) / 1024:.2f} KB")
    print(f"Indexes: {stats.get('indexes', 0)}")
    
    if stats.get('category_breakdown'):
        print("\nCategory Breakdown:")
        for category, count in stats['category_breakdown'].items():
            print(f"  {category}: {count}")
    
    if stats.get('michelin_breakdown'):
        print("\nMichelin Stars:")
        for level, count in stats['michelin_breakdown'].items():
            if count > 0:
                print(f"  {level}: {count}")
    
    # Test geospatial query if we have POIs
    if stats.get('total_pois', 0) > 0:
        mongo.test_geospatial_query()
    
    # Close connection
    mongo.close()
    
    print("\n" + "=" * 60)
    print("Setup complete! ✨")
    print("=" * 60)


if __name__ == "__main__":
    main()
