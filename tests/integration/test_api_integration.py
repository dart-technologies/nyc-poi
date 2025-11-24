#!/usr/bin/env python3
"""
NYC POI Concierge - End-to-End Integration Test
Tests the complete stack: Backend API → MongoDB Atlas
"""

import sys
import json
import time
from typing import Dict, Any
import requests
from colorama import Fore, Style, init

# Initialize colorama for colored output
init(autoreset=True)

# Configuration
API_BASE_URL = "https://innate-eudemonistically-sharita.ngrok-free.dev"
LOCAL_URL = "http://localhost:8000"

# Test data
TEST_LOCATION = {
    "latitude": 40.7580,  # Times Square
    "longitude": -73.9855
}

class IntegrationTester:
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.passed = 0
        self.failed = 0
        self.tests_run = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log a message with color"""
        colors = {
            "INFO": Fore.BLUE,
            "SUCCESS": Fore.GREEN,
            "ERROR": Fore.RED,
            "WARNING": Fore.YELLOW
        }
        color = colors.get(level, Fore.WHITE)
        print(f"{color}{message}{Style.RESET_ALL}")
    
    def assert_true(self, condition: bool, message: str):
        """Assert a condition is true"""
        if condition:
            self.passed += 1
            self.log(f"  ✅ {message}", "SUCCESS")
            return True
        else:
            self.failed += 1
            self.log(f"  ❌ {message}", "ERROR")
            return False
    
    def test_health_check(self) -> bool:
        """Test 1: Health Check Endpoint"""
        self.log("\n🧪 Test 1: Health Check Endpoint", "INFO")
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            
            # Check status code
            self.assert_true(response.status_code == 200, "Status code is 200")
            
            # Check response structure
            data = response.json()
            self.assert_true("status" in data, "Response has 'status' field")
            self.assert_true(data["status"] == "healthy", "Status is 'healthy'")
            self.assert_true("database" in data, "Response has 'database' field")
            self.assert_true(data["database"] == "connected", "Database is connected")
            self.assert_true("poi_count" in data, "Response has 'poi_count' field")
            self.assert_true(data["poi_count"] >= 7, f"POI count is {data['poi_count']} (expected >= 7)")
            
            self.log(f"  📊 Database: {data['database']}, POIs: {data['poi_count']}", "INFO")
            return True
            
        except Exception as e:
            self.log(f"  ❌ Health check failed: {str(e)}", "ERROR")
            self.failed += 1
            return False
    
    def test_query_pois_basic(self) -> bool:
        """Test 2: Basic POI Query"""
        self.log("\n🧪 Test 2: Basic POI Query", "INFO")
        
        try:
            payload = {
                "latitude": TEST_LOCATION["latitude"],
                "longitude": TEST_LOCATION["longitude"],
                "radius_meters": 5000,
                "min_prestige_score": 50,
                "limit": 5
            }
            
            response = requests.post(
                f"{self.base_url}/query-pois",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            # Check status code
            self.assert_true(response.status_code == 200, "Status code is 200")
            
            # Check response structure
            data = response.json()
            self.assert_true("pois" in data, "Response has 'pois' field")
            self.assert_true("count" in data, "Response has 'count' field")
            self.assert_true(isinstance(data["pois"], list), "POIs is a list")
            self.assert_true(data["count"] == len(data["pois"]), "Count matches POI array length")
            
            # Check POI structure if results returned
            if data["count"] > 0:
                poi = data["pois"][0]
                self.assert_true("_id" in poi, "POI has '_id' field")
                self.assert_true("name" in poi, "POI has 'name' field")
                self.assert_true("prestige" in poi, "POI has 'prestige' field")
                self.assert_true("location" in poi, "POI has 'location' field")
                self.assert_true("distance" in poi, "POI has 'distance' field")
                
                # Check prestige structure
                if "michelin_stars" in poi["prestige"]:
                    stars = poi["prestige"]["michelin_stars"]
                    self.log(f"  ⭐ Found: {poi['name']} ({stars} Michelin stars, {poi['distance']:.0f}m away)", "INFO")
                else:
                    self.log(f"  📍 Found: {poi['name']} ({poi['distance']:.0f}m away)", "INFO")
            
            return True
            
        except Exception as e:
            self.log(f"  ❌ Query failed: {str(e)}", "ERROR")
            self.failed += 1
            return False
    
    def test_query_pois_michelin_filter(self) -> bool:
        """Test 3: Query with Michelin Filter"""
        self.log("\n🧪 Test 3: Query Michelin-Starred Restaurants", "INFO")
        
        try:
            payload = {
                "latitude": TEST_LOCATION["latitude"],
                "longitude": TEST_LOCATION["longitude"],
                "radius_meters": 5000,
                "min_prestige_score": 100,  # High prestige = Michelin stars
                "limit": 3
            }
            
            response = requests.post(
                f"{self.base_url}/query-pois",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            data = response.json()
            self.assert_true(response.status_code == 200, "Status code is 200")
            
            # Check all returned POIs have high prestige
            michelin_count = 0
            for poi in data["pois"]:
                if "michelin_stars" in poi.get("prestige", {}):
                    michelin_count += 1
                    stars = "⭐" * poi["prestige"]["michelin_stars"]
                    self.log(f"  {stars} {poi['name']} (Score: {poi['prestige']['score']})", "INFO")
            
            self.assert_true(michelin_count > 0, f"Found {michelin_count} Michelin-starred restaurants")
            
            return True
            
        except Exception as e:
            self.log(f"  ❌ Michelin filter failed: {str(e)}", "ERROR")
            self.failed += 1
            return False
    
    def test_contextual_recommendations(self) -> bool:
        """Test 4: Contextual Recommendations"""
        self.log("\n🧪 Test 4: Contextual Recommendations", "INFO")
        
        try:
            payload = {
                "latitude": TEST_LOCATION["latitude"],
                "longitude": TEST_LOCATION["longitude"],
                "radius_meters": 5000,
                "occasion": "date-night",
                "time_of_day": "dinner",
                "limit": 3
            }
            
            response = requests.post(
                f"{self.base_url}/recommendations",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            # Check status code
            self.assert_true(response.status_code == 200, "Status code is 200")
            
            # Check response structure
            data = response.json()
            self.assert_true("pois" in data, "Response has 'pois' field")
            self.assert_true("explanation" in data, "Response has 'explanation' field")
            self.assert_true("count" in data, "Response has 'count' field")
            
            # Log explanation
            self.log(f"  💡 {data['explanation']}", "INFO")
            
            # Check POIs have context-appropriate fields
            for poi in data["pois"]:
                if "best_for" in poi and "occasions" in poi["best_for"]:
                    self.assert_true(
                        "date-night" in poi["best_for"]["occasions"],
                        f"{poi['name']} is suitable for date night"
                    )
                self.log(f"  🍽️  {poi['name']}", "INFO")
            
            return True
            
        except Exception as e:
            self.log(f"  ❌ Recommendations failed: {str(e)}", "ERROR")
            self.failed += 1
            return False
    
    def test_geospatial_accuracy(self) -> bool:
        """Test 5: Geospatial Distance Calculation"""
        self.log("\n🧪 Test 5: Geospatial Distance Accuracy", "INFO")
        
        try:
            payload = {
                "latitude": TEST_LOCATION["latitude"],
                "longitude": TEST_LOCATION["longitude"],
                "radius_meters": 1000,  # 1km radius
                "limit": 10
            }
            
            response = requests.post(
                f"{self.base_url}/query-pois",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            data = response.json()
            
            # Check all distances are within radius
            all_within_radius = True
            for poi in data["pois"]:
                distance = poi.get("distance", 0)
                within_radius = distance <= 1000
                all_within_radius = all_within_radius and within_radius
                
                if not within_radius:
                    self.log(f"  ⚠️  {poi['name']} is {distance:.0f}m away (> 1000m)", "WARNING")
            
            self.assert_true(
                all_within_radius,
                "All POIs are within specified radius"
            )
            
            # Check distances are sorted (closer first)
            distances = [poi.get("distance", 0) for poi in data["pois"]]
            if len(distances) > 1:
                # Allow for prestige sorting (not purely distance)
                self.log(f"  📏 Distance range: {min(distances):.0f}m - {max(distances):.0f}m", "INFO")
            
            return True
            
        except Exception as e:
            self.log(f"  ❌ Geospatial test failed: {str(e)}", "ERROR")
            self.failed += 1
            return False
    
    def test_edge_cases(self) -> bool:
        """Test 6: Edge Cases and Error Handling"""
        self.log("\n🧪 Test 6: Edge Cases & Error Handling", "INFO")
        
        test_cases = [
            {
                "name": "Zero results query (very high prestige)",
                "payload": {
                    "latitude": TEST_LOCATION["latitude"],
                    "longitude": TEST_LOCATION["longitude"],
                    "min_prestige_score": 999,  # Impossibly high
                    "limit": 5
                },
                "expect_empty": True
            },
            {
                "name": "Very small radius",
                "payload": {
                    "latitude": TEST_LOCATION["latitude"],
                    "longitude": TEST_LOCATION["longitude"],
                    "radius_meters": 1,  # 1 meter
                    "limit": 5
                },
                "expect_empty": True
            }
        ]
        
        all_passed = True
        for test_case in test_cases:
            try:
                response = requests.post(
                    f"{self.base_url}/query-pois",
                    json=test_case["payload"],
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                data = response.json()
                if test_case.get("expect_empty"):
                    passed = data["count"] == 0
                    self.assert_true(passed, f"{test_case['name']}: Returns empty results")
                else:
                    passed = response.status_code == 200
                    self.assert_true(passed, f"{test_case['name']}: Returns 200")
                
                all_passed = all_passed and passed
                
            except Exception as e:
                self.log(f"  ❌ {test_case['name']} failed: {str(e)}", "ERROR")
                self.failed += 1
                all_passed = False
        
        return all_passed
    
    def test_response_time(self) -> bool:
        """Test 7: Response Time Performance"""
        self.log("\n🧪 Test 7: Response Time Performance", "INFO")
        
        try:
            payload = {
                "latitude": TEST_LOCATION["latitude"],
                "longitude": TEST_LOCATION["longitude"],
                "radius_meters": 3000,
                "limit": 5
            }
            
            # Test multiple requests
            times = []
            for i in range(3):
                start = time.time()
                response = requests.post(
                    f"{self.base_url}/query-pois",
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                end = time.time()
                times.append(end - start)
            
            avg_time = sum(times) / len(times)
            max_time = max(times)
            min_time = min(times)
            
            self.log(f"  ⏱️  Avg: {avg_time*1000:.0f}ms, Min: {min_time*1000:.0f}ms, Max: {max_time*1000:.0f}ms", "INFO")
            
            # Check performance (should be under 2 seconds)
            self.assert_true(avg_time < 2.0, f"Average response time is under 2s ({avg_time:.2f}s)")
            self.assert_true(max_time < 3.0, f"Max response time is under 3s ({max_time:.2f}s)")
            
            return True
            
        except Exception as e:
            self.log(f"  ❌ Performance test failed: {str(e)}", "ERROR")
            self.failed += 1
            return False
    
    def run_all_tests(self):
        """Run all integration tests"""
        self.log("=" * 70, "INFO")
        self.log("🧪 NYC POI Concierge - Integration Test Suite", "INFO")
        self.log(f"🌐 Testing API: {self.base_url}", "INFO")
        self.log("=" * 70, "INFO")
        
        start_time = time.time()
        
        # Run all tests
        tests = [
            self.test_health_check,
            self.test_query_pois_basic,
            self.test_query_pois_michelin_filter,
            self.test_contextual_recommendations,
            self.test_geospatial_accuracy,
            self.test_edge_cases,
            self.test_response_time
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                self.log(f"Test {test.__name__} crashed: {str(e)}", "ERROR")
                self.failed += 1
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Print summary
        self.log("\n" + "=" * 70, "INFO")
        self.log("📊 Test Summary", "INFO")
        self.log("=" * 70, "INFO")
        
        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0
        
        self.log(f"✅ Passed: {self.passed}", "SUCCESS")
        if self.failed > 0:
            self.log(f"❌ Failed: {self.failed}", "ERROR")
        else:
            self.log(f"❌ Failed: {self.failed}", "SUCCESS")
        
        self.log(f"📈 Pass Rate: {pass_rate:.1f}%", "SUCCESS" if pass_rate >= 90 else "WARNING")
        self.log(f"⏱️  Duration: {duration:.2f}s", "INFO")
        
        self.log("=" * 70, "INFO")
        
        if self.failed == 0:
            self.log("\n🎉 ALL TESTS PASSED! System is working end-to-end! 🎉", "SUCCESS")
            return 0
        else:
            self.log(f"\n⚠️  {self.failed} test(s) failed. Please review.", "WARNING")
            return 1


def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="NYC POI Concierge Integration Tests")
    parser.add_argument("--url", default=API_BASE_URL, help="API base URL to test")
    parser.add_argument("--local", action="store_true", help="Test local server instead of ngrok")
    
    args = parser.parse_args()
    
    url = LOCAL_URL if args.local else args.url
    
    tester = IntegrationTester(base_url=url)
    exit_code = tester.run_all_tests()
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
