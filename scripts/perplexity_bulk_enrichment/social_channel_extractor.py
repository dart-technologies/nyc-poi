"""
Social Channel Extractor for POIs
Extracts Instagram, Yelp, Google Maps, X (Twitter), Foursquare links
"""

import re
from typing import Dict, List, Optional
from urllib.parse import urlparse


class SocialChannelExtractor:
    """Extract social media and review platform links from URLs and content"""
    
    # Platform URL patterns
    PLATFORM_PATTERNS = {
        "instagram": [
            r'instagram\.com/([a-zA-Z0-9._]+)',
            r'@([a-zA-Z0-9._]+)',  # Handle @mentions in content
        ],
        "yelp": [
            r'yelp\.com/biz/([a-zA-Z0-9\-]+)',
        ],
        "google_maps": [
            r'google\.com/maps/place/([^/]+)',
            r'maps\.app\.goo\.gl/([a-zA-Z0-9]+)',
        ],
        "twitter": [
            r'twitter\.com/([a-zA-Z0-9_]+)',
            r'x\.com/([a-zA-Z0-9_]+)',
        ],
        "foursquare": [
            r'foursquare\.com/v/([a-zA-Z0-9\-]+)',
        ],
        "opentable": [
            r'opentable\.com/([a-zA-Z0-9\-]+)',
        ],
        "resy": [
            r'resy\.com/cities/[^/]+/([a-zA-Z0-9\-]+)',
        ]
    }
    
    @classmethod
    def extract_from_citations(cls, citations: List[Dict]) -> Dict[str, str]:
        """Extract social channels from citation URLs"""
        
        social_links = {}
        
        for citation in citations:
            url = citation.get("url", "")
            
            for platform, patterns in cls.PLATFORM_PATTERNS.items():
                if platform in social_links:
                    continue  # Already found
                
                for pattern in patterns:
                    match = re.search(pattern, url, re.IGNORECASE)
                    if match:
                        social_links[platform] = url
                        break
        
        return social_links
    
    @classmethod
    def extract_from_content(cls, content: str) -> Dict[str, str]:
        """Extract social handles from content text"""
        
        handles = {}
        
        # Instagram handles
        instagram_matches = re.findall(r'@([a-zA-Z0-9._]+)', content)
        if instagram_matches:
            # Take the first one (most likely the restaurant's handle)
            handles["instagram_handle"] = instagram_matches[0]
        
        # Look for explicit URLs in content
        url_matches = re.findall(r'https?://[^\s]+', content)
        for url in url_matches:
            for platform, patterns in cls.PLATFORM_PATTERNS.items():
                if platform in handles:
                    continue
                
                for pattern in patterns:
                    if re.search(pattern, url, re.IGNORECASE):
                        handles[platform] = url
                        break
        
        return handles
    
    @classmethod
    def build_social_object(cls, citations: List[Dict], content: str = "") -> Dict[str, str]:
        """Build complete social media object for POI"""
        
        social = {}
        
        # Extract from citations (most reliable)
        citation_links = cls.extract_from_citations(citations)
        social.update(citation_links)
        
        # Extract from content (handles and mentions)
        if content:
            content_links = cls.extract_from_content(content)
            # Only add if not already found in citations
            for key, value in content_links.items():
                if key not in social:
                    social[key] = value
        
        return social


# Helper function to enrich existing POI with social channels
def enrich_poi_with_social(poi: Dict) -> Dict:
    """Add social channels to existing POI document"""
    
    # Get citations from sources
    citations = []
    for source in poi.get("sources", []):
        if source.get("citations"):
            citations.extend(source["citations"])
        elif source.get("url"):
            citations.append({"url": source["url"]})
    
    # Extract content for text analysis
    content = ""
    if poi.get("experience", {}).get("signature_dishes"):
        content += " ".join(poi["experience"]["signature_dishes"])
    
    # Extract social channels
    social = SocialChannelExtractor.build_social_object(citations, content)
    
    # Add to POI
    if "contact" not in poi:
        poi["contact"] = {}
    
    poi["contact"]["social"] = social
    
    return poi


# Example usage
if __name__ == "__main__":
    # Test with sample data
    test_citations = [
        {"url": "https://www.instagram.com/lebernardanny"},
        {"url": "https://www.yelp.com/biz/le-bernardin-new-york"},
        {"url": "https://guide.michelin.com/us/en/new-york-state/new-york/restaurant/le-bernardin"}
    ]
    
    test_content = "Follow @lebernardanny on Instagram for daily specials"
    
    social = SocialChannelExtractor.build_social_object(test_citations, test_content)
    
    print("Extracted Social Channels:")
    for platform, link in social.items():
        print(f"  {platform}: {link}")
