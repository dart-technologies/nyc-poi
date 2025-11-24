/**
 * DiscoverHeader - Header with neighborhood, context, time selector, and view toggle
 */

import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Dimensions } from 'react-native';
import { colors, spacing, typography, borderRadius } from '../../styles/tokens';

const { width: SCREEN_WIDTH } = Dimensions.get('window');
const IS_SMALL_DEVICE = SCREEN_WIDTH < 375;

type TimeSlot = 'morning' | 'lunch' | 'afternoon' | 'evening' | 'night';
type ViewMode = 'map' | 'list';

interface TimeOption {
    label: string;
    value: TimeSlot;
}

interface DiscoverHeaderProps {
    neighborhood: string;
    contextLabel: string;
    timeLabel: string;
    timeOfDay: TimeSlot;
    viewMode: ViewMode;
    statusMessage?: string | null;
    timeOptions: TimeOption[];
    onTimeChange: (time: TimeSlot) => void;
    onViewModeToggle: () => void;
}

const DiscoverHeader = React.memo<DiscoverHeaderProps>(({
    neighborhood,
    contextLabel,
    timeLabel,
    timeOfDay,
    viewMode,
    statusMessage,
    timeOptions,
    onTimeChange,
    onViewModeToggle,
}) => {
    const [timeDropdownVisible, setTimeDropdownVisible] = useState(false);

    const handleTimeSelect = (time: TimeSlot) => {
        onTimeChange(time);
        setTimeDropdownVisible(false);
    };

    return (
        <>
            <View style={styles.header}>
                <View style={{ flex: 1 }}>
                    <Text style={styles.title}>{neighborhood}</Text>
                    <View style={{ flexDirection: 'row', alignItems: 'center' }}>
                        <Text style={styles.subtitle}>{contextLabel}</Text>
                        <Text style={[styles.subtitle, { marginHorizontal: 6 }]}> • </Text>
                        <TouchableOpacity onPress={() => setTimeDropdownVisible((prev) => !prev)}>
                            <Text style={[styles.subtitle, styles.timeClickable]}>
                                {timeLabel} {timeDropdownVisible ? '▲' : '▼'}
                            </Text>
                        </TouchableOpacity>
                    </View>
                    {statusMessage && <Text style={styles.statusText}>{statusMessage}</Text>}
                </View>
                <TouchableOpacity style={styles.viewToggleButton} onPress={onViewModeToggle}>
                    <Text style={styles.viewToggleButtonText}>
                        {viewMode === 'map' ? '📋 List' : '🗺️ Map'}
                    </Text>
                </TouchableOpacity>
            </View>

            {timeDropdownVisible && (
                <View style={styles.timeDropdown}>
                    {timeOptions.map((option) => (
                        <TouchableOpacity
                            key={option.value}
                            style={[
                                styles.timeDropdownItem,
                                timeOfDay === option.value && styles.timeDropdownItemActive,
                            ]}
                            onPress={() => handleTimeSelect(option.value)}
                        >
                            <Text
                                style={[
                                    styles.timeDropdownText,
                                    timeOfDay === option.value && styles.timeDropdownTextActive,
                                ]}
                            >
                                {option.label}
                            </Text>
                        </TouchableOpacity>
                    ))}
                </View>
            )}
        </>
    );
});

DiscoverHeader.displayName = 'DiscoverHeader';

const styles = StyleSheet.create({
    header: {
        backgroundColor: 'transparent',
        paddingTop: IS_SMALL_DEVICE ? 12 : 16,
        paddingBottom: IS_SMALL_DEVICE ? 12 : 16,
        paddingHorizontal: IS_SMALL_DEVICE ? 16 : 20,
        borderBottomWidth: 1,
        borderBottomColor: colors.borderLight,
        flexDirection: 'row',
        alignItems: 'center',
    },
    title: {
        ...typography.h2,
        color: colors.text.primary,
        marginBottom: spacing.xs,
    },
    subtitle: {
        ...typography.bodySmall,
        color: colors.text.secondary,
    },
    timeClickable: {
        color: colors.primary,
        textDecorationLine: 'underline',
    },
    statusText: {
        ...typography.caption,
        color: colors.primary,
        marginTop: spacing.xs,
    },
    viewToggleButton: {
        paddingHorizontal: 14,
        paddingVertical: 8,
        borderRadius: borderRadius.md,
        backgroundColor: 'rgba(255, 193, 7, 0.2)',
        borderWidth: 1,
        borderColor: colors.borderActive,
    },
    viewToggleButtonText: {
        color: colors.primary,
        fontWeight: '600',
    },
    timeDropdown: {
        backgroundColor: colors.surface,
        borderBottomWidth: 1,
        borderBottomColor: colors.borderActive,
        flexDirection: 'row',
        paddingHorizontal: spacing.lg,
        paddingVertical: spacing.sm,
    },
    timeDropdownItem: {
        paddingHorizontal: spacing.md,
        paddingVertical: 6,
        borderRadius: borderRadius.md,
        backgroundColor: 'rgba(255, 255, 255, 0.05)',
        marginRight: spacing.sm,
    },
    timeDropdownItemActive: {
        backgroundColor: 'rgba(255, 193, 7, 0.2)',
    },
    timeDropdownText: {
        ...typography.caption,
        color: colors.text.secondary,
    },
    timeDropdownTextActive: {
        color: colors.primary,
    },
});

export default DiscoverHeader;
