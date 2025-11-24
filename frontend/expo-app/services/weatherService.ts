/**
 * Weather Service
 * Integrates with OpenWeatherMap API
 */

import { config } from '../config';
import { Coordinates } from './locationService';

export interface WeatherData {
    temperature: number; // Fahrenheit
    feelsLike: number;
    condition: string; // e.g., "Clear", "Rain", "Clouds"
    description: string; // e.g., "clear sky", "light rain"
    humidity: number; // percentage
    windSpeed: number; // mph
    icon: string; // weather icon code
    timestamp: number;
}

export interface WeatherContext {
    isCold: boolean; // < 50°F
    isHot: boolean; // > 80°F
    isRaining: boolean;
    isNice: boolean; // 60-75°F, clear/partly cloudy
    recommendation: string; // e.g., "Perfect weather for outdoor dining"
}

class WeatherService {
    private cache: Map<string, { data: WeatherData; expires: number }> = new Map();
    private readonly CACHE_DURATION = 10 * 60 * 1000; // 10 minutes

    /**
     * Get current weather for coordinates
     */
    async getCurrentWeather(coords: Coordinates): Promise<WeatherData | null> {
        const cacheKey = `${coords.latitude.toFixed(2)},${coords.longitude.toFixed(2)}`;

        // Check cache
        const cached = this.cache.get(cacheKey);
        if (cached && cached.expires > Date.now()) {
            return cached.data;
        }

        try {
            const url = `${config.weather.baseUrl}/weather?lat=${coords.latitude}&lon=${coords.longitude}&units=${config.weather.units}&appid=${config.weather.apiKey}`;

            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`Weather API error: ${response.status}`);
            }

            const data = await response.json();

            const weatherData: WeatherData = {
                temperature: Math.round(data.main.temp),
                feelsLike: Math.round(data.main.feels_like),
                condition: data.weather[0].main,
                description: data.weather[0].description,
                humidity: data.main.humidity,
                windSpeed: Math.round(data.wind.speed),
                icon: data.weather[0].icon,
                timestamp: Date.now(),
            };

            // Cache the result
            this.cache.set(cacheKey, {
                data: weatherData,
                expires: Date.now() + this.CACHE_DURATION,
            });

            return weatherData;
        } catch (error) {
            console.error('Error fetching weather:', error);
            return null;
        }
    }

    /**
     * Get weather context for recommendations
     */
    getWeatherContext(weather: WeatherData): WeatherContext {
        const temp = weather.temperature;
        const condition = weather.condition.toLowerCase();

        const isCold = temp < 50;
        const isHot = temp > 80;
        const isRaining = condition.includes('rain') || condition.includes('drizzle');
        const isNice = temp >= 60 && temp <= 75 && !isRaining;

        let recommendation = '';
        if (isRaining) {
            recommendation = 'Rainy day - perfect for cozy indoor dining';
        } else if (isCold) {
            recommendation = 'Cold weather - ideal for warm comfort food';
        } else if (isHot) {
            recommendation = 'Hot day - great for refreshing meals and cold drinks';
        } else if (isNice) {
            recommendation = 'Beautiful weather - perfect for outdoor dining';
        } else {
            recommendation = 'Good day for dining out';
        }

        return {
            isCold,
            isHot,
            isRaining,
            isNice,
            recommendation,
        };
    }

    /**
     * Get weather icon URL from OpenWeatherMap
     */
    getWeatherIconUrl(iconCode: string): string {
        return `https://openweathermap.org/img/wn/${iconCode}@2x.png`;
    }

    /**
     * Format temperature for display
     */
    formatTemperature(temp: number): string {
        return `${Math.round(temp)}°F`;
    }

    /**
     * Clear weather cache
     */
    clearCache(): void {
        this.cache.clear();
    }
}

export const weatherService = new WeatherService();
