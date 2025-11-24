/**
 * MapMarker - Optimized, memoized marker component for map view
 */

import React from 'react';
import { View, Text, Image, StyleSheet } from 'react-native';
import { Marker } from 'react-native-maps';
import { POI, Coordinates } from '../../services/mcpService';
import { colors } from '../../styles/tokens';

interface MapMarkerProps {
    poi: POI;
    isSelected: boolean;
    onPress: (poi: POI) => void;
    zIndex: number;
    getCoordinates: (poi: POI) => Coordinates;
}

const getPrestigeColor = (prestigeScore: number): string => {
    if (prestigeScore >= 100) return colors.prestige.gold;
    if (prestigeScore >= 50) return colors.prestige.amber;
    if (prestigeScore >= 25) return colors.prestige.blue;
    return colors.prestige.gray;
};

const MapMarker = React.memo<MapMarkerProps>(
    ({ poi, isSelected, onPress, zIndex, getCoordinates }) => {
        const coords = getCoordinates(poi);
        const logo = poi.media?.logo_url;
        const michelinStars = poi.prestige?.michelin_stars || 0;
        const prestigeScore = poi.prestige?.score || 0;
        const markerColor = getPrestigeColor(prestigeScore);

        return (
            <Marker
                key={`marker-${poi._id}`}
                coordinate={coords}
                title={poi.name}
                onPress={() => onPress(poi)}
                zIndex={zIndex}
            >
                <View
                    style={[
                        styles.markerBubble,
                        isSelected && styles.markerBubbleActive,
                        { borderColor: markerColor },
                    ]}
                >
                    {logo ? (
                        <Image source={{ uri: logo }} style={styles.markerLogo} />
                    ) : (
                        <View style={[styles.markerFallback, { backgroundColor: markerColor }]}>
                            <Text style={styles.markerFallbackText}>{poi.name.charAt(0)}</Text>
                        </View>
                    )}
                    {michelinStars > 0 && (
                        <View style={styles.markerStarBadge}>
                            <Text style={styles.markerStarText}>
                                {'⭐'.repeat(Math.min(michelinStars, 3))}
                            </Text>
                        </View>
                    )}
                </View>
            </Marker>
        );
    },
    // Custom comparison for better performance
    (prevProps, nextProps) => {
        return (
            prevProps.poi._id === nextProps.poi._id &&
            prevProps.isSelected === nextProps.isSelected
        );
    }
);

MapMarker.displayName = 'MapMarker';

const styles = StyleSheet.create({
    markerBubble: {
        alignItems: 'center',
        justifyContent: 'center',
        width: 48,
        height: 48,
        borderRadius: 24,
        backgroundColor: 'rgba(10, 10, 30, 0.9)',
        borderWidth: 3,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.3,
        shadowRadius: 4,
    },
    markerBubbleActive: {
        borderWidth: 5,
        borderColor: colors.primary,
        backgroundColor: 'rgba(255, 193, 7, 0.3)',
        shadowColor: colors.primary,
        shadowOpacity: 0.8,
        shadowRadius: 12,
        shadowOffset: { width: 0, height: 0 },
        transform: [{ scale: 1.3 }],
    },
    markerLogo: {
        width: 40,
        height: 40,
        borderRadius: 20,
    },
    markerFallback: {
        width: 40,
        height: 40,
        borderRadius: 20,
        justifyContent: 'center',
        alignItems: 'center',
    },
    markerFallbackText: {
        color: '#ffffff',
        fontWeight: '800',
        fontSize: 18,
    },
    markerStarBadge: {
        position: 'absolute',
        top: -6,
        right: -6,
        backgroundColor: 'rgba(0, 0, 0, 0.9)',
        borderRadius: 10,
        paddingHorizontal: 4,
        paddingVertical: 2,
        borderWidth: 1.5,
        borderColor: colors.prestige.gold,
    },
    markerStarText: {
        fontSize: 9,
        lineHeight: 10,
    },
});

export default MapMarker;
