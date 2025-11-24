/**
 * Map View Integration Example for Discover Tab
 * Shows how to add map view alongside the POI list
 */

import React, { useState } from 'react';
import { View, StyleSheet, TouchableOpacity, Text } from 'react-native';
import { POIMap } from '@/components/POIMap';
import { POI } from '@/services/mcpService';

// Add to your existing Discover screen component

interface MapViewToggleProps {
    pois: POI[];
    onPOISelect: (poi: POI) => void;
}

export function MapViewToggle({ pois, onPOISelect }: MapViewToggleProps) {
    const [showMap, setShowMap] = useState(false);

    return (
        <View style={styles.container}>
            {/* Toggle Button */}
            <View style={styles.toggleContainer}>
                <TouchableOpacity
                    style={[styles.toggleButton, !showMap && styles.activeButton]}
                    onPress={() => setShowMap(false)}
                >
                    <Text style={[styles.toggleText, !showMap && styles.activeText]}>
                        List
                    </Text>
                </TouchableOpacity>
                <TouchableOpacity
                    style={[styles.toggleButton, showMap && styles.activeButton]}
                    onPress={() => setShowMap(true)}
                >
                    <Text style={[styles.toggleText, showMap && styles.activeText]}>
                        Map
                    </Text>
                </TouchableOpacity>
            </View>

            {/* Map View */}
            {showMap && (
                <View style={styles.mapContainer}>
                    <POIMap
                        pois={pois}
                        showUserLocation={true}
                        onMarkerPress={onPOISelect}
                        style={styles.map}
                    />
                </View>
            )}
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
    },
    toggleContainer: {
        flexDirection: 'row',
        padding: 16,
        gap: 12,
    },
    toggleButton: {
        flex: 1,
        paddingVertical: 12,
        paddingHorizontal: 24,
        borderRadius: 12,
        backgroundColor: 'rgba(255, 255, 255, 0.1)',
        alignItems: 'center',
    },
    activeButton: {
        backgroundColor: 'rgba(108, 99, 255, 0.3)',
        borderWidth: 1,
        borderColor: '#6C63FF',
    },
    toggleText: {
        fontSize: 16,
        fontWeight: '600',
        color: 'rgba(255, 255, 255, 0.6)',
    },
    activeText: {
        color: '#FFFFFF',
    },
    mapContainer: {
        flex: 1,
        padding: 16,
        paddingTop: 0,
    },
    map: {
        flex: 1,
        borderRadius: 16,
    },
});

/*
 * INTEGRATION STEPS:
 * 
 * 1. Import this component in your Discover screen:
 *    import { MapViewToggle } from './MapViewToggle';
 * 
 * 2. Add state for view mode in your screen:
 *    const [pois, setPois] = useState<POI[]>([]);
 * 
 * 3. Replace or augment your current list view:
 *    <MapViewToggle 
 *      pois={pois} 
 *      onPOISelect={(poi) => {
 *        // Show POI details modal
 *        setSelectedPOI(poi);
 *      }} 
 *    />
 * 
 * 4. Keep your existing POI list rendering for list view
 * 
 * RESULT:
 * - Toggle between list and map views
 * - Tap markers to see POI details
 * - Same data, two visualizations
 */
