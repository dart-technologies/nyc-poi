/**
 * MCP Client Service
 * Integrates with LastMile AI MCP Server for POI queries and recommendations
 */

import { config } from '../config';
import { Coordinates } from './locationService';
import OpenAI from 'openai';

export interface POI {
    _id: string;
    name: string;
    category: string;
    subcategories: string[];
    location: {
        type: string;
        coordinates: [number, number];
    };
    address: {
        street: string;
        city: string;
        state: string;
        zip: string;
        neighborhood: string;
        borough: string;
    };
    prestige: {
        score: number;
        michelin_stars?: number;
        michelin_since?: number;
        michelin_bib_gourmand?: boolean;
        james_beard_awards?: string[];
        nyt_stars?: number;
        best_of_lists?: Array<{
            source: string;
            list: string;
            rank?: number;
            year: number;
        }>;
    };
    contact: {
        phone?: string;
        website?: string;
        reservations_url?: string;
    };
    experience: {
        price_range: string;
        avg_meal_cost?: number;
        dress_code?: string;
        reservation_difficulty?: string;
        signature_dishes?: string[];
        ambiance?: string[];
    };
    best_for?: {
        occasions?: string[];
        time_of_day?: string[];
        weather?: string[];
    };
    media?: {
        logo_url?: string;
        hero_image_url?: string;
    };
    branding?: {
        primary_color?: string;
        accent_color?: string;
    };
    distance?: number; // Added by client
    distance_formatted?: string; // Added by client
}

export interface ChatMessage {
    role: 'user' | 'assistant' | 'system';
    content: string;
    timestamp: number;
    pois?: POI[]; // Attached POIs for display
}

class MCPService {
    private openai: OpenAI;
    private conversationHistory: ChatMessage[] = [];

    constructor() {
        this.openai = new OpenAI({
            apiKey: config.openai.apiKey,
            dangerouslyAllowBrowser: true, // Required for Expo
        });
    }

    /**
     * Query POIs directly (bypass chat)
     */
    async queryPOIs(params: {
        location: Coordinates;
        radius?: number;
        category?: string;
        subcategory?: string;
        min_prestige?: number;
        limit?: number;
        time_of_day?: string;
    }): Promise<POI[]> {
        const requestUrl = `${config.mcp.serverUrl}/query-pois`;
        const requestBody = {
            latitude: params.location.latitude,
            longitude: params.location.longitude,
            radius_meters: params.radius || config.map.defaultRadius,
            category: params.category,
            subcategory: params.subcategory,
            min_prestige_score: params.min_prestige,
            limit: params.limit || 10,
            time_of_day: params.time_of_day,
        };

        // console.log('🔵 [MCP Service] queryPOIs called');
        // console.log('   URL:', requestUrl);
        // console.log('   Server URL from config:', config.mcp.serverUrl);
        // console.log('   Request body:', JSON.stringify(requestBody, null, 2));
        // console.log('   Timestamp:', new Date().toISOString());

        try {
            // console.log('   📡 Making fetch request...');
            const startTime = Date.now();

            const response = await fetch(requestUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody),
            });

            // const duration = Date.now() - startTime;
            // console.log(`   ⏱️  Response received in ${duration}ms`);
            // console.log('   Status:', response.status, response.statusText);

            if (!response.ok) {
                console.error('   ❌ Response not OK:', response.status);
                const errorText = await response.text();
                console.error('   Error body:', errorText);
                throw new Error(`MCP server error: ${response.status}`);
            }

            // console.log('   📥 Parsing JSON response...');
            const data = await response.json();
            // console.log('   ✅ Response parsed successfully');
            // console.log('   POI count:', data.pois?.length || 0);

            // if (data.pois && data.pois.length > 0) {
            //     console.log('   First POI:', data.pois[0].name);
            // }

            return data.pois || [];
        } catch (error) {
            const err = error as Error;
            console.error('❌ [MCP Service] queryPOIs ERROR:');
            console.error('   Error type:', err.constructor.name);
            console.error('   Error message:', err.message);
            console.error('   Full error:', err);
            console.error('   Stack:', err.stack);
            console.log('   📦 Falling back to mock POI data for demo');

            // Return mock data for demo
            return this.getMockPOIs(params);
        }
    }

    /**
     * Get mock POI data for demo purposes
     */
    private getMockPOIs(params: {
        category?: string;
        min_prestige?: number;
        time_of_day?: string;
    }): POI[] {
        const mockPOIs: POI[] = [
            {
                _id: '1',
                name: 'Le Bernardin',
                category: 'fine-dining',
                subcategories: ['french', 'seafood'],
                location: {
                    type: 'Point',
                    coordinates: [-73.9826, 40.7614],
                },
                address: {
                    street: '155 W 51st St',
                    city: 'New York',
                    state: 'NY',
                    zip: '10019',
                    neighborhood: 'Midtown West',
                    borough: 'Manhattan',
                },
                prestige: {
                    score: 150,
                    michelin_stars: 3,
                    michelin_since: 2005,
                    james_beard_awards: ['Outstanding Restaurant 2018'],
                    nyt_stars: 4,
                },
                contact: {
                    phone: '(212) 554-1515',
                    website: 'https://www.le-bernardin.com',
                    reservations_url: 'https://www.le-bernardin.com/reservations',
                },
                experience: {
                    price_range: '$$$$',
                    avg_meal_cost: 200,
                    dress_code: 'Business Casual',
                    reservation_difficulty: 'very-high',
                    signature_dishes: ['Tuna Ribbons', 'Black Bass', 'Lobster'],
                    ambiance: ['elegant', 'romantic', 'upscale'],
                },
                best_for: {
                    occasions: ['date-night', 'business-dinner', 'special-occasion'],
                    time_of_day: ['lunch', 'dinner'],
                    weather: ['any'],
                },
                media: {
                    logo_url: 'https://upload.wikimedia.org/wikipedia/en/b/be/Le_Bernardin_logo.png',
                },
            },
            {
                _id: '2',
                name: 'Eleven Madison Park',
                category: 'fine-dining',
                subcategories: ['contemporary', 'american'],
                location: {
                    type: 'Point',
                    coordinates: [-73.9874, 40.7423],
                },
                address: {
                    street: '11 Madison Ave',
                    city: 'New York',
                    state: 'NY',
                    zip: '10010',
                    neighborhood: 'Flatiron',
                    borough: 'Manhattan',
                },
                prestige: {
                    score: 150,
                    michelin_stars: 3,
                    michelin_since: 2012,
                    james_beard_awards: ['Outstanding Restaurant 2017'],
                    best_of_lists: [{
                        source: "World's 50 Best",
                        list: "World's 50 Best Restaurants",
                        rank: 1,
                        year: 2017,
                    }],
                },
                contact: {
                    phone: '(212) 889-0905',
                    website: 'https://www.elevenmadisonpark.com',
                    reservations_url: 'https://www.elevenmadisonpark.com/reservations',
                },
                experience: {
                    price_range: '$$$$',
                    avg_meal_cost: 335,
                    dress_code: 'Jacket Required',
                    reservation_difficulty: 'very-high',
                    signature_dishes: ['Plant-based tasting menu'],
                    ambiance: ['artistic', 'innovative', 'refined'],
                },
                best_for: {
                    occasions: ['special-occasion', 'celebration'],
                    time_of_day: ['dinner'],
                    weather: ['any'],
                },
                media: {
                    logo_url: 'https://upload.wikimedia.org/wikipedia/en/a/a0/Eleven_Madison_Park_logo.png',
                },
            },
            {
                _id: '3',
                name: 'Gramercy Tavern',
                category: 'fine-dining',
                subcategories: ['american', 'contemporary'],
                location: {
                    type: 'Point',
                    coordinates: [-73.9889, 40.7380],
                },
                address: {
                    street: '42 E 20th St',
                    city: 'New York',
                    state: 'NY',
                    zip: '10003',
                    neighborhood: 'Gramercy',
                    borough: 'Manhattan',
                },
                prestige: {
                    score: 80,
                    michelin_stars: 1,
                    michelin_since: 2006,
                    james_beard_awards: ['Outstanding Restaurant 2008'],
                    nyt_stars: 3,
                },
                contact: {
                    phone: '(212) 477-0777',
                    website: 'https://www.gramercytavern.com',
                },
                experience: {
                    price_range: '$$$',
                    avg_meal_cost: 125,
                    dress_code: 'Smart Casual',
                    reservation_difficulty: 'moderate',
                    signature_dishes: ['Roasted Duck', 'Seasonal Tasting Menu'],
                    ambiance: ['warm', 'tavern-style', 'seasonal'],
                },
                best_for: {
                    occasions: ['date-night', 'dinner-with-friends'],
                    time_of_day: ['lunch', 'dinner'],
                    weather: ['any'],
                },
                media: {
                    logo_url: 'https://upload.wikimedia.org/wikipedia/en/4/4b/Gramercy_Tavern_logo.png',
                },
            },
            {
                _id: '4',
                name: "Joe's Pizza",
                category: 'casual-dining',
                subcategories: ['pizza', 'italian'],
                location: {
                    type: 'Point',
                    coordinates: [-74.0021, 40.7303],
                },
                address: {
                    street: '7 Carmine St',
                    city: 'New York',
                    state: 'NY',
                    zip: '10014',
                    neighborhood: 'Greenwich Village',
                    borough: 'Manhattan',
                },
                prestige: {
                    score: 25,
                    best_of_lists: [{
                        source: 'Eater NY',
                        list: 'Best Pizza NYC',
                        year: 2024,
                    }],
                },
                contact: {
                    phone: '(212) 366-1182',
                    website: 'https://www.joespizzanyc.com',
                },
                experience: {
                    price_range: '$',
                    avg_meal_cost: 12,
                    dress_code: 'Casual',
                    reservation_difficulty: 'none',
                    signature_dishes: ['Classic New York Slice', 'Margherita Pizza'],
                    ambiance: ['casual', 'quick', 'authentic'],
                },
                best_for: {
                    occasions: ['casual', 'lunch', 'late-night'],
                    time_of_day: ['lunch', 'dinner', 'late-night'],
                    weather: ['any'],
                },
                media: {
                    logo_url: 'https://upload.wikimedia.org/wikipedia/en/0/07/Joe%27s_Pizza_logo.png',
                },
            },
        ];

        // Filter based on parameters
        let filtered = mockPOIs;

        if (params.category) {
            filtered = filtered.filter(poi => poi.category === params.category);
        }

        if (params.min_prestige !== undefined) {
            filtered = filtered.filter(poi => poi.prestige.score >= params.min_prestige!);
        }

        if (params.time_of_day) {
            filtered = filtered.filter(poi => {
                const windows = poi.best_for?.time_of_day;
                if (!windows || windows.length === 0) {
                    return true;
                }
                return windows.includes(params.time_of_day!) || windows.includes('any');
            });
        }

        return filtered;
    }

    /**
     * Get contextual recommendations (bypass chat)
     */
    async getRecommendations(params: {
        location: Coordinates;
        occasion?: string;
        weather_condition?: string;
        time_of_day?: string;
        limit?: number;
    }): Promise<{ pois: POI[]; explanation: string }> {
        // console.log('🔵 [MCP Service] getRecommendations called');
        // console.log('   Location:', params.location);
        // console.log('   Occasion:', params.occasion);
        // console.log('   Weather:', params.weather_condition);
        // console.log('   Time of day:', params.time_of_day);

        try {
            const response = await fetch(`${config.mcp.serverUrl}/recommendations`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    latitude: params.location.latitude,
                    longitude: params.location.longitude,
                    occasion: params.occasion,
                    weather_condition: params.weather_condition,
                    time_of_day: params.time_of_day,
                    limit: params.limit || 5,
                }),
            });

            console.log('   Status:', response.status);

            if (!response.ok) {
                const errorText = await response.text();
                console.error('   Error response:', errorText);
                throw new Error(`MCP server error: ${response.status}`);
            }

            const data = await response.json();
            // console.log('   POIs received:', data.pois?.length || 0);
            // console.log('   Explanation:', data.explanation);

            return {
                pois: data.pois || [],
                explanation: data.explanation || 'Here are my top recommendations for you.',
            };
        } catch (error) {
            console.error('❌ Error getting recommendations:', error);
            return {
                pois: [],
                explanation: 'Sorry, I encountered an error getting recommendations.',
            };
        }
    }

    /**
     * Chat with GPT-4o-mini (with MCP tool calling)
     */
    async chat(userMessage: string, context?: {
        location?: Coordinates;
        weather?: string;
        timeOfDay?: string;
    }): Promise<ChatMessage> {
        // Add user message to history
        const userMsg: ChatMessage = {
            role: 'user',
            content: userMessage,
            timestamp: Date.now(),
        };
        this.conversationHistory.push(userMsg);

        try {
            // Build system message with context
            let systemMessage = 'You are a knowledgeable NYC restaurant concierge assistant. You help users discover amazing restaurants, especially those with Michelin stars and prestigious awards. Be conversational, enthusiastic, and helpful.';

            if (context?.location) {
                systemMessage += `\n\nUser's current location: ${context.location.latitude}, ${context.location.longitude}`;
            }
            if (context?.weather) {
                systemMessage += `\n\nCurrent weather: ${context.weather}`;
            }
            if (context?.timeOfDay) {
                systemMessage += `\n\nTime of day: ${context.timeOfDay}`;
            }

            // Call OpenAI
            const completion = await this.openai.chat.completions.create({
                model: config.openai.model,
                messages: [
                    { role: 'system', content: systemMessage },
                    ...this.conversationHistory.slice(-10).map(msg => ({
                        role: msg.role,
                        content: msg.content,
                    })),
                ],
                temperature: 0.7,
                max_tokens: 500,
            });

            const assistantContent = completion.choices[0]?.message?.content || 'Sorry, I could not generate a response.';

            const assistantMsg: ChatMessage = {
                role: 'assistant',
                content: assistantContent,
                timestamp: Date.now(),
            };

            this.conversationHistory.push(assistantMsg);
            return assistantMsg;
        } catch (error) {
            console.error('Error in chat:', error);
            const errorMsg: ChatMessage = {
                role: 'assistant',
                content: 'Sorry, I encountered an error. Please try again.',
                timestamp: Date.now(),
            };
            this.conversationHistory.push(errorMsg);
            return errorMsg;
        }
    }

    /**
     * Get conversation history
     */
    getHistory(): ChatMessage[] {
        return this.conversationHistory;
    }

    /**
     * Clear conversation history
     */
    clearHistory(): void {
        this.conversationHistory = [];
    }

    /**
     * Check POI data freshness
     */
    async checkPOIFreshness(poiId: string): Promise<{
        updated_at: string | null;
        age_hours: number | null;
        is_fresh: boolean;
    }> {
        try {
            const response = await fetch(`${config.mcp.serverUrl}/poi/${poiId}/freshness`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Error checking POI freshness:', error);
            return { updated_at: null, age_hours: null, is_fresh: false };
        }
    }

    /**
 * Refresh POI data with latest from web
 */
    async refreshPOI(poiId: string, force: boolean = false): Promise<POI | null> {
        try {
            // console.log(`🔄 [MCP Service] Refreshing POI ${poiId}, force=${force}`);
            const response = await fetch(
                `${config.mcp.serverUrl}/poi/${poiId}/refresh?force=${force}`,
                { method: 'POST' }
            );

            console.log('   Status:', response.status);

            if (!response.ok) {
                const errorText = await response.text();
                console.error('   Error:', errorText);
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();
            // console.log('   Response:', data);
            // console.log('   Has enrichment_data:', !!data.enrichment_data);

            // Merge enrichment_data into POI object for frontend access
            if (data.enrichment_data) {
                data.poi.enrichment_data = data.enrichment_data;
            }

            return data.poi;
        } catch (error) {
            console.error('❌ Error refreshing POI:', error);
            return null;
        }
    }
}

export const mcpService = new MCPService();
