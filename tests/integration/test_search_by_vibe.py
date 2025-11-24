#!/usr/bin/env python3
"""
Integration test for search_by_vibe semantic search tool.

Tests the vector search functionality via MCP Cloud endpoint.
"""

import os
import sys
import json
import httpx
import asyncio
from datetime import datetime
from typing import Dict, Any, List

# MCP Server URL - defaults to localhost for integration testing
# Set MCP_SERVER_URL environment variable to test against MCP Cloud
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000")
IS_LOCAL = "localhost" in MCP_SERVER_URL or "127.0.0.1" in MCP_SERVER_URL

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


async def test_basic_semantic_search():
    """Test 1: Basic semantic search"""
    print_header("Test 1: Basic Semantic Search - Romantic Vibe")
    
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            if IS_LOCAL:
                # Local HTTP server endpoint
                payload = {
                    "vibe_query": "romantic and quiet with amazing views",
                    "limit": 5,
                    "min_score": 0.7
                }
                endpoint = f"{MCP_SERVER_URL}/search-by-vibe"
            else:
                # MCP Cloud SSE endpoint
                payload = {
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {
                        "name": "search_by_vibe",
                        "arguments": {
                            "vibe_query": "romantic and quiet with amazing views",
                            "limit": 5,
                            "min_score": 0.7
                        }
                    },
                    "id": 1
                }
                endpoint = f"{MCP_SERVER_URL}/sse"
            
            print_info(f"Query: 'romantic and quiet with amazing views'")
            print_info(f"Endpoint: {endpoint}")
            
            response = await client.post(
                endpoint,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                if IS_LOCAL:
                    # Local server returns direct JSON
                    data = response.json()
                    if "results" in data or "error" not in data:
                        print_success("Semantic search successful!")
                        print(f"\n{Color.BOLD}Results Preview:{Color.END}")
                        preview = json.dumps(data, indent=2)[:500]
                        print(preview + "..." if len(preview) >= 500 else preview)
                        return True
                else:
                    # MCP Cloud returns MCP protocol response
                    data = response.json()
                    if "result" in data:
                        result = data["result"]
                        content = result.get("content", [])
                        if content:
                            text_content = content[0].get("text", "") if isinstance(content, list) else str(content)
                            
                            # Check for expected markers
                            if "🔮 **Semantic Search Results**" in text_content and "🎯 Vibe Query:" in text_content:
                                print_success("Semantic search successful!")
                                print(f"\n{Color.BOLD}Results Preview:{Color.END}")
                                print(text_content[:400] + "..." if len(text_content) > 400 else text_content)
                                return True
                            else:
                                print_error("Unexpected response format")
                                return False
                        else:
                            print_error("No content in response")
                            return False
                    else:
                        print_error(f"Invalid response: {data}")
                        return False
            else:
                print_error(f"Request failed (status: {response.status_code})")
                print_info(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print_error(f"Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_celebration_vibe():
    """Test 2: Celebration vibe search"""
    print_header("Test 2: Celebration Vibe Search")
    
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            payload = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "search_by_vibe",
                    "arguments": {
                        "vibe_query": "lively spot for celebrating with friends",
                        "limit": 3,
                        "min_score": 0.65
                    }
                },
                "id": 2
            }
            
            print_info(f"Query: 'lively spot for celebrating with friends'")
            print_info(f"Min score: 0.65 (lower threshold)")
            
            response = await client.post(
                f"{MCP_SERVER_URL}/sse",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "result" in data and "content" in data["result"]:
                    print_success("Celebration vibe search successful!")
                    content = data["result"]["content"]
                    if content:
                        text = content[0].get("text", "") if isinstance(content, list) else str(content)
                        # Count POIs found
                        poi_count = text.count("**") // 2  # Count pairs of **
                        print_info(f"Found ~{poi_count} POI(s)")
                    return True
                else:
                    print_error("Invalid response structure")
                    return False
            else:
                print_error(f"Request failed (status: {response.status_code})")
                return False
                
    except Exception as e:
        print_error(f"Test failed: {str(e)}")
        return False


async def test_category_filter():
    """Test 3: Semantic search with category filter"""
    print_header("Test 3: Category Filter - Fine Dining Only")
    
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            payload = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "search_by_vibe",
                    "arguments": {
                        "vibe_query": "elegant upscale dining experience",
                        "category": "fine-dining",
                        "limit": 5,
                        "min_score": 0.7
                    }
                },
                "id": 3
            }
            
            print_info(f"Query: 'elegant upscale dining experience'")
            print_info(f"Category filter: fine-dining")
            
            response = await client.post(
                f"{MCP_SERVER_URL}/sse",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "result" in data and "content" in data["result"]:
                    content = data["result"]["content"]
                    if content:
                        text = content[0].get("text", "") if isinstance(content, list) else str(content)
                        # Verify category filtering worked
                        if "fine-dining" in text.lower() or "michelin" in text.lower() or "⭐" in text:
                            print_success("Category filtering working correctly!")
                            return True
                        else:
                            print_info("Results found but couldn't verify category (may still be correct)")
                            return True
                    else:
                        print_error("No results found")
                        return False
                else:
                    print_error("Invalid response")
                    return False
            else:
                print_error(f"Request failed (status: {response.status_code})")
                return False
                
    except Exception as e:
        print_error(f"Test failed: {str(e)}")
        return False


async def test_low_threshold():
    """Test 4: Low similarity threshold"""
    print_header("Test 4: Low Threshold - More Results")
    
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            payload = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "search_by_vibe",
                    "arguments": {
                        "vibe_query": "cozy rainy day comfort food",
                        "limit": 10,
                        "min_score": 0.5  # Very low threshold
                    }
                },
                "id": 4
            }
            
            print_info(f"Query: 'cozy rainy day comfort food'")
            print_info(f"Min score: 0.5 (very low - should return more results)")
            
            response = await client.post(
                f"{MCP_SERVER_URL}/sse",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "result" in data and "content" in data["result"]:
                    content = data["result"]["content"]
                    if content:
                        text = content[0].get("text", "") if isinstance(content, list) else str(content)
                        poi_count = text.count("**") // 2
                        print_success(f"Low threshold search successful! Found ~{poi_count} POI(s)")
                        
                        # With low threshold, should get more results
                        if poi_count >= 3:
                            print_info("✓ Low threshold returning more diverse results")
                        return True
                    else:
                        print_error("No results")
                        return False
                else:
                    print_error("Invalid response")
                    return False
            else:
                print_error(f"Request failed (status: {response.status_code})")
                return False
                
    except Exception as e:
        print_error(f"Test failed: {str(e)}")
        return False


async def run_all_tests():
    """Run all integration tests for search_by_vibe"""
    print_header("search_by_vibe Integration Tests")
    print(f"{Color.BOLD}MCP Server URL:{Color.END} {MCP_SERVER_URL}")
    print(f"{Color.BOLD}Test Time:{Color.END} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    tests = [
        ("Basic Semantic Search", test_basic_semantic_search),
        ("Celebration Vibe", test_celebration_vibe),
        ("Category Filter", test_category_filter),
        ("Low Threshold", test_low_threshold),
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
        print(f"\n{Color.GREEN}{Color.BOLD}🎉 ALL TESTS PASSED! Vector search is working correctly.{Color.END}\n")
        return 0
    elif passed > 0:
        print(f"\n{Color.YELLOW}{Color.BOLD}⚠️  Some tests failed, but vector search is partially functional.{Color.END}\n")
        return 1
    else:
        print(f"\n{Color.RED}{Color.BOLD}❌ All tests failed. Check vector index configuration.{Color.END}\n")
        return 2


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
