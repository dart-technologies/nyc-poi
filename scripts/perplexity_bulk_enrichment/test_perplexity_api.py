#!/usr/bin/env python3
"""Test Perplexity Sonar API connection"""

import os
import asyncio
import httpx
import sys

async def test_perplexity():
    api_key = os.getenv("PERPLEXITY_API_KEY")
    
    if not api_key:
        print("❌ PERPLEXITY_API_KEY not found in environment")
        sys.exit(1)
    
    print(f"✅ API Key found: {api_key[:10]}...")
    print("\n🔍 Testing Perplexity Sonar API...")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print("   Sending test request...")
            response = await client.post(
                "https://api.perplexity.ai/chat/completions",
                headers=headers,
                json={
                    "model": "sonar",
                    "messages": [
                        {
                            "role": "user",
                            "content": "What is Le Bernardin restaurant in NYC known for? Give a very brief answer."
                        }
                    ],
                    "temperature": 0.2,
                    "max_tokens": 100,
                    "return_citations": True
                }
            )
            
            print(f"   Status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                print(f"\n✅ SUCCESS! Response:\n{content}\n")
                return True
            else:
                print(f"\n❌ ERROR: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_perplexity())
    sys.exit(0 if result else 1)
