/**
 * FilterBar - Time-based contextual filters for Discover screen
 */

import React from 'react';
import { View, Text, TouchableOpacity, ScrollView, StyleSheet, Dimensions } from 'react-native';
import { colors, spacing, borderRadius, typography } from '../../styles/tokens';

const { width: SCREEN_WIDTH } = Dimensions.get('window');
const IS_SMALL_DEVICE = SCREEN_WIDTH < 375;

type TimeSlot = 'morning' | 'lunch' | 'afternoon' | 'evening' | 'night';

interface FilterOption {
    value: string;
    label: string;
    emoji: string;
}

interface FilterBarProps {
    timeOfDay: TimeSlot;
    filter: string;
    onFilterChange: (filter: string) => void;
}

const TIME_BASED_FILTERS: Record<TimeSlot, FilterOption[]> = {
    morning: [
        { value: 'all', label: 'All', emoji: '🌅' },
        { value: 'breakfast', label: 'Breakfast', emoji: '🥞' },
        { value: 'coffee', label: 'Coffee', emoji: '☕' },
        { value: 'brunch', label: 'Brunch', emoji: '🥂' },
    ],
    lunch: [
        { value: 'all', label: 'All', emoji: '☀️' },
        { value: 'casual', label: 'Casual', emoji: '🍔' },
        { value: 'quick-bites', label: 'Quick Bites', emoji: '🥙' },
        { value: 'michelin', label: 'Michelin', emoji: '⭐' },
    ],
    afternoon: [
        { value: 'all', label: 'All', emoji: '🌤️' },
        { value: 'michelin', label: 'Michelin', emoji: '⭐' },
        { value: 'fine-dining', label: 'Fine Dining', emoji: '🍽️' },
        { value: 'casual', label: 'Casual', emoji: '🍕' },
    ],
    evening: [
        { value: 'all', label: 'All', emoji: '🌆' },
        { value: 'fine-dining', label: 'Fine Dining', emoji: '🍽️' },
        { value: 'michelin', label: 'Michelin', emoji: '⭐' },
        { value: 'casual', label: 'Casual', emoji: '🍝' },
    ],
    night: [
        { value: 'all', label: 'All', emoji: '🌙' },
        { value: 'bars', label: 'Bars', emoji: '🍸' },
        { value: 'late-night', label: 'Late Night', emoji: '🌃' },
        { value: 'casual', label: 'Casual', emoji: '🍕' },
    ],
};

const FilterBar = React.memo<FilterBarProps>(({ timeOfDay, filter, onFilterChange }) => {
    const filters = TIME_BASED_FILTERS[timeOfDay];
    const [pressedButton, setPressedButton] = React.useState<string | null>(null);

    const handlePress = (filterValue: string) => {
        setPressedButton(filterValue);
        onFilterChange(filterValue);
        setTimeout(() => setPressedButton(null), 200);
    };

    return (
        <View style={styles.container}>
            <ScrollView
                horizontal
                showsHorizontalScrollIndicator={false}
                contentContainerStyle={styles.content}
            >
                {filters.map((filterOption) => {
                    const isActive = filter === filterOption.value;
                    const isPressed = pressedButton === filterOption.value;

                    return (
                        <TouchableOpacity
                            key={filterOption.value}
                            style={[
                                styles.button,
                                isActive && styles.buttonActive,
                                isPressed && styles.buttonPressed,
                            ]}
                            onPress={() => handlePress(filterOption.value)}
                            activeOpacity={0.7}
                        >
                            <Text style={[styles.text, isActive && styles.textActive]}>
                                {filterOption.emoji} {filterOption.label}
                            </Text>
                        </TouchableOpacity>
                    );
                })}
            </ScrollView>
        </View>
    );
});

FilterBar.displayName = 'FilterBar';

const styles = StyleSheet.create({
    container: {
        backgroundColor: colors.surfaceElevated,
        paddingVertical: 14,
        borderBottomWidth: 1,
        borderBottomColor: colors.borderLight,
    },
    content: {
        paddingHorizontal: spacing.lg,
    },
    button: {
        paddingHorizontal: 18,
        paddingVertical: 10,
        borderRadius: borderRadius.lg,
        backgroundColor: 'rgba(255, 255, 255, 0.08)',
        marginRight: 10,
        borderWidth: 1,
        borderColor: colors.border,
    },
    buttonActive: {
        backgroundColor: 'rgba(255, 193, 7, 0.25)',
        borderColor: colors.borderActive,
        shadowColor: colors.primary,
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.3,
        shadowRadius: 8,
    },
    buttonPressed: {
        transform: [{ scale: 0.95 }],
        opacity: 0.8,
    },
    text: {
        ...typography.label,
        color: colors.text.secondary,
    },
    textActive: {
        color: colors.primary,
    },
});

export default FilterBar;
