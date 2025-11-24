#!/usr/bin/env python3
"""
Test if Tavily can extract social media handles from web content
"""

import asyncio
import os
import sys

try:
    from tavily import TavilyClient
except ImportError:
    import subprocess
    subprocess.run(["pip", "install", "tavily-python"], check=True)
    from tavily import TavilyClient


async def test_social_handle_extraction():
    """Test Tavily's ability to extract social media handles"""
    
    # Load API key
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        import subprocess
        result = subprocess.run(
            ["grep", "TAVILY_API_KEY", "../../backend/mcp-server/.env"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            api_key = result.stdout.strip().split("=")[1]
            os.environ["TAVILY_API_KEY"] = api_key
    
    client = TavilyClient(api_key=api_key)
    
    print("="*70)
    print("🔍 TESTING: Can Tavily Extract Social Media Handles?")
    print("="*70)
    print("\nTarget: Levain Bakery (known to have active Instagram)")
    print("\nQuery: Extract Instagram, Yelp, and Twitter handles\n")
    print("-"*70)
    
    # Specific query for social handles
    query = "Levain Bakery NYC Instagram handle Twitter Yelp profile social media accounts"
    
    try:
        response = client.search(
            query=query,
            search_depth="advanced",
            include_answer=True,
            include_raw_content=True,
            max_results=10
        )
        
        print("\n📝 ANSWER:")
        print(response.get("answer", "No answer provided"))
        
        print("\n\n📚 CITATIONS:")
        for i, result in enumerate(response.get("results", [])[:5], 1):
            url = result.get("url", "")
            title = result.get("title", "")
            print(f"\n{i}. {title}")
            print(f"   URL: {url}")
            
            # Check if URL contains social platforms
            if "instagram.com" in url:
                print(f"   ✅ INSTAGRAM LINK FOUND!")
            if "twitter.com" in url or "x.com" in url:
                print(f"   ✅ TWITTER/X LINK FOUND!")
            if "yelp.com" in url:
                print(f"   ✅ YELP LINK FOUND!")
        
        # Check raw content for handles
        print("\n\n🔎 SCANNING RAW CONTENT FOR HANDLES:")
        import re
        
        handles_found = {
            "instagram": set(),
            "twitter": set(),
            "yelp": set()
        }
        
        for result in response.get("results", []):
            content = result.get("content", "") + " " + result.get("url", "")
            
            # Instagram handles
            ig_matches = re.findall(r'(?:instagram\.com/|@)([a-zA-Z0-9._]+)', content)
            handles_found["instagram"].update(ig_matches)
            
            # Twitter handles
            tw_matches = re.findall(r'(?:twitter\.com/|x\.com/|@)([a-zA-Z0-9_]+)', content)
            handles_found["twitter"].update(tw_matches)
            
            # Yelp business slugs
            yelp_matches = re.findall(r'yelp\.com/biz/([a-zA-Z0-9\-]+)', content)
            handles_found["yelp"].update(yelp_matches)
        
        print(f"\nInstagram handles found: {handles_found['instagram']}")
        print(f"Twitter handles found: {handles_found['twitter']}")
        print(f"Yelp slugs found: {handles_found['yelp']}")
        
        print("\n" + "="*70)
        print("✅ TEST COMPLETE")
        print("="*70)
        
        # Summary
        has_social = any(handles_found.values())
        if has_social:
            print("\n✅ SUCCESS: Tavily CAN extract social media handles!")
            print("   Strategy: Parse URLs and content from Tavily results")
        else:
            print("\n⚠️  LIMITED: Tavily provides editorial sources, not social directly")
            print("   Alternative: Use Yelp API for structured social data")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_social_handle_extraction())
