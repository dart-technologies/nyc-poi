/**
 * POI Map Component with Custom Marker Overlay
 * Workaround for expo-maps marker rendering issues with New Architecture
 * Uses Apple Maps for the map view and custom View components for markers
 */

import React, { useEffect, useState } from 'react';
import { StyleSheet, View, ActivityIndicator, Text, TouchableOpacity } from 'react-native';
import { AppleMaps } from 'expo-maps';
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
    const [mapRegion, setMapRegion] = useState({ latitude: 40.7580, longitude: -73.9855, zoom: 13 });

    useEffect(() => {
        loadUserLocation();
    }, []);

    const loadUserLocation = async () => {
        try {
            const location = await locationService.getCurrentLocation();
            if (location && location.coords) {
                setUserLocation(location.coords);
                setMapRegion({
                    latitude: location.coords.latitude,
                    longitude: location.coords.longitude,
                    zoom: 13,
                });
            }
        } catch (error) {
            console.error('Failed to get user location:', error);
            // Default to Times Square if location fails
            if (pois.length > 0) {
                const [lng, lat] = pois[0].location.coordinates;
                setMapRegion({ latitude: lat, longitude: lng, zoom: 13 });
            }
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

    console.log('POIMap: Rendering with', pois.length, 'POIs');

    return (
        <View style={[styles.container, style]}>
            {/* Apple Maps Base Layer */}
            <AppleMaps.View
                style={styles.map}
                cameraPosition={{
                    coordinates: { latitude: mapRegion.latitude, longitude: mapRegion.longitude },
                    zoom: mapRegion.zoom,
                }}
                uiSettings={{
                    compassEnabled: true,
                }}
                onCameraMove={(event) => {
                    setMapRegion({
                        latitude: event.coordinates?.latitude ?? mapRegion.latitude,
                        longitude: event.coordinates?.longitude ?? mapRegion.longitude,
                        zoom: event.zoom ?? mapRegion.zoom,
                    });
                }}
            />

            {/* Custom Marker Overlay - Works with New Architecture */}
            <View style={styles.markerOverlay} pointerEvents="box-none">
                {pois.map((poi) => {
                    const [longitude, latitude] = poi.location.coordinates;
                    const michelinStars = poi.prestige?.michelin_stars || 0;

                    // Calculate pixel position (simplified - would need proper projection in production)
                    const markerPosition = calculateMarkerPosition(
                        { latitude, longitude },
                        mapRegion
                    );

                    return (
                        <TouchableOpacity
                            key={poi._id}
                            style={[
                                styles.customMarker,
                                {
                                    left: markerPosition.x,
                                    top: markerPosition.y,
                                    backgroundColor: getMarkerColor(michelinStars),
                                },
                            ]}
                            onPress={() => onMarkerPress?.(poi)}
                        >
                            <Text style={styles.markerText}>
                                {michelinStars >= 3 ? '⭐⭐⭐' : michelinStars >= 1 ? '⭐'.repeat(michelinStars) : '📍'}
                            </Text>
                            <View style={styles.markerLabel}>
                                <Text style={styles.markerLabelText} numberOfLines={1}>
                                    {poi.name}
                                </Text>
                            </View>
                        </TouchableOpacity>
                    );
                })}
            </View>
        </View>
    );
}

// Simplified coordinate to pixel conversion
// In production, you'd use proper map projection math
function calculateMarkerPosition(
    coords: Coordinates,
    mapRegion: { latitude: number; longitude: number; zoom: number }
): { x: number; y: number } {
    // This is a very simplified calculation
    // For a proper implementation, you'd need to use the actual map projection
    const centerLat = mapRegion.latitude;
    const centerLng = mapRegion.longitude;

    // Approximate pixels per degree at zoom level 13
    const scale = Math.pow(2, mapRegion.zoom - 10);
    const pixelsPerLng = 100 * scale;
    const pixelsPerLat = 100 * scale;

    const x = (coords.longitude - centerLng) * pixelsPerLng + 180; // 180 = half screen width
    const y = (centerLat - coords.latitude) * pixelsPerLat + 300; // 300 = half screen height

    return { x, y };
}

function getMarkerColor(michelinStars: number): string {
    switch (michelinStars) {
        case 3:
            return '#FFD700'; // Gold for 3-star
        case 2:
            return '#FF6B6B'; // Red for 2-star
        case 1:
            return '#6C63FF'; // Purple for 1-star
        default:
            return '#4ECDC4'; // Teal for no stars
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
    markerOverlay: {
        ...StyleSheet.absoluteFillObject,
        justifyContent: 'center',
        alignItems: 'center',
    },
    customMarker: {
        position: 'absolute',
        padding: 8,
        borderRadius: 20,
        borderWidth: 2,
        borderColor: '#fff',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.3,
        shadowRadius: 4,
        elevation: 5,
        alignItems: 'center',
    },
    markerText: {
        fontSize: 16,
    },
    markerLabel: {
        marginTop: 4,
        paddingHorizontal: 6,
        paddingVertical: 2,
        backgroundColor: 'rgba(0, 0, 0, 0.7)',
        borderRadius: 4,
    },
    markerLabelText: {
        fontSize: 10,
        color: '#fff',
        fontWeight: '600',
    },
});
