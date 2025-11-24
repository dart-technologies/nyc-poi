/**
 * POI Card Component
 * Displays restaurant information with prestige badges
 */

import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Linking } from 'react-native';
import { POI } from '../services/mcpService';

interface POICardProps {
    poi: POI;
    onPress?: () => void;
}

export function POICard({ poi, onPress }: POICardProps) {
    const handleCall = async () => {
        if (poi.contact.phone) {
            try {
                await Linking.openURL(`tel:${poi.contact.phone}`);
            } catch (error) {
                console.log('Phone link not available in simulator');
            }
        }
    };

    const handleWebsite = async () => {
        if (poi.contact.website) {
            try {
                await Linking.openURL(poi.contact.website);
            } catch (error) {
                console.log('Website link not available in simulator');
            }
        }
    };

    const handleReservation = async () => {
        try {
            if (poi.contact.reservations_url) {
                await Linking.openURL(poi.contact.reservations_url);
            } else if (poi.contact.website) {
                await Linking.openURL(poi.contact.website);
            }
        } catch (error) {
            console.log('Reservation link not available in simulator');
        }
    };

    return (
        <TouchableOpacity style={styles.card} onPress={onPress} activeOpacity={0.7}>
            {/* Header with name and distance */}
            <View style={styles.header}>
                <View style={styles.titleContainer}>
                    <Text style={styles.name} numberOfLines={1}>{poi.name}</Text>
                    <Text style={styles.neighborhood}>{poi.address.neighborhood}</Text>
                </View>
                {poi.distance_formatted && (
                    <Text style={styles.distance}>{poi.distance_formatted}</Text>
                )}
            </View>

            {/* Prestige Badges */}
            {renderPrestigeBadges(poi)}

            {/* Category and Price */}
            <View style={styles.meta}>
                <Text style={styles.category}>
                    {poi.subcategories.join(', ') || poi.category}
                </Text>
                <Text style={styles.price}>{poi.experience.price_range}</Text>
            </View>

            {/* Signature Dishes */}
            {poi.experience.signature_dishes && poi.experience.signature_dishes.length > 0 && (
                <Text style={styles.dishes} numberOfLines={2}>
                    Known for: {poi.experience.signature_dishes.slice(0, 3).join(', ')}
                </Text>
            )}

            {/* Action Buttons */}
            <View style={styles.actions}>
                {poi.contact.phone && (
                    <TouchableOpacity style={styles.actionButton} onPress={handleCall}>
                        <Text style={styles.actionText}>📞 Call</Text>
                    </TouchableOpacity>
                )}
                {poi.contact.website && (
                    <TouchableOpacity style={styles.actionButton} onPress={handleWebsite}>
                        <Text style={styles.actionText}>🌐 Website</Text>
                    </TouchableOpacity>
                )}
                {(poi.contact.reservations_url || poi.contact.website) && (
                    <TouchableOpacity style={[styles.actionButton, styles.primaryButton]} onPress={handleReservation}>
                        <Text style={[styles.actionText, styles.primaryText]}>Reserve</Text>
                    </TouchableOpacity>
                )}
            </View>
        </TouchableOpacity>
    );
}

function renderPrestigeBadges(poi: POI) {
    const badges: React.ReactElement[] = [];

    // Michelin Stars
    if (poi.prestige.michelin_stars && poi.prestige.michelin_stars > 0) {
        const stars = '⭐'.repeat(poi.prestige.michelin_stars);
        badges.push(
            <View key="michelin" style={[styles.badge, styles.michelinBadge]}>
                <Text style={styles.badgeText}>
                    {stars} MICHELIN {poi.prestige.michelin_since ? `(${poi.prestige.michelin_since})` : ''}
                </Text>
            </View>
        );
    }

    // Michelin Bib Gourmand
    if (poi.prestige.michelin_bib_gourmand) {
        badges.push(
            <View key="bib" style={[styles.badge, styles.bibBadge]}>
                <Text style={styles.badgeText}>🍴 BIB GOURMAND</Text>
            </View>
        );
    }

    // James Beard Awards
    if (poi.prestige.james_beard_awards && poi.prestige.james_beard_awards.length > 0) {
        badges.push(
            <View key="jb" style={[styles.badge, styles.jamesBeardbadge]}>
                <Text style={styles.badgeText}>🏆 JAMES BEARD</Text>
            </View>
        );
    }

    // NYT Stars
    if (poi.prestige.nyt_stars && poi.prestige.nyt_stars > 0) {
        const stars = '★'.repeat(poi.prestige.nyt_stars);
        badges.push(
            <View key="nyt" style={[styles.badge, styles.nytBadge]}>
                <Text style={styles.badgeText}>{stars} NYT</Text>
            </View>
        );
    }

    if (badges.length > 0) {
        return <View style={styles.badgeContainer}>{badges}</View>;
    }

    return null;
}

const styles = StyleSheet.create({
    card: {
        backgroundColor: 'rgba(26, 26, 46, 0.7)',
        borderRadius: 20,
        padding: 18,
        marginVertical: 10,
        marginHorizontal: 16,
        borderWidth: 1,
        borderColor: 'rgba(255, 255, 255, 0.15)',
        shadowColor: '#00d4ff',
        shadowOffset: { width: 0, height: 6 },
        shadowOpacity: 0.15,
        shadowRadius: 12,
        elevation: 8,
    },
    header: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        marginBottom: 8,
    },
    titleContainer: {
        flex: 1,
        marginRight: 8,
    },
    name: {
        fontSize: 22,
        fontWeight: 'bold',
        color: '#ffffff',
        marginBottom: 4,
        textShadowColor: 'rgba(255, 193, 7, 0.3)',
        textShadowOffset: { width: 0, height: 0 },
        textShadowRadius: 8,
    },
    neighborhood: {
        fontSize: 14,
        color: 'rgba(255, 255, 255, 0.6)',
    },
    distance: {
        fontSize: 14,
        fontWeight: '700',
        color: '#00d4ff',
        textShadowColor: 'rgba(255, 193, 7, 0.5)',
        textShadowOffset: { width: 0, height: 0 },
        textShadowRadius: 6,
    },
    badgeContainer: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        gap: 8,
        marginVertical: 12,
    },
    badge: {
        paddingHorizontal: 14,
        paddingVertical: 7,
        borderRadius: 10,
        borderWidth: 1,
        shadowOffset: { width: 0, height: 3 },
        shadowOpacity: 0.4,
        shadowRadius: 6,
        elevation: 5,
    },
    michelinBadge: {
        backgroundColor: '#ff2d55',
        borderColor: '#ff5070',
        shadowColor: '#ff2d55',
    },
    bibBadge: {
        backgroundColor: '#e74c3c',
        borderColor: '#ef6c5d',
        shadowColor: '#e74c3c',
    },
    jamesBeardbadge: {
        backgroundColor: '#f39c12',
        borderColor: '#f5b041',
        shadowColor: '#f39c12',
    },
    nytBadge: {
        backgroundColor: '#3498db',
        borderColor: '#5dade2',
        shadowColor: '#3498db',
    },
    badgeText: {
        color: '#ffffff',
        fontSize: 11,
        fontWeight: 'bold',
        letterSpacing: 0.5,
    },
    meta: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 8,
    },
    category: {
        fontSize: 14,
        color: 'rgba(255, 255, 255, 0.7)',
        textTransform: 'capitalize',
        flex: 1,
    },
    price: {
        fontSize: 17,
        fontWeight: '700',
        color: '#00ff88',
    },
    dishes: {
        fontSize: 13,
        color: 'rgba(255, 255, 255, 0.5)',
        fontStyle: 'italic',
        marginBottom: 12,
        lineHeight: 18,
    },
    actions: {
        flexDirection: 'row',
        gap: 8,
        marginTop: 8,
    },
    actionButton: {
        flex: 1,
        paddingVertical: 12,
        paddingHorizontal: 14,
        borderRadius: 12,
        backgroundColor: 'rgba(255, 255, 255, 0.1)',
        alignItems: 'center',
        borderWidth: 1,
        borderColor: 'rgba(255, 255, 255, 0.2)',
    },
    primaryButton: {
        backgroundColor: 'rgba(255, 193, 7, 0.25)',
        borderColor: 'rgba(255, 193, 7, 0.4)',
        shadowColor: '#00d4ff',
        shadowOffset: { width: 0, height: 3 },
        shadowOpacity: 0.3,
        shadowRadius: 6,
    },
    actionText: {
        fontSize: 13,
        fontWeight: '600',
        color: 'rgba(255, 255, 255, 0.8)',
    },
    primaryText: {
        color: '#00d4ff',
        fontWeight: '700',
    },
});
