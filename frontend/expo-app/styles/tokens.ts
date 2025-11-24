/**
 * Design Tokens - Shared styling constants
 * Use these across all components for consistency
 */

export const colors = {
    // Primary brand
    primary: '#00d4ff',
    primaryDark: '#0099cc',
    primaryLight: '#33ddff',

    // Background
    background: '#0a0a1e',
    surface: 'rgba(10, 10, 30, 0.95)',
    surfaceElevated: 'rgba(26, 26, 46, 0.7)',

    // Borders
    border: 'rgba(255, 255, 255, 0.1)',
    borderLight: 'rgba(255, 255, 255, 0.05)',
    borderActive: 'rgba(255, 193, 7, 0.3)',

    // Text
    text: {
        primary: '#ffffff',
        secondary: 'rgba(255, 255, 255, 0.7)',
        tertiary: 'rgba(255, 255, 255, 0.5)',
        disabled: 'rgba(255, 255, 255, 0.3)',
    },

    // Semantic
    success: '#10b981',
    warning: '#f59e0b',
    error: '#ef4444',
    info: '#3b82f6',

    // Prestige colors
    prestige: {
        gold: '#FFD700',
        amber: '#F59E0B',
        blue: '#3B82F6',
        gray: '#6B7280',
    },

    // Overlays
    overlay: 'rgba(0, 0, 0, 0.5)',
    overlayLight: 'rgba(0, 0, 0, 0.3)',
};

export const spacing = {
    xs: 4,
    sm: 8,
    md: 12,
    lg: 16,
    xl: 20,
    xxl: 24,
    xxxl: 32,
};

export const borderRadius = {
    sm: 8,
    md: 12,
    lg: 16,
    xl: 20,
    xxl: 24,
    full: 9999,
};

export const typography = {
    // Headers
    h1: {
        fontSize: 32,
        fontWeight: '700' as const,
        lineHeight: 40,
    },
    h2: {
        fontSize: 28,
        fontWeight: '700' as const,
        lineHeight: 36,
    },
    h3: {
        fontSize: 24,
        fontWeight: '600' as const,
        lineHeight: 32,
    },

    // Body
    body: {
        fontSize: 16,
        fontWeight: '400' as const,
        lineHeight: 24,
    },
    bodyLarge: {
        fontSize: 18,
        fontWeight: '400' as const,
        lineHeight: 28,
    },
    bodySmall: {
        fontSize: 14,
        fontWeight: '400' as const,
        lineHeight: 20,
    },

    // Special
    caption: {
        fontSize: 13,
        fontWeight: '500' as const,
        lineHeight: 18,
    },
    label: {
        fontSize: 15,
        fontWeight: '600' as const,
        lineHeight: 20,
    },
};

export const shadows = {
    small: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 2,
    },
    medium: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.2,
        shadowRadius: 8,
        elevation: 4,
    },
    large: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 8 },
        shadowOpacity: 0.3,
        shadowRadius: 16,
        elevation: 8,
    },
    glow: {
        shadowColor: '#00d4ff',
        shadowOffset: { width: 0, height: 0 },
        shadowOpacity: 0.6,
        shadowRadius: 12,
        elevation: 6,
    },
};

export const animations = {
    // Durations (in ms)
    duration: {
        fast: 150,
        normal: 250,
        slow: 400,
        verySlow: 600,
    },

    // Standard easing
    easing: {
        default: 'ease-in-out',
        in: 'ease-in',
        out: 'ease-out',
    },
};

export const layout = {
    // Screen breakpoints
    breakpoints: {
        small: 375,  // iPhone SE
        medium: 390, // iPhone 13
        large: 428,  // iPhone Pro Max
    },

    // Common dimensions
    headerHeight: 60,
    tabBarHeight: 80,
    carouselHeight: 140,
    markerSize: 48,
    buttonHeight: 44,
};

// Helper functions
export const getPrestigeColor = (prestigeScore: number): string => {
    if (prestigeScore >= 100) return colors.prestige.gold;
    if (prestigeScore >= 50) return colors.prestige.amber;
    if (prestigeScore >= 25) return colors.prestige.blue;
    return colors.prestige.gray;
};

export const getSpacing = (...multipliers: number[]): number => {
    return multipliers.reduce((sum, m) => sum + (spacing.md * m), 0);
};
