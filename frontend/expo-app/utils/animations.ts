/**
 * Animation Utilities - Reusable animation helpers
 */

import { Animated, Easing } from 'react-native';

// Standard durations
export const DURATION = {
    fast: 150,
    normal: 250,
    slow: 400,
    verySlow: 600,
};

// Standard easing curves
export const EASING = {
    default: Easing.bezier(0.4, 0, 0.2, 1),
    in: Easing.in(Easing.ease),
    out: Easing.out(Easing.ease),
    bounce: Easing.elastic(1.2),
};

/**
 * Pulse animation - scales element up and back down
 */
export const createPulseAnimation = (
    animatedValue: Animated.Value,
    scale: number = 1.05,
    duration: number = DURATION.fast
): Animated.CompositeAnimation => {
    return Animated.sequence([
        Animated.timing(animatedValue, {
            toValue: scale,
            duration,
            easing: EASING.out,
            useNativeDriver: true,
        }),
        Animated.timing(animatedValue, {
            toValue: 1,
            duration,
            easing: EASING.in,
            useNativeDriver: true,
        }),
    ]);
};

/**
 * Press animation - scales element down on press
 */
export const createPressAnimation = (
    animatedValue: Animated.Value,
    scale: number = 0.95,
    duration: number = 100
): {
    onPressIn: () => void;
    onPressOut: () => void;
} => {
    return {
        onPressIn: () => {
            Animated.timing(animatedValue, {
                toValue: scale,
                duration,
                useNativeDriver: true,
            }).start();
        },
        onPressOut: () => {
            Animated.timing(animatedValue, {
                toValue: 1,
                duration,
                useNativeDriver: true,
            }).start();
        },
    };
};

/**
 * Glow animation - loops opacity for glowing effect
 */
export const createGlowAnimation = (
    animatedValue: Animated.Value,
    duration: number = 1000
): Animated.CompositeAnimation => {
    return Animated.loop(
        Animated.sequence([
            Animated.timing(animatedValue, {
                toValue: 1,
                duration,
                easing: EASING.default,
                useNativeDriver: true,
            }),
            Animated.timing(animatedValue, {
                toValue: 0.4,
                duration,
                easing: EASING.default,
                useNativeDriver: true,
            }),
        ])
    );
};

/**
 * Fade in animation
 */
export const createFadeInAnimation = (
    animatedValue: Animated.Value,
    duration: number = DURATION.normal
): Animated.CompositeAnimation => {
    return Animated.timing(animatedValue, {
        toValue: 1,
        duration,
        easing: EASING.out,
        useNativeDriver: true,
    });
};

/**
 * Fade out animation
 */
export const createFadeOutAnimation = (
    animatedValue: Animated.Value,
    duration: number = DURATION.normal
): Animated.CompositeAnimation => {
    return Animated.timing(animatedValue, {
        toValue: 0,
        duration,
        easing: EASING.in,
        useNativeDriver: true,
    });
};

/**
 * Slide in from bottom animation
 */
export const createSlideInAnimation = (
    animatedValue: Animated.Value,
    fromValue: number = 50,
    duration: number = DURATION.normal
): Animated.CompositeAnimation => {
    animatedValue.setValue(fromValue);
    return Animated.timing(animatedValue, {
        toValue: 0,
        duration,
        easing: EASING.out,
        useNativeDriver: true,
    });
};

/**
 * Spring animation - bouncy effect
 */
export const createSpringAnimation = (
    animatedValue: Animated.Value,
    toValue: number,
    tension: number = 40,
    friction: number = 7
): Animated.CompositeAnimation => {
    return Animated.spring(animatedValue, {
        toValue,
        tension,
        friction,
        useNativeDriver: true,
    });
};

/**
 * Shimmer animation for loading states
 */
export const createShimmerAnimation = (
    animatedValue: Animated.Value,
    duration: number = 1500
): Animated.CompositeAnimation => {
    return Animated.loop(
        Animated.timing(animatedValue, {
            toValue: 1,
            duration,
            easing: Easing.linear,
            useNativeDriver: true,
        })
    );
};

/**
 * Stagger animations - delays each animation in sequence
 */
export const createStaggerAnimation = (
    animations: Animated.CompositeAnimation[],
    staggerDelay: number = 50
): Animated.CompositeAnimation => {
    return Animated.stagger(staggerDelay, animations);
};
