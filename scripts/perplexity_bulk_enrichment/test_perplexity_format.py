#!/usr/bin/env python3
"""
Test Perplexity response format for best-of lists
"""

import asyncio
import httpx
import os
import json


async def test_perplexity_format():
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        import subprocess
        result = subprocess.run(
            ["grep", "PERPLEXITY_API_KEY", "../../backend/mcp-server/.env"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            api_key = result.stdout.strip().split("=")[1]
    
    prompt = """List the top 5 best pizza NYC Manhattan essential must-try iconic slices.

Format each venue as:
**Name**: [Restaurant/Bar Name]
**Address**: [Full street address]
**Known For**: [What makes it special/famous]
**Price**: [$, $$, $$$, or $$$$]

Focus on well-established, highly-rated venues."""
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "https://api.perplexity.ai/chat/completions",
            headers=headers,
            json={
                "model": "sonar",
                "messages": [{
                    "role": "system",
                    "content": "You are a NYC restaurant expert. Provide accurate, factual information."
                }, {
                    "role": "user",
                    "content": prompt
                }],
                "temperature": 0.2,
                "max_tokens": 2000,
                "return_citations": True
            }
        )
        
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        
        print("PERPLEXITY RESPONSE:")
        print("="*70)
        print(content)
        print("="*70)
        print("\nCITATIONS:")
        print(json.dumps(data["choices"][0]["message"].get("citations", []), indent=2))


if __name__ == "__main__":
    asyncio.run(test_perplexity_format())
