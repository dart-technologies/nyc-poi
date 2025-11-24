/**
 * POI Map Component using react-native-maps
 * Direct implementation with react-native-maps for better New Architecture compatibility
 */

import React, { useEffect, useState } from 'react';
import { StyleSheet, View, ActivityIndicator } from 'react-native';
import MapView, { Marker, PROVIDER_DEFAULT } from 'react-native-maps';
import { POI } from '../services/mcpService';
import { Coordinates, locationService } from '../services/locationService';

export interface POIMapProps {
    pois: POI[];
    onMarkerPress?: (poi: POI) => void;
    showUserLocation?: boolean;
    style?: any;
}

export function POIMap({ pois, onMarkerPress, showUserLocation = true, style }: POIMapProps) {
    const [userLocation, setUserLocation] = useState<Coordinates | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadUserLocation();
    }, []);

    const loadUserLocation = async () => {
        try {
            const location = await locationService.getCurrentLocation();
            if (location && location.coords) {
                setUserLocation(location.coords);
            }
        } catch (error) {
            console.error('Failed to get user location:', error);
            // Default to Times Square if location fails
            setUserLocation({
                latitude: 40.7580,
                longitude: -73.9855,
            });
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <View style={[styles.container, styles.loadingContainer, style]}>
                <ActivityIndicator size="large" color="#6C63FF" />
            </View>
        );
    }

    // Calculate initial region
    const initialRegion = userLocation
        ? {
            latitude: userLocation.latitude,
            longitude: userLocation.longitude,
            latitudeDelta: 0.03,
            longitudeDelta: 0.03,
        }
        : pois.length > 0
            ? {
                latitude: pois[0].location.coordinates[1],
                longitude: pois[0].location.coordinates[0],
                latitudeDelta: 0.03,
                longitudeDelta: 0.03,
            }
            : {
                latitude: 40.7580,
                longitude: -73.9855,
                latitudeDelta: 0.03,
                longitudeDelta: 0.03,
            };

    console.log('POIMap (react-native-maps): Rendering', pois.length, 'POIs');

    return (
        <View style={[styles.container, style]}>
            <MapView
                style={styles.map}
                provider={PROVIDER_DEFAULT} // Use Apple Maps on iOS
                initialRegion={initialRegion}
                showsUserLocation={showUserLocation}
                showsMyLocationButton={true}
                showsCompass={true}
            >
                {pois.map((poi) => {
                    const [longitude, latitude] = poi.location.coordinates;
                    const michelinStars = poi.prestige?.michelin_stars || 0;

                    return (
                        <Marker
                            key={poi._id}
                            coordinate={{ latitude, longitude }}
                            title={poi.name}
                            description={getMarkerDescription(poi)}
                            pinColor={getMarkerColor(michelinStars)}
                            onPress={() => {
                                console.log('Marker pressed:', poi.name);
                                onMarkerPress?.(poi);
                            }}
                        />
                    );
                })}
            </MapView>
        </View>
    );
}

function getMarkerDescription(poi: POI): string {
    const parts: string[] = [];

    if (poi.prestige?.michelin_stars) {
        parts.push(`${'⭐'.repeat(poi.prestige.michelin_stars)} Michelin`);
    }

    if (poi.experience?.price_range) {
        parts.push(poi.experience.price_range);
    }

    if (poi.address?.neighborhood) {
        parts.push(poi.address.neighborhood);
    }

    if (poi.distance) {
        const distanceKm = (poi.distance / 1000).toFixed(1);
        parts.push(`${distanceKm}km away`);
    }

    return parts.join(' · ');
}

function getMarkerColor(michelinStars: number): string {
    switch (michelinStars) {
        case 3:
            return 'gold'; // Gold for 3-star
        case 2:
            return 'red'; // Red for 2-star
        case 1:
            return 'purple'; // Purple for 1-star
        default:
            return 'blue'; // Blue for no stars
    }
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        overflow: 'hidden',
        borderRadius: 16,
    },
    loadingContainer: {
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: '#1a1a2e',
    },
    map: {
        flex: 1,
    },
});
