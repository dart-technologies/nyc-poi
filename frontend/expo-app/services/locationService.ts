/**
 * Location Services
 * Handles GPS location requests and permissions
 */

import * as Location from 'expo-location';

export interface Coordinates {
    latitude: number;
    longitude: number;
}

export interface LocationResult {
    coords: Coordinates;
    timestamp: number;
    accuracy?: number;
    address?: string;
}

class LocationService {
    private lastLocation: LocationResult | null = null;
    private lastGeocode: { query: string; coords: Coordinates } | null = null;

    /**
     * Request location permissions
     */
    async requestPermissions(): Promise<boolean> {
        try {
            const { status } = await Location.requestForegroundPermissionsAsync();
            return status === 'granted';
        } catch (error) {
            console.error('Error requesting location permissions:', error);
            return false;
        }
    }

    /**
     * Check if location permissions are granted
     */
    async hasPermissions(): Promise<boolean> {
        try {
            const { status } = await Location.getForegroundPermissionsAsync();
            return status === 'granted';
        } catch (error) {
            console.error('Error checking location permissions:', error);
            return false;
        }
    }

    /**
     * Get current location
     */
    async getCurrentLocation(): Promise<LocationResult | null> {
        try {
            const hasPermission = await this.hasPermissions();
            if (!hasPermission) {
                const granted = await this.requestPermissions();
                if (!granted) {
                    throw new Error('Location permissions not granted');
                }
            }

            const location = await Location.getCurrentPositionAsync({
                accuracy: Location.Accuracy.Balanced,
            });

            this.lastLocation = {
                coords: {
                    latitude: location.coords.latitude,
                    longitude: location.coords.longitude,
                },
                timestamp: location.timestamp,
                accuracy: location.coords.accuracy || undefined,
            };

            return this.lastLocation;
        } catch (error) {
            console.error('Error getting current location:', error);
            return null;
        }
    }

    /**
     * Get reverse geocoded address for coordinates
     */
    async getAddress(coords: Coordinates): Promise<string | null> {
        try {
            const results = await Location.reverseGeocodeAsync(coords);
            if (results.length > 0) {
                const result = results[0];
                return `${result.street || ''}, ${result.city || ''}, ${result.region || ''}`.trim();
            }
            return null;
        } catch (error) {
            console.error('Error reverse geocoding:', error);
            return null;
        }
    }

    /**
     * Calculate distance between two coordinates in meters
     */
    calculateDistance(coord1: Coordinates, coord2: Coordinates): number {
        const R = 6371e3; // Earth's radius in meters
        const φ1 = (coord1.latitude * Math.PI) / 180;
        const φ2 = (coord2.latitude * Math.PI) / 180;
        const Δφ = ((coord2.latitude - coord1.latitude) * Math.PI) / 180;
        const Δλ = ((coord2.longitude - coord1.longitude) * Math.PI) / 180;

        const a =
            Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
            Math.cos(φ1) * Math.cos(φ2) * Math.sin(Δλ / 2) * Math.sin(Δλ / 2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

        return R * c;
    }

    /**
     * Format distance for display (in miles)
     */
    formatDistance(meters: number): string {
        const miles = meters / 1609.34;

        // For very short distances (< 0.1 miles), show in feet
        if (miles < 0.1) {
            const feet = Math.round(meters * 3.28084);
            return `${feet} ft`;
        }

        // Otherwise show miles with 1 decimal place
        return `${miles.toFixed(1)} mi`;
    }

    /**
     * Get last known location
     */
    getLastLocation(): LocationResult | null {
        return this.lastLocation;
    }

    /**
     * Geocode a free-form address/place string into coordinates
     */
    async geocodeAddress(query: string): Promise<Coordinates | null> {
        if (!query.trim()) {
            return null;
        }

        // Return cached match if the query hasn't changed
        if (this.lastGeocode && this.lastGeocode.query === query.trim()) {
            return this.lastGeocode.coords;
        }

        try {
            const [result] = await Location.geocodeAsync(query.trim());
            if (result?.latitude && result?.longitude) {
                const coords = {
                    latitude: result.latitude,
                    longitude: result.longitude,
                };
                this.lastGeocode = { query: query.trim(), coords };
                return coords;
            }
            return null;
        } catch (error) {
            console.error('Error geocoding address:', error);
            return null;
        }
    }
}

export const locationService = new LocationService();
