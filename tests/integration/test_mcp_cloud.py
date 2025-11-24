#!/usr/bin/env python3
"""
Integration test for MCP Cloud deployment
Tests the deployed MCP server at LastMile AI Cloud
"""

import os
import sys
import json
import httpx
import asyncio
from datetime import datetime
from typing import Dict, Any, List

# MCP Cloud endpoint
MCP_SERVER_URL = "https://15csm9y282hdasy6yvu2l7244j9vcrfc.deployments.mcp-agent.com"

class Color:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Color.BOLD}{Color.BLUE}{'='*80}{Color.END}")
    print(f"{Color.BOLD}{Color.BLUE}{text.center(80)}{Color.END}")
    print(f"{Color.BOLD}{Color.BLUE}{'='*80}{Color.END}\n")

def print_success(text: str):
    """Print success message"""
    print(f"{Color.GREEN}✅ {text}{Color.END}")

def print_error(text: str):
    """Print error message"""
    print(f"{Color.RED}❌ {text}{Color.END}")

def print_info(text: str):
    """Print info message"""
    print(f"{Color.YELLOW}ℹ️  {text}{Color.END}")

async def test_health_check():
    """Test 1: Health check endpoint"""
    print_header("Test 1: Health Check")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{MCP_SERVER_URL}/health")
            
            if response.status_code == 200:
                print_success(f"Health check passed (status: {response.status_code})")
                print_info(f"Response: {response.text}")
                return True
            else:
                print_error(f"Health check failed (status: {response.status_code})")
                return False
                
    except Exception as e:
        print_error(f"Health check failed: {str(e)}")
        return False

async def test_mcp_tools_list():
    """Test 2: List available MCP tools"""
    print_header("Test 2: List MCP Tools")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # MCP uses SSE endpoint for tool discovery
            response = await client.post(
                f"{MCP_SERVER_URL}/sse",
                json={
                    "jsonrpc": "2.0",
                    "method": "tools/list",
                    "id": 1
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "result" in data and "tools" in data["result"]:
                    tools = data["result"]["tools"]
                    print_success(f"Found {len(tools)} MCP tools:")
                    for tool in tools:
                        print(f"  - {Color.BOLD}{tool['name']}{Color.END}: {tool.get('description', 'No description')}")
                    return True
                else:
                    print_error("Invalid tools list response")
                    return False
            else:
                print_error(f"Tools list failed (status: {response.status_code})")
                return False
                
    except Exception as e:
        print_error(f"Tools list failed: {str(e)}")
        return False

async def test_query_pois():
    """Test 3: Query POIs tool"""
    print_header("Test 3: Query POIs (Times Square)")
    
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Test query_pois near Times Square
            payload = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "query_pois",
                    "arguments": {
                        "latitude": 40.7580,
                        "longitude": -73.9851,
                        "radius_meters": 2000,
                        "limit": 5
                    }
                },
                "id": 2
            }
            
            print_info(f"Searching for POIs near Times Square (40.7580, -73.9851)")
            
            response = await client.post(
                f"{MCP_SERVER_URL}/sse",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "result" in data:
                    result = data["result"]
                    # Parse the content (MCP returns text content)
                    content = result.get("content", [])
                    if content:
                        text_content = content[0].get("text", "") if isinstance(content, list) else str(content)
                        print_success("Query POIs successful!")
                        print(f"\n{Color.BOLD}Results:{Color.END}")
                        print(text_content[:500] + "..." if len(text_content) > 500 else text_content)
                        return True
                    else:
                        print_error("No POIs found in response")
                        return False
                else:
                    print_error(f"Invalid response: {data}")
                    return False
            else:
                print_error(f"Query POIs failed (status: {response.status_code})")
                print_info(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print_error(f"Query POIs failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_contextual_recommendations():
    """Test 4: Contextual recommendations tool"""
    print_header("Test 4: Contextual Recommendations (Date Night)")
    
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Test contextual recommendations for date night
            payload = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "get_contextual_recommendations",
                    "arguments": {
                        "latitude": 40.7580,
                        "longitude": -73.9851,
                        "occasion": "date-night",
                        "group_size": 2,
                        "budget": "$$$",
                        "limit": 3
                    }
                },
                "id": 3
            }
            
            print_info(f"Getting date night recommendations near Times Square")
            
            response = await client.post(
                f"{MCP_SERVER_URL}/sse",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "result" in data:
                    result = data["result"]
                    content = result.get("content", [])
                    if content:
                        text_content = content[0].get("text", "") if isinstance(content, list) else str(content)
                        print_success("Contextual recommendations successful!")
                        print(f"\n{Color.BOLD}Recommendations:{Color.END}")
                        print(text_content[:500] + "..." if len(text_content) > 500 else text_content)
                        return True
                    else:
                        print_error("No recommendations found in response")
                        return False
                else:
                    print_error(f"Invalid response: {data}")
                    return False
            else:
                print_error(f"Contextual recommendations failed (status: {response.status_code})")
                print_info(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print_error(f"Contextual recommendations failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_database_connectivity():
    """Test 5: Verify database has data"""
    print_header("Test 5: Database Connectivity")
    
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Query all categories to verify database
            payload = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "query_pois",
                    "arguments": {
                        "latitude": 40.7580,
                        "longitude": -73.9851,
                        "radius_meters": 10000,  # 10km to get more results
                        "limit": 20
                    }
                },
                "id": 4
            }
            
            print_info(f"Querying database for POIs (10km radius)")
            
            response = await client.post(
                f"{MCP_SERVER_URL}/sse",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "result" in data:
                    result = data["result"]
                    content = result.get("content", [])
                    if content:
                        text_content = content[0].get("text", "") if isinstance(content, list) else str(content)
                        # Count POIs mentioned
                        poi_count = text_content.count("POI:")
                        print_success(f"Database connectivity verified! Found ~{poi_count} POIs")
                        return True
                    else:
                        print_error("No data found in database")
                        return False
                else:
                    print_error(f"Invalid response: {data}")
                    return False
            else:
                print_error(f"Database query failed (status: {response.status_code})")
                return False
                
    except Exception as e:
        print_error(f"Database connectivity test failed: {str(e)}")
        return False

async def run_all_tests():
    """Run all integration tests"""
    print_header("MCP Cloud Integration Tests")
    print(f"{Color.BOLD}MCP Server URL:{Color.END} {MCP_SERVER_URL}")
    print(f"{Color.BOLD}Test Time:{Color.END} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    tests = [
        ("Health Check", test_health_check),
        ("MCP Tools List", test_mcp_tools_list),
        ("Query POIs", test_query_pois),
        ("Contextual Recommendations", test_contextual_recommendations),
        ("Database Connectivity", test_database_connectivity),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"Test '{test_name}' crashed: {str(e)}")
            results.append((test_name, False))
        
        # Small delay between tests
        await asyncio.sleep(0.5)
    
    # Print summary
    print_header("Test Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = f"{Color.GREEN}PASSED{Color.END}" if result else f"{Color.RED}FAILED{Color.END}"
        print(f"  {test_name:.<50} {status}")
    
    print(f"\n{Color.BOLD}Total: {passed}/{total} tests passed{Color.END}")
    
    if passed == total:
        print(f"\n{Color.GREEN}{Color.BOLD}🎉 ALL TESTS PASSED! MCP Cloud server is working correctly.{Color.END}\n")
        return 0
    else:
        print(f"\n{Color.RED}{Color.BOLD}⚠️  Some tests failed. Review the output above.{Color.END}\n")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(run_all_tests())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n{Color.YELLOW}Tests interrupted by user{Color.END}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Test suite crashed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
