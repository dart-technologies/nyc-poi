/**
 * Test API Integration
 * Run this to verify the Expo app can communicate with the backend
 */

import { mcpService } from './services/mcpService';
import { config } from './config';

async function testAPIIntegration() {
    console.log('🧪 Testing API Integration...\n');
    console.log(`📡 API URL: ${config.mcp.serverUrl}\n`);

    // Test 1: Query POIs
    console.log('Test 1: Query POIs near Times Square');
    try {
        const pois = await mcpService.queryPOIs({
            location: {
                latitude: 40.7580,
                longitude: -73.9855,
            },
            radius: 3000,
            min_prestige: 50,
            limit: 3,
        });

        console.log(`✅ Found ${pois.length} POIs:`);
        pois.forEach(poi => {
            const stars = poi.prestige.michelin_stars ? `${'⭐'.repeat(poi.prestige.michelin_stars)}` : '';
            const distance = poi.distance ? `${Math.round(poi.distance)}m` : '';
            console.log(`   - ${poi.name} ${stars} ${distance}`);
        });
    } catch (error) {
        console.error('❌ Failed:', error);
    }

    console.log('\n');

    // Test 2: Get Recommendations
    console.log('Test 2: Get recommendations for date night');
    try {
        const result = await mcpService.getRecommendations({
            location: {
                latitude: 40.7580,
                longitude: -73.9855,
            },
            occasion: 'date-night',
            time_of_day: 'dinner',
            limit: 2,
        });

        console.log(`✅ ${result.explanation}`);
        console.log(`   Found ${result.pois.length} recommendations:`);
        result.pois.forEach(poi => {
            const stars = poi.prestige.michelin_stars ? `${'⭐'.repeat(poi.prestige.michelin_stars)}` : '';
            console.log(`   - ${poi.name} ${stars}`);
        });
    } catch (error) {
        console.error('❌ Failed:', error);
    }

    console.log('\n✨ API Integration Test Complete!\n');
}

// Run tests
console.log('Starting API Integration Tests...\n');
testAPIIntegration();
