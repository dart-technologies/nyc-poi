/**
 * Configuration for NYC POI Concierge
 */

export const config = {
    openai: {
        apiKey: process.env.EXPO_PUBLIC_OPENAI_API_KEY || '',
        model: 'gpt-4o-mini',
    },
    weather: {
        apiKey: process.env.EXPO_PUBLIC_OPENWEATHER_API_KEY || '',
        baseUrl: 'https://api.openweathermap.org/data/2.5',
        units: 'imperial', // Fahrenheit for NYC
    },
    mcp: {
        serverUrl: process.env.EXPO_PUBLIC_MCP_SERVER_URL || 'http://localhost:8000',
    },
    map: {
        defaultCenter: {
            latitude: 40.7580,
            longitude: -73.9855,
        },
        defaultRadius: 2000, // 2km in meters
    },
    debug: process.env.EXPO_PUBLIC_DEBUG_MODE === 'true',
};
