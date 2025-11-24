// NYC POI Concierge - API Configuration
// Generated: 2025-11-23 08:06 EST

export const API_CONFIG = {
    // ngrok Public URL (local development with public access)
    baseURL: 'https://innate-eudemonistically-sharita.ngrok-free.dev',

    // API Endpoints
    endpoints: {
        health: '/health',
        queryPOIs: '/query-pois',
        recommendations: '/recommendations',
    },

    // Default request timeout (ms)
    timeout: 10000,
};

// Example Usage:
// import { API_CONFIG } from './config/api';
// 
// const response = await fetch(`${API_CONFIG.baseURL}${API_CONFIG.endpoints.queryPOIs}`, {
//   method: 'POST',
//   headers: { 'Content-Type': 'application/json' },
//   body: JSON.stringify({
//     latitude: 40.7580,
//     longitude: -73.9855,
//     radius_meters: 2000,
//     min_prestige_score: 50,
//     limit: 5
//   })
// });

// Type definitions for API requests/responses
export interface QueryPOIsRequest {
    latitude: number;
    longitude: number;
    radius_meters?: number;
    category?: string;
    min_prestige_score?: number;
    limit?: number;
}

export interface ContextualRecommendationsRequest {
    latitude: number;
    longitude: number;
    radius_meters?: number;
    occasion?: string;
    weather_condition?: string;
    time_of_day?: string;
    limit?: number;
}

export interface POI {
    _id: string;
    name: string;
    slug: string;
    category: string;
    subcategories: string[];
    location: {
        type: 'Point';
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
        james_beard_awards?: string[];
        nyt_stars?: number;
        best_of_lists?: any[];
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
        ambiance?: string[];
        signature_dishes?: string[];
    };
    best_for?: {
        occasions?: string[];
        time_of_day?: string[];
        weather?: string[];
    };
    distance?: number;
    relevance_score?: number;
}

export interface QueryPOIsResponse {
    pois: POI[];
    count: number;
}

export interface RecommendationsResponse {
    pois: POI[];
    explanation: string;
    count: number;
}
