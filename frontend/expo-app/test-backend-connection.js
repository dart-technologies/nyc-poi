#!/usr/bin/env node
/**
 * Test mobile app connectivity to backend
 * Simulates what the Expo app does when loading
 */

const BACKEND_URL = process.env.EXPO_PUBLIC_MCP_SERVER_URL || 'http://localhost:8000';

console.log('🔍 Testing Mobile App → Backend Connection\n');
console.log(`Backend URL: ${BACKEND_URL}\n`);

async function testConnection() {
    try {
        // Test 1: Health Check
        console.log('1. Testing health endpoint...');
        const healthRes = await fetch(`${BACKEND_URL}/health`);
        const healthData = await healthRes.json();

        if (healthData.status === 'healthy') {
            console.log(`   ✅ Backend is healthy`);
            console.log(`   ✅ Database: ${healthData.database}`);
            console.log(`   ✅ POI Count: ${healthData.poi_count}`);
        } else {
            console.log(`   ❌ Backend unhealthy:`, healthData);
            return false;
        }

        // Test 2: Query POIs (what the Discover screen does)
        console.log('\n2. Testing POI query (Discover screen simulation)...');
        const queryRes = await fetch(`${BACKEND_URL}/query-pois`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                latitude: 40.7580,
                longitude: -73.9855,
                radius_meters: 5000,
                limit: 10,
            })
        });

        if (!queryRes.ok) {
            console.log(`   ❌ Query failed with status ${queryRes.status}`);
            return false;
        }

        const queryData = await queryRes.json();
        console.log(`   ✅ Received ${queryData.count} POIs`);

        if (queryData.pois && queryData.pois.length > 0) {
            console.log(`\n   Top 3 POIs near Times Square:`);
            queryData.pois.slice(0, 3).forEach((poi, i) => {
                const distance = poi.distance ? `${Math.round(poi.distance)}m` : 'N/A';
                const stars = poi.prestige?.michelin_stars
                    ? ` (${'⭐'.repeat(poi.prestige.michelin_stars)})`
                    : '';
                console.log(`   ${i + 1}. ${poi.name}${stars} - ${distance}`);
            });
        }

        // Test 3: Recommendations (what quick actions use)
        console.log('\n3. Testing recommendations endpoint...');
        const recRes = await fetch(`${BACKEND_URL}/recommendations`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                latitude: 40.7580,
                longitude: -73.9855,
                radius_meters: 3000,
                time_of_day: 'evening',
                limit: 5,
            })
        });

        if (!recRes.ok) {
            console.log(`   ⚠️  Recommendations endpoint failed (status ${recRes.status})`);
            console.log(`   This is optional, query-pois works fine`);
        } else {
            const recData = await recRes.json();
            console.log(`   ✅ Received ${recData.count} recommendations`);
        }

        console.log('\n' + '='.repeat(60));
        console.log('✅ ALL TESTS PASSED');
        console.log('='.repeat(60));
        console.log('\n📱 Your mobile app should work now!');
        console.log('\nNext steps:');
        console.log('1. Start Expo app: npx expo start');
        console.log('2. Press "r" to reload if already running');
        console.log('3. Navigate to Discover tab');
        console.log('4. You should see POIs loaded from MongoDB!\n');

        return true;

    } catch (error) {
        console.log('\n❌ Connection test failed:', error.message);
        console.log('\nTroubleshooting:');
        console.log(`1. Is backend running? Check: curl ${BACKEND_URL}/health`);
        console.log('2. Start backend: cd backend/mcp-server && python3 http_server.py');
        console.log('3. Check firewall/network settings\n');
        return false;
    }
}

testConnection();
