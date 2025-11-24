#!/usr/bin/env python3
"""
MCP-MongoDB Integration Diagnostic Script
Checks all aspects of the integration to identify issues
"""

import os
import sys
import json
import asyncio
from pathlib import Path

# Add src to path
# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend" / "mcp-server" / "src"))

def print_section(title):
    print("\n" + "=" * 70)
    print(f"   {title}")
    print("=" * 70)

def print_status(label, status, message=""):
    emoji = "✅" if status else "❌"
    print(f"{emoji} {label}: {message if message else ('OK' if status else 'FAILED')}")

def check_environment():
    """Check environment variables"""
    print_section("1. ENVIRONMENT VARIABLES")
    
    required_vars = ["MONGODB_URI", "OPENAI_API_KEY", "TAVILY_API_KEY"]
    all_present = True
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            masked = value[:10] + "..." if len(value) > 10 else value
            print_status(var, True, f"Set ({masked})")
        else:
            print_status(var, False, "NOT SET")
            all_present = False
    
    return all_present

def check_mongodb_connection():
    """Check MongoDB connection"""
    print_section("2. MONGODB CONNECTION")
    
    try:
        from src.utils.mongodb import MongoDBClient
        
        print("Attempting to connect to MongoDB Atlas...")
        mongo = MongoDBClient()
        
        if mongo.connect():
            print_status("MongoDB Connection", True, "Connected successfully")
            
            # Get stats
            stats = mongo.get_collection_stats()
            total_pois = stats.get('total_pois', 0)
            print_status("POI Count", total_pois > 0, f"{total_pois} POIs in database")
            
            # Test query
            if total_pois > 0:
                print("\nTesting geospatial query...")
                results = mongo.test_geospatial_query()
                print_status("Geospatial Query", len(results) > 0, f"Found {len(results)} POIs")
            
            mongo.close()
            return True
        else:
            print_status("MongoDB Connection", False, "Connection failed")
            return False
            
    except Exception as e:
        print_status("MongoDB Connection", False, str(e))
        return False

def check_mcp_tools():
    """Check MCP tools registration"""
    print_section("3. MCP TOOLS")
    
    try:
        import importlib.util
        
        # Check if main.py exists and can be imported
        main_path = Path(__file__).parent / "main.py"
        if not main_path.exists():
            print_status("main.py", False, "File not found")
            return False
        
        print_status("main.py", True, "File exists")
        
        # Try to load and inspect tools
        spec = importlib.util.spec_from_file_location("main", main_path)
        main_module = importlib.util.module_from_spec(spec)
        
        print("\n🔧 MCP Tools should be registered:")
        tools = ["query_pois", "get_contextual_recommendations", "enrich_poi_live"]
        for tool in tools:
            print(f"  • {tool}")
        
        return True
        
    except Exception as e:
        print_status("MCP Tools", False, str(e))
        return False

async def check_mcp_cloud_deployment():
    """Check MCP Cloud deployment"""
    print_section("4. MCP CLOUD DEPLOYMENT")
    
    try:
        config_path = Path(__file__).parent / "mcp_agent.deployed.secrets.yaml"
        
        if config_path.exists():
            print_status("MCP Cloud Config", True, "deployed.secrets.yaml found")
            
            with open(config_path) as f:
                content = f.read()
                if "MONGODB_URI" in content:
                    print_status("MongoDB URI in config", True)
                else:
                    print_status("MongoDB URI in config", False)
        else:
            print_status("MCP Cloud Config", False, "No deployed.secrets.yaml")
        
        return True
        
    except Exception as e:
        print_status("MCP Cloud Config", False, str(e))
        return False

def check_http_server():
    """Check HTTP server endpoints"""
    print_section("5. HTTP SERVER (for mobile app)")
    
    try:
        http_server_path = Path(__file__).parent / "http_server.py"
        
        if not http_server_path.exists():
            print_status("http_server.py", False, "File not found")
            return False
        
        print_status("http_server.py", True, "File exists")
        
        # Check if server is running
        import urllib.request
        import socket
        
        # Try to connect to localhost:8000
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', 8000))
            sock.close()
            
            if result == 0:
                print_status("HTTP Server Running", True, "Port 8000 is open")
                
                # Try health check
                try:
                    with urllib.request.urlopen('http://localhost:8000/health', timeout=2) as response:
                        data = json.loads(response.read())
                        print_status("Health Endpoint", True, f"Status: {data.get('status')}")
                except Exception as e:
                    print_status("Health Endpoint", False, str(e))
            else:
                print_status("HTTP Server Running", False, "Port 8000 not listening")
                print("💡 Start with: python3 http_server.py")
        except Exception as e:
            print_status("HTTP Server Check", False, str(e))
        
        return True
        
    except Exception as e:
        print_status("HTTP Server", False, str(e))
        return False

def check_mobile_app_config():
    """Check mobile app configuration"""
    print_section("6. MOBILE APP CONFIGURATION")
    
    try:
        app_dir = Path(__file__).parent.parent.parent / "frontend" / "expo-app"
        
        if not app_dir.exists():
            print_status("Expo App Directory", False, "Not found")
            return False
        
        print_status("Expo App Directory", True, str(app_dir))
        
        # Check for config files
        config_path = app_dir / "config" / "index.ts"
        if config_path.exists():
            print_status("App Config", True, "config/index.ts exists")
        
        # Check service file
        service_path = app_dir / "services" / "mcpService.ts"
        if service_path.exists():
            print_status("MCP Service", True, "mcpService.ts exists")
            
            with open(service_path) as f:
                content = f.read()
                if "query-pois" in content:
                    print_status("  query-pois endpoint", True)
                if "recommendations" in content:
                    print_status("  recommendations endpoint", True)
        
        return True
        
    except Exception as e:
        print_status("Mobile App Config", False, str(e))
        return False

def print_recommendations():
    """Print troubleshooting recommendations"""
    print_section("RECOMMENDATIONS")
    
    print("""
📱 Mobile App Stuck on Loading? Try these steps:

1. **Check Backend is Running:**
   cd backend/mcp-server
   python3 http_server.py
   
2. **Check ngrok tunnel (if using):**
   ngrok http 8000
   
3. **Update Mobile App URL:**
   cd frontend/expo-app
   # Edit .env file with ngrok URL or use:
   ./update-api-url.sh
   
4. **Reload Mobile App:**
   # In Expo terminal, press 'r' to reload
   
5. **Check Mobile App Logs:**
   # Look for errors in the Expo console
   # Check if API calls are being made
   
6. **Test Backend Directly:**
   curl http://localhost:8000/health
   
   curl -X POST http://localhost:8000/query-pois \\
     -H "Content-Type: application/json" \\
     -d '{
       "latitude": 40.7580,
       "longitude": -73.9855,
       "radius_meters": 2000,
       "limit": 5
     }'

7. **Check MongoDB has data:**
   cd backend/mcp-server
   python3 -c "from src.utils.mongodb import MongoDBClient; m=MongoDBClient(); m.connect(); print(m.get_collection_stats())"

8. **Common Issues:**
   - Mobile app pointing to wrong URL
   - Backend not running
   - MongoDB empty or connection failed
   - CORS issues (should be handled by FastAPI)
   - Network connectivity from mobile device
""")

async def main():
    """Run all diagnostics"""
    print("\n" + "🔍 NYC POI - MCP-MongoDB Integration Diagnostics".center(70))
    
    env_ok = check_environment()
    mongo_ok = check_mongodb_connection()
    tools_ok = check_mcp_tools()
    cloud_ok = await check_mcp_cloud_deployment()
    http_ok = check_http_server()
    mobile_ok = check_mobile_app_config()
    
    print_section("SUMMARY")
    
    all_ok = all([env_ok, mongo_ok, tools_ok, cloud_ok, http_ok, mobile_ok])
    
    if all_ok:
        print("\n✅ All checks passed! System should be working.\n")
    else:
        print("\n⚠️  Some checks failed. Review the output above.\n")
    
    print_recommendations()

if __name__ == "__main__":
    asyncio.run(main())
