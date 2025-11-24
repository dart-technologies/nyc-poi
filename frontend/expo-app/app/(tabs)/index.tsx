/**
 * Discover Screen
 * Map-first exploration with contextual filters
 */

import React, {
  useState,
  useEffect,
  useRef,
  useMemo,
  useCallback,
} from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
  FlatList,
  Platform,
  Animated,
  Dimensions,
  LayoutAnimation,
  UIManager,
  Image,
} from 'react-native';
import type { ViewToken } from 'react-native';
import MapView, { Marker, PROVIDER_DEFAULT, Circle } from 'react-native-maps';
import { SafeAreaView } from 'react-native-safe-area-context';
import { router } from 'expo-router';
import { locationService, Coordinates } from '../../services/locationService';
import { mcpService, POI } from '../../services/mcpService';
import { POICard } from '../../components/POICard';

const { width: SCREEN_WIDTH } = Dimensions.get('window');
const IS_SMALL_DEVICE = SCREEN_WIDTH < 375;
const IS_LARGE_DEVICE = SCREEN_WIDTH >= 428;
const DEFAULT_CENTER: Coordinates = { latitude: 40.7580, longitude: -73.9855 };

type TimeSlot = 'morning' | 'lunch' | 'afternoon' | 'evening' | 'night';

const TIME_OPTIONS: { label: string; value: TimeSlot }[] = [
  { label: 'Morning', value: 'morning' },
  { label: 'Lunch', value: 'lunch' },
  { label: 'Afternoon', value: 'afternoon' },
  { label: 'Evening', value: 'evening' },
  { label: 'Night', value: 'night' },
];

const getTimeSlotForDate = (date: Date = new Date()): TimeSlot => {
  const hour = date.getHours();
  if (hour < 6) return 'night';
  if (hour < 11) return 'morning';
  if (hour < 14) return 'lunch';
  if (hour < 17) return 'afternoon';
  if (hour < 21) return 'evening';
  return 'night';
};

const formatTimeLabel = (slot: TimeSlot) => {
  switch (slot) {
    case 'morning':
      return 'Morning';
    case 'lunch':
      return 'Lunch';
    case 'afternoon':
      return 'Afternoon';
    case 'evening':
      return 'Evening';
    case 'night':
      return 'Night';
    default:
      return 'Now';
  }
};

const getPoiCoordinates = (poi: POI): Coordinates => ({
  latitude: poi.location.coordinates[1],
  longitude: poi.location.coordinates[0],
});

type NeighborhoodZone = {
  name: string;
  coords: Coordinates;
  radius: number; // meters
};

const MANHATTAN_NEIGHBORHOODS: NeighborhoodZone[] = [
  { name: 'Hudson Yards', coords: { latitude: 40.7540, longitude: -74.0020 }, radius: 800 },
  { name: 'Chelsea', coords: { latitude: 40.7465, longitude: -74.0014 }, radius: 900 },
  { name: 'Midtown West', coords: { latitude: 40.7624, longitude: -73.9850 }, radius: 900 },
  { name: 'Hell\'s Kitchen', coords: { latitude: 40.7638, longitude: -73.9910 }, radius: 900 },
  { name: 'Upper West Side', coords: { latitude: 40.7870, longitude: -73.9754 }, radius: 1200 },
  { name: 'Upper East Side', coords: { latitude: 40.7736, longitude: -73.9566 }, radius: 1200 },
  { name: 'Harlem', coords: { latitude: 40.8116, longitude: -73.9465 }, radius: 1500 },
  { name: 'Flatiron', coords: { latitude: 40.7411, longitude: -73.9897 }, radius: 700 },
  { name: 'Gramercy', coords: { latitude: 40.7377, longitude: -73.9847 }, radius: 700 },
  { name: 'East Village', coords: { latitude: 40.7265, longitude: -73.9815 }, radius: 900 },
  { name: 'West Village', coords: { latitude: 40.7348, longitude: -74.0030 }, radius: 800 },
  { name: 'SoHo', coords: { latitude: 40.7233, longitude: -74.0020 }, radius: 700 },
  { name: 'Tribeca', coords: { latitude: 40.7163, longitude: -74.0094 }, radius: 700 },
  { name: 'Financial District', coords: { latitude: 40.7075, longitude: -74.0113 }, radius: 700 },
];

const resolveNeighborhoodName = (coords: Coordinates | null, fallback?: string) => {
  if (coords) {
    const match = MANHATTAN_NEIGHBORHOODS.find(
      zone => locationService.calculateDistance(zone.coords, coords) <= zone.radius,
    );
    if (match) {
      return match.name;
    }
  }
  if (fallback) {
    return fallback.split(',')[0]?.trim() || fallback;
  }
  return 'Discover NYC';
};

const formatFriendlyAddress = (address?: string) => {
  if (!address) return 'your area';
  const parts = address.split(',').map(part => part.trim()).filter(Boolean);
  if (parts.length === 0) return 'your area';
  if (parts.length === 1) return parts[0];
  return `${parts[0]}, ${parts[1]}`;
};

// Time-based filter configurations
const TIME_BASED_FILTERS = {
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

const CAROUSEL_PLACEHOLDERS = [0, 1, 2];

// Enable LayoutAnimation on Android
if (Platform.OS === 'android' && UIManager.setLayoutAnimationEnabledExperimental) {
  UIManager.setLayoutAnimationEnabledExperimental(true);
}

export default function DiscoverScreen() {
  const [location, setLocation] = useState<Coordinates | null>(null);
  const [pois, setPois] = useState<POI[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'michelin' | 'fine-dining' | 'casual' | 'breakfast' | 'coffee' | 'brunch' | 'bars' | 'late-night' | 'quick-bites'>('all');
  const [viewMode, setViewMode] = useState<'list' | 'map'>('map');
  const [timeOfDay, setTimeOfDay] = useState<TimeSlot>(getTimeSlotForDate());
  const [timeDropdownVisible, setTimeDropdownVisible] = useState(false);
  const [selectedPoiId, setSelectedPoiId] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [activeCenter, setActiveCenter] = useState<Coordinates>(DEFAULT_CENTER);
  const [activeNeighborhood, setActiveNeighborhood] = useState<string>('Midtown West');
  const [activeAddress, setActiveAddress] = useState<string>('Midtown West');
  const [mapReady, setMapReady] = useState(false);
  const [mapCenter, setMapCenter] = useState<Coordinates | null>(null);
  const [destinationCenter, setDestinationCenter] = useState<Coordinates | null>(null);
  const [isNearbyRefreshing, setIsNearbyRefreshing] = useState(false);

  const mapRef = useRef<MapView | null>(null);
  const carouselRef = useRef<FlatList<POI>>(null);
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const slideAnim = useRef(new Animated.Value(20)).current;
  const listOpacity = useRef(new Animated.Value(1)).current;

  const viewabilityConfig = useRef({ viewAreaCoveragePercentThreshold: 65 });
  const onViewableItemsChanged = useRef(({ viewableItems }: { viewableItems: ViewToken[] }) => {
    if (!viewableItems || viewableItems.length === 0) {
      return;
    }
    const poi = viewableItems[0].item as POI;
    if (poi && poi._id !== selectedPoiId) {
      setSelectedPoiId(poi._id);
      focusOnPoi(poi);
    }
  });

  const timeLabel = useMemo(() => formatTimeLabel(timeOfDay), [timeOfDay]);
  const currentNeighborhood = useMemo(() => {
    if (!activeNeighborhood) return 'Discover NYC';
    return activeNeighborhood;
  }, [activeNeighborhood]);

  const contextLabel = useMemo(() => {
    const displayLabel = activeAddress || activeNeighborhood || 'NYC';
    return location ? `Near ${displayLabel}` : displayLabel;
  }, [location, activeAddress, activeNeighborhood]);

  const isMapNearUser = useMemo(() => {
    if (!location || !mapCenter) {
      return !location;
    }
    return locationService.calculateDistance(location, mapCenter) < 200; // ~0.12 miles
  }, [location, mapCenter]);

  const showSearchNearby = Boolean(location && mapCenter && !isMapNearUser);

  useEffect(() => {
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 400,
        useNativeDriver: true,
      }),
      Animated.timing(slideAnim, {
        toValue: 0,
        duration: 400,
        useNativeDriver: true,
      }),
    ]).start();

    initializeLocation();
  }, []);

  useEffect(() => {
    if (!location) return;
    setActiveCenter(location);
    (async () => {
      const label = await locationService.getAddress(location);
      setActiveNeighborhood(resolveNeighborhoodName(location, label));
      setActiveAddress(formatFriendlyAddress(label));
      setDestinationCenter(location);
    })();
  }, [location]);

  useEffect(() => {
    if (activeCenter) {
      setMapCenter(activeCenter);
    }
  }, [activeCenter]);

  useEffect(() => {
    if (activeCenter) {
      loadPOIs(activeCenter);
    }
  }, [activeCenter, filter, timeOfDay]);

  useEffect(() => {
    if (mapRef.current && viewMode === 'map' && activeCenter) {
      mapRef.current.animateToRegion({
        latitude: activeCenter.latitude,
        longitude: activeCenter.longitude,
        latitudeDelta: 0.014, // ~1 mile diameter
        longitudeDelta: 0.014,
      });
    }
  }, [activeCenter, viewMode]);

  useEffect(() => {
    if (viewMode === 'map' && selectedPoiId && mapReady) {
      const match = pois.find((poi) => poi._id === selectedPoiId);
      if (match) {
        focusOnPoi(match);
      }
    }
  }, [viewMode, mapReady, selectedPoiId, pois]);

  useEffect(() => {
    if (pois.length === 0) {
      setSelectedPoiId(null);
      return;
    }
    const exists = pois.some((poi) => poi._id === selectedPoiId);
    if (!exists) {
      setSelectedPoiId(pois[0]._id);
    }
  }, [pois, selectedPoiId]);

  const initializeLocation = async () => {
    console.log('🗺️  [Discover] Initializing location...');
    const loc = await locationService.getCurrentLocation();
    if (loc) {
      console.log('   ✅ Location obtained:', loc.coords);
      setLocation(loc.coords);
      setActiveCenter(loc.coords);
      const label = await locationService.getAddress(loc.coords);
      console.log('   📍 Address:', label);
      setActiveNeighborhood(resolveNeighborhoodName(loc.coords, label));
      setActiveAddress(formatFriendlyAddress(label));
      setDestinationCenter(loc.coords);
    } else {
      console.log('   ⚠️  Location unavailable, using default center');
      setLocation(null);
      setActiveCenter(DEFAULT_CENTER);
      setActiveNeighborhood('Midtown West');
      setActiveAddress('Midtown West');
      setStatusMessage('Using Midtown Manhattan while we find your GPS fix.');
      setIsLoading(false);
    }
  };

  const loadPOIs = async (center: Coordinates) => {
    if (!center) return;

    console.log('📥 [Discover] Loading POIs...');
    console.log('   Center:', center);
    console.log('   Filter:', filter);
    console.log('   Time of day:', timeOfDay);

    Animated.timing(listOpacity, {
      toValue: 0.3,
      duration: 300,
      useNativeDriver: true,
    }).start();

    setIsLoading(true);
    try {
      setStatusMessage(null);
      let params: any = {
        location: center,
        radius: 5000,
        limit: 50, // Query more, but we'll filter to top 10
        time_of_day: timeOfDay,
      };

      switch (filter) {
        case 'michelin':
          params.min_prestige = 50;
          break;
        case 'fine-dining':
          params.category = 'fine-dining';
          break;
        case 'casual':
          params.category = 'casual-dining';
          break;
        // Time-based subcategory filters
        case 'breakfast':
        case 'coffee':
        case 'brunch':
          params.subcategory = filter;
          break;
        case 'bars':
        case 'late-night':
          params.category = 'bars-cocktails';
          break;
        case 'quick-bites':
          params.category = 'casual-dining';
          break;
      }

      console.log('   🔎 Query params:', JSON.stringify(params, null, 2));
      console.log('   ⏱️  Calling mcpService.queryPOIs...');
      const startTime = Date.now();

      const results = await mcpService.queryPOIs(params);

      const duration = Date.now() - startTime;
      console.log(`   ✅ Results received in ${duration}ms`);
      console.log(`   📊 POI count: ${results.length}`);

      const referencePoint = center;

      // Hydrate with distance and filter out invalid coordinates
      const hydrated = results
        .map((poi) => {
          try {
            const coords = getPoiCoordinates(poi);

            // Validate coordinates
            if (!coords ||
              typeof coords.latitude !== 'number' ||
              typeof coords.longitude !== 'number' ||
              isNaN(coords.latitude) ||
              isNaN(coords.longitude) ||
              coords.latitude < -90 || coords.latitude > 90 ||
              coords.longitude < -180 || coords.longitude > 180) {
              console.warn(`   ⚠️  Invalid coordinates for POI: ${poi.name}`);
              return null;
            }

            const distance = referencePoint
              ? locationService.calculateDistance(referencePoint, coords)
              : undefined;
            return {
              ...poi,
              distance,
              distance_formatted: distance ? locationService.formatDistance(distance) : undefined,
            };
          } catch (err) {
            console.error(`   ❌ Error processing POI ${poi.name}:`, err);
            return null;
          }
        })
        .filter((poi): poi is NonNullable<typeof poi> => poi !== null);

      // Sort by prestige score first, then distance
      hydrated.sort((a, b) => {
        const scoreA = a.prestige?.score || 0;
        const scoreB = b.prestige?.score || 0;

        if (scoreA !== scoreB) {
          return scoreB - scoreA; // Higher prestige first
        }

        if (a.distance !== undefined && b.distance !== undefined) {
          return a.distance - b.distance; // Closer first
        }
        return 0;
      });

      // Limit to top 10 for map and carousel
      const top10 = hydrated.slice(0, 10);
      console.log(`   📍 Showing top ${top10.length} POIs on map`);

      console.log('   ✨ POIs hydrated and sorted');

      LayoutAnimation.configureNext(LayoutAnimation.Presets.easeInEaseOut);
      setPois(top10);
      if (!selectedPoiId && top10.length > 0) {
        setSelectedPoiId(top10[0]._id);
      }
      setTimeout(() => {
        setIsLoading(false);
        Animated.timing(listOpacity, {
          toValue: 1,
          duration: 500,
          useNativeDriver: true,
        }).start();
        console.log('   🎉 POIs loaded and displayed');
      }, 200);
    } catch (error) {
      const err = error as Error;
      console.error('❌ [Discover] Error loading POIs:', err);
      console.error('   Message:', err.message);
      console.error('   Stack:', err.stack);
      setPois([]);
      setStatusMessage('Unable to reach the concierge API. Showing no results.');
      setIsLoading(false);
    }
  };

  const handleRefresh = () => {
    loadPOIs(activeCenter);
  };

  const handleSearchNearby = async () => {
    setIsNearbyRefreshing(true);
    try {
      // If user has panned away (button visible), anchor to the map center
      if (showSearchNearby && mapCenter) {
        setActiveCenter(mapCenter);
        setDestinationCenter(mapCenter);
        const label = await locationService.getAddress(mapCenter);
        setActiveNeighborhood(resolveNeighborhoodName(mapCenter, label));
        setActiveAddress(formatFriendlyAddress(label));
        setStatusMessage('Exploring this area.');
      } else {
        const current = await locationService.getCurrentLocation();
        if (current?.coords) {
          setLocation(current.coords);
          setActiveCenter(current.coords);
          setDestinationCenter(current.coords);
          const label = await locationService.getAddress(current.coords);
          setActiveNeighborhood(resolveNeighborhoodName(current.coords, label));
          setActiveAddress(formatFriendlyAddress(label));
          setDestinationCenter(current.coords);
          setStatusMessage('Updated to your current location.');
        } else if (location) {
          setActiveCenter(location);
          const label = await locationService.getAddress(location);
          setActiveNeighborhood(resolveNeighborhoodName(location, label));
          setActiveAddress(formatFriendlyAddress(label));
          setDestinationCenter(location);
          setStatusMessage('Using your last known location.');
        } else {
          setActiveCenter(DEFAULT_CENTER);
          setActiveNeighborhood('Midtown West');
          setActiveAddress('Midtown West');
          setDestinationCenter(DEFAULT_CENTER);
          setStatusMessage('Still using Midtown fallback while GPS is unavailable.');
        }
      }
    } finally {
      setIsNearbyRefreshing(false);
    }
  };

  const focusOnPoi = useCallback((poi: POI) => {
    if (!mapRef.current) return;
    const poiCoords = getPoiCoordinates(poi);
    const points: Coordinates[] = [poiCoords];

    if (location) {
      points.push(location);
    }
    if (points.length === 1) {
      mapRef.current.animateToRegion({
        latitude: poiCoords.latitude,
        longitude: poiCoords.longitude,
        latitudeDelta: 0.02,
        longitudeDelta: 0.02,
      });
      return;
    }

    mapRef.current.fitToCoordinates(points, {
      edgePadding: { top: 160, right: 80, bottom: 300, left: 80 },
      animated: true,
    });
  }, [location]);

  const handleMarkerPress = useCallback((poi: POI) => {
    setSelectedPoiId(poi._id);
    focusOnPoi(poi);
    const index = pois.findIndex((item) => item._id === poi._id);
    if (index >= 0) {
      try {
        carouselRef.current?.scrollToIndex({ index, animated: true });
      } catch (error) {
        console.warn('Unable to scroll carousel:', error);
      }
    }
  }, [pois, focusOnPoi]);

  const handleCarouselPress = useCallback((poi: POI) => {
    setSelectedPoiId(poi._id);
    focusOnPoi(poi);
  }, [focusOnPoi]);

  const handleRefreshPOI = useCallback((poi: POI) => {
    // Navigate to Chat tab with POI for refresh
    router.push({
      pathname: '/two',
      params: {
        poiId: poi._id,
        poiName: poi.name,
        action: 'refresh',
      },
    });
  }, []);

  const renderMapView = () => (
    <View style={styles.mapWrapper}>
      <MapView
        ref={(ref) => (mapRef.current = ref)}
        style={StyleSheet.absoluteFill}
        provider={PROVIDER_DEFAULT}
        initialRegion={{
          latitude: activeCenter.latitude,
          longitude: activeCenter.longitude,
          latitudeDelta: 0.015, // Approx 0.5mi radius
          longitudeDelta: 0.015,
        }}
        showsUserLocation={true}
        showsMyLocationButton={false}
        showsCompass={true}
        customMapStyle={MAP_STYLE}
        onMapReady={() => setMapReady(true)}
        onRegionChangeComplete={(region) => {
          setMapCenter({
            latitude: region.latitude,
            longitude: region.longitude,
          });
        }}
      >
        {showSearchNearby && mapCenter && (
          <>
            <Circle
              center={mapCenter}
              radius={150}
              strokeColor="rgba(255, 193, 7, 0.9)"
              fillColor="rgba(255, 193, 7, 0.2)"
            />
            <Circle
              center={mapCenter}
              radius={300}
              strokeColor="rgba(255, 193, 7, 0.7)"
              fillColor="rgba(255, 193, 7, 0.12)"
            />
            <Circle
              center={mapCenter}
              radius={450}
              strokeColor="rgba(255, 193, 7, 0.4)"
              fillColor="rgba(255, 193, 7, 0.05)"
            />
          </>
        )}
        {destinationCenter && (
          <Marker
            coordinate={destinationCenter}
            title="Destination"
            description={activeAddress}
            pinColor="#FFC107"
          />
        )}
        {pois
          .filter((poi) => {
            // Only render markers with valid coordinates
            try {
              const coords = getPoiCoordinates(poi);
              return (
                coords &&
                typeof coords.latitude === 'number' &&
                typeof coords.longitude === 'number' &&
                !isNaN(coords.latitude) &&
                !isNaN(coords.longitude) &&
                coords.latitude >= -90 &&
                coords.latitude <= 90 &&
                coords.longitude >= -180 &&
                coords.longitude <= 180
              );
            } catch {
              return false;
            }
          })
          .map((poi, index) => {
            try {
              const coords = getPoiCoordinates(poi);
              const isSelected = poi._id === selectedPoiId;
              const logo = poi.media?.logo_url;
              const michelinStars = poi.prestige?.michelin_stars || 0;
              const prestigeScore = poi.prestige?.score || 0;

              // Prestige-based color
              let markerColor = '#6B7280'; // Gray for low prestige
              if (prestigeScore >= 100) markerColor = '#FFD700'; // Gold for 3-star
              else if (prestigeScore >= 50) markerColor = '#F59E0B'; // Amber for Michelin
              else if (prestigeScore >= 25) markerColor = '#3B82F6'; // Blue for prestigious

              return (
                <Marker
                  key={`marker-${poi._id}`}
                  coordinate={coords}
                  title={poi.name}
                  onPress={() => handleMarkerPress(poi)}
                  zIndex={isSelected ? 1000 : (10 - index)}
                >
                  <View style={[
                    styles.markerBubbleSimple,
                    isSelected && styles.markerBubbleSimpleActive,
                    { borderColor: markerColor }
                  ]}>
                    {logo ? (
                      <Image source={{ uri: logo }} style={styles.markerLogoSimple} />
                    ) : (
                      <View style={[styles.markerFallbackSimple, { backgroundColor: markerColor }]}>
                        <Text style={styles.markerFallbackTextSimple}>{poi.name.charAt(0)}</Text>
                      </View>
                    )}
                    {michelinStars > 0 && (
                      <View style={styles.markerStarBadgeSimple}>
                        <Text style={styles.markerStarTextSimple}>
                          {'⭐'.repeat(Math.min(michelinStars, 3))}
                        </Text>
                      </View>
                    )}
                  </View>
                </Marker>
              );
            } catch (err) {
              console.error(`❌ [Render] Error rendering marker for ${poi.name}:`, err);
              console.error(`   Stack:`, err.stack);
              return null;
            }
          })
          .filter((marker): marker is React.ReactElement => marker !== null)
        }
      </MapView>

      <View style={styles.mapOverlay} pointerEvents="box-none">
        {showSearchNearby && (
          <TouchableOpacity
            style={styles.searchNearbyButton}
            onPress={handleSearchNearby}
            disabled={isNearbyRefreshing}
          >
            {isNearbyRefreshing ? (
              <ActivityIndicator size="small" color="#0a0a1e" />
            ) : (
              <Text style={styles.searchNearbyText}>📍 Search Nearby</Text>
            )}
          </TouchableOpacity>
        )}
        {showSearchNearby && (
          <View pointerEvents="none" style={styles.crosshairOverlay}>
            <View style={styles.crosshairHorizontal} />
            <View style={styles.crosshairVertical} />
          </View>
        )}
      </View>

      {isLoading && (
        <View style={[StyleSheet.absoluteFill, styles.mapLoadingOverlay]}>
          <ActivityIndicator size="large" color="#FFC107" />
        </View>
      )}

      <View style={styles.carouselContainer}>
        {pois.length > 0 ? (
          <FlatList
            ref={carouselRef}
            data={pois}
            horizontal
            showsHorizontalScrollIndicator={false}
            snapToAlignment="center"
            decelerationRate="fast"
            snapToInterval={SCREEN_WIDTH * 0.8 + 16}
            keyExtractor={(item) => item._id}
            renderItem={({ item }) => (
              <TouchableOpacity
                style={[styles.carouselCard, item._id === selectedPoiId && styles.carouselCardActive]}
                onPress={() => handleCarouselPress(item)}
                activeOpacity={0.85}
              >
                <View style={styles.carouselHeader}>
                  {item.media?.logo_url ? (
                    <Image source={{ uri: item.media.logo_url }} style={styles.carouselLogo} />
                  ) : (
                    <View style={styles.carouselLogoFallback}>
                      <Text style={styles.carouselLogoFallbackText}>{item.name.charAt(0)}</Text>
                    </View>
                  )}
                  <View style={{ flex: 1 }}>
                    <Text style={styles.carouselName} numberOfLines={1}>{item.name}</Text>
                    <Text style={styles.carouselNeighborhood} numberOfLines={1}>
                      {item.address.street.replace(/, New York,? NY\.?$/, '').trim()}
                    </Text>
                  </View>
                  {item.distance_formatted && (
                    <Text style={styles.carouselDistance}>{item.distance_formatted}</Text>
                  )}
                </View>
                <Text style={styles.carouselMeta} numberOfLines={1}>
                  {item.experience.price_range} · {item.subcategories.join(', ') || item.category}
                </Text>

                {/* Refresh Button */}
                {/* Ask AI Button */}
                <TouchableOpacity
                  style={styles.askAiButton}
                  onPress={(e) => {
                    e.stopPropagation();
                    handleRefreshPOI(item);
                  }}
                  activeOpacity={0.7}
                >
                  <Text style={styles.askAiText}>✨ Ask AI</Text>
                </TouchableOpacity>
              </TouchableOpacity>
            )}
            contentContainerStyle={styles.carouselContent}
            onViewableItemsChanged={onViewableItemsChanged.current}
            viewabilityConfig={viewabilityConfig.current}
            // Performance optimizations
            removeClippedSubviews={true}
            maxToRenderPerBatch={3}
            windowSize={5}
            initialNumToRender={3}
            getItemLayout={(data, index) => ({
              length: SCREEN_WIDTH * 0.8 + 16,
              offset: (SCREEN_WIDTH * 0.8 + 16) * index,
              index,
            })}
          />
        ) : isLoading ? (
          <ScrollView
            horizontal
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={styles.carouselContent}
          >
            {CAROUSEL_PLACEHOLDERS.map((item) => (
              <View key={item} style={styles.carouselSkeletonCard}>
                <View style={styles.carouselSkeletonHeader}>
                  <View style={styles.carouselSkeletonAvatar} />
                  <View style={{ flex: 1 }}>
                    <View style={styles.carouselSkeletonLine} />
                    <View style={[styles.carouselSkeletonLine, { width: '60%', marginTop: 6 }]} />
                  </View>
                </View>
                <View style={[styles.carouselSkeletonLine, { width: '80%' }]} />
              </View>
            ))}
          </ScrollView>
        ) : (
          <View style={styles.carouselEmptyState}>
            <Text style={styles.carouselEmptyTitle}>No prestige hits here yet</Text>
            <Text style={styles.carouselEmptyText}>Try refresh or adjust filters.</Text>
          </View>
        )}
      </View>
    </View>
  );

  const renderListView = () => (
    <View style={{ flex: 1 }}>
      <Animated.FlatList
        data={pois}
        renderItem={({ item }) => <POICard poi={item} />}
        keyExtractor={(item) => item._id}
        contentContainerStyle={styles.listContent}
        showsVerticalScrollIndicator={false}
        style={{ opacity: listOpacity }}
      />

      {isLoading && (
        <View style={[StyleSheet.absoluteFill, styles.centerContainer, { backgroundColor: 'rgba(10, 10, 30, 0.8)' }]}>
          <ActivityIndicator size="large" color="#4a90e2" />
          <Text style={styles.loadingText}>Updating...</Text>
        </View>
      )}

      {!isLoading && pois.length === 0 && (
        <View style={styles.centerContainer}>
          <Text style={styles.emptyText}>No restaurants found</Text>
          <Text style={styles.emptySubtext}>Try changing your filter</Text>
          <TouchableOpacity style={styles.retryButton} onPress={handleRefresh}>
            <Text style={styles.retryButtonText}>🔄 Retry</Text>
          </TouchableOpacity>
        </View>
      )}
    </View>
  );

  if (!activeCenter) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#4a90e2" />
        <Text style={styles.loadingText}>Preparing map...</Text>
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <Animated.View
        style={[
          { flex: 1 },
          {
            opacity: fadeAnim,
            transform: [{ translateY: slideAnim }],
          },
        ]}
      >
        <View style={styles.header}>
          <View style={{ flex: 1 }}>
            <Text style={styles.headerTitle}>{currentNeighborhood || 'Discover'}</Text>
            <View style={{ flexDirection: 'row', alignItems: 'center' }}>
              <Text style={styles.headerSubtitle}>{contextLabel}</Text>
              <Text style={[styles.headerSubtitle, { marginHorizontal: 6 }]}> • </Text>
              <TouchableOpacity onPress={() => setTimeDropdownVisible((prev) => !prev)}>
                <Text style={[styles.headerSubtitle, styles.timeClickable]}>
                  {timeLabel} {timeDropdownVisible ? '▲' : '▼'}
                </Text>
              </TouchableOpacity>
            </View>
            {statusMessage && (
              <Text style={styles.statusText}>{statusMessage}</Text>
            )}
          </View>
        </View>



        {timeDropdownVisible && (
          <View style={styles.timeDropdownHeader}>
            {TIME_OPTIONS.map((option) => (
              <TouchableOpacity
                key={option.value}
                style={[
                  styles.timeDropdownItemHeader,
                  timeOfDay === option.value && styles.timeDropdownItemActive
                ]}
                onPress={() => {
                  setTimeOfDay(option.value);
                  setTimeDropdownVisible(false);
                  setStatusMessage(`Dialed into ${option.label.toLowerCase()} vibes.`);
                }}
              >
                <Text style={[
                  styles.timeDropdownTextHeader,
                  timeOfDay === option.value && styles.timeDropdownTextActive
                ]}>
                  {option.label}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        )}

        <View style={styles.filterBar}>
          <ScrollView
            horizontal
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={styles.filterContent}
          >
            {TIME_BASED_FILTERS[timeOfDay as keyof typeof TIME_BASED_FILTERS].map((filterOption) => (
              <TouchableOpacity
                key={filterOption.value}
                style={[styles.filterButton, filter === filterOption.value && styles.filterButtonActive]}
                onPress={() => setFilter(filterOption.value as any)}
              >
                <Text style={[styles.filterText, filter === filterOption.value && styles.filterTextActive]}>
                  {filterOption.emoji} {filterOption.label}
                </Text>
              </TouchableOpacity>
            ))}
          </ScrollView>
        </View>

        <View style={{ flex: 1 }}>
          {viewMode === 'map' ? renderMapView() : renderListView()}
        </View>
      </Animated.View>
    </SafeAreaView>
  );
}

const MAP_STYLE = [
  {
    elementType: 'geometry',
    stylers: [{ color: '#1d2c4d' }],
  },
  {
    elementType: 'labels.text.fill',
    stylers: [{ color: '#8ec3b9' }],
  },
  {
    elementType: 'labels.text.stroke',
    stylers: [{ color: '#1a3646' }],
  },
];

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0a0a1e',
  },
  header: {
    backgroundColor: 'transparent',
    paddingTop: IS_SMALL_DEVICE ? 12 : 16,
    paddingBottom: IS_SMALL_DEVICE ? 12 : 16,
    paddingHorizontal: IS_SMALL_DEVICE ? 16 : 20,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255, 255, 255, 0.1)',
    flexDirection: 'row',
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: IS_SMALL_DEVICE ? 20 : IS_LARGE_DEVICE ? 28 : 24,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 4,
    textShadowColor: 'rgba(255, 193, 7, 0.3)',
    textShadowOffset: { width: 0, height: 0 },
    textShadowRadius: 10,
  },
  headerSubtitle: {
    fontSize: IS_SMALL_DEVICE ? 11 : 13,
    color: 'rgba(255, 255, 255, 0.7)',
  },
  statusText: {
    marginTop: 4,
    fontSize: 12,
    color: '#FFC107',
  },
  viewToggleButton: {
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 12,
    backgroundColor: 'rgba(255, 193, 7, 0.2)',
    borderWidth: 1,
    borderColor: 'rgba(255, 193, 7, 0.5)',
  },
  viewToggleButtonText: {
    color: '#FFC107',
    fontWeight: '600',
  },
  timeClickable: {
    color: '#FFC107',
    textDecorationLine: 'underline',
  },
  timeDropdownHeader: {
    backgroundColor: 'rgba(10, 10, 30, 0.85)', // Unified dark glass
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255, 193, 7, 0.3)',
    flexDirection: 'row',
    paddingHorizontal: 16,
    paddingVertical: 8,
  },
  timeDropdownItemHeader: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    marginRight: 8,
  },
  timeDropdownItemActive: {
    backgroundColor: 'rgba(255, 193, 7, 0.2)',
  },
  timeDropdownTextHeader: {
    color: 'rgba(255, 255, 255, 0.7)',
    fontSize: 13,
    fontWeight: '600',
  },
  timeDropdownTextActive: {
    color: '#FFC107',
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'transparent',
  },
  loadingText: {
    marginTop: 12,
    fontSize: 16,
    color: 'rgba(255, 255, 255, 0.7)',
  },
  emptyText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#ffffff',
    marginBottom: 8,
  },
  emptySubtext: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.5)',
    marginBottom: 20,
  },
  retryButton: {
    paddingHorizontal: 24,
    paddingVertical: 12,
    backgroundColor: '#4a90e2',
    borderRadius: 20,
  },
  retryButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
  filterBar: {
    backgroundColor: 'rgba(10, 10, 30, 0.85)', // Unified dark glass
    paddingVertical: 14,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255, 255, 255, 0.05)',
  },
  filterContent: {
    paddingHorizontal: 16,
    gap: 6, // Tightened from 8
  },
  filterButton: {
    paddingHorizontal: 18,
    paddingVertical: 10,
    borderRadius: 18,
    backgroundColor: 'rgba(255, 255, 255, 0.05)', // Subtle glass
    marginRight: 6, // Tightened from 10
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.15)',
  },
  filterButtonActive: {
    backgroundColor: 'rgba(255, 193, 7, 0.25)',
    borderColor: 'rgba(255, 193, 7, 0.4)',
    shadowColor: '#FFC107',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
  },
  filterText: {
    fontSize: 14,
    fontWeight: '600',
    color: 'rgba(255, 255, 255, 0.6)',
  },
  filterTextActive: {
    color: '#FFC107',
  },
  timeFilterButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  timeFilterText: {
    color: '#ffffff',
  },
  refreshButton: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: '#f0f0f0',
  },
  refreshText: {
    fontSize: 16,
  },
  timeDropdown: {
    marginTop: 12,
    marginHorizontal: 16,
    padding: 12,
    borderRadius: 14,
    backgroundColor: 'rgba(10, 10, 30, 0.95)',
    borderWidth: 1,
    borderColor: 'rgba(255, 193, 7, 0.3)',
  },
  timeDropdownItem: {
    paddingVertical: 8,
  },
  timeDropdownText: {
    color: '#ffffff',
    fontSize: 15,
  },
  mapWrapper: {
    flex: 1,
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    overflow: 'hidden',
    backgroundColor: '#000',
  },
  mapOverlay: {
    position: 'absolute',
    top: 20,
    left: 20,
    right: 20,
    zIndex: 10,
    alignItems: 'center',
  },
  searchNearbyButton: {
    alignSelf: 'center',
    backgroundColor: '#FFC107',
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 18,
    shadowColor: '#FFC107',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.35,
    shadowRadius: 8,
    borderWidth: 1,
    borderColor: 'rgba(0, 0, 0, 0.2)',
  },
  searchNearbyText: {
    color: '#0a0a1e',
    fontWeight: '700',
  },
  mapLoadingOverlay: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  markerBubble: {
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 12,
    backgroundColor: 'rgba(10, 10, 30, 0.85)',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.3)',
    alignItems: 'center',
  },
  markerBubbleActive: {
    borderColor: '#FFC107',
    backgroundColor: 'rgba(255, 193, 7, 0.15)',
  },
  markerLogo: {
    width: 36,
    height: 36,
    borderRadius: 18,
    marginBottom: 4,
  },
  markerFallback: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: '#FFC107',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 4,
  },
  markerFallbackText: {
    color: '#0a0a1e',
    fontWeight: '700',
  },
  markerLabel: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: '600',
    maxWidth: 160,
    textAlign: 'center',
  },
  markerLabelActive: {
    color: '#FFC107',
    fontWeight: '700',
  },
  markerLabelContainer: {
    alignItems: 'center',
    gap: 2,
  },
  markerStarBadge: {
    position: 'absolute',
    top: -8,
    right: -8,
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
    borderRadius: 12,
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderWidth: 1,
    borderColor: '#FFD700',
  },
  markerStarText: {
    fontSize: 10,
    lineHeight: 12,
  },
  markerDistance: {
    color: 'rgba(255, 255, 255, 0.7)',
    fontSize: 10,
    fontWeight: '500',
  },
  // Simplified markers (logo only)
  markerBubbleSimple: {
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
  markerBubbleSimpleActive: {
    borderWidth: 5,
    borderColor: '#FFC107',
    backgroundColor: 'rgba(255, 193, 7, 0.3)',
    shadowColor: '#FFC107',
    shadowOpacity: 0.8,
    shadowRadius: 12,
    shadowOffset: { width: 0, height: 0 },
    transform: [{ scale: 1.3 }],
  },
  markerLogoSimple: {
    width: 40,
    height: 40,
    borderRadius: 20,
  },
  markerFallbackSimple: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  markerFallbackTextSimple: {
    color: '#ffffff',
    fontWeight: '800',
    fontSize: 18,
  },
  markerStarBadgeSimple: {
    position: 'absolute',
    top: -6,
    right: -6,
    backgroundColor: 'rgba(0, 0, 0, 0.9)',
    borderRadius: 10,
    paddingHorizontal: 4,
    paddingVertical: 2,
    borderWidth: 1.5,
    borderColor: '#FFD700',
  },
  markerStarTextSimple: {
    fontSize: 9,
    lineHeight: 10,
  },
  crosshairOverlay: {
    ...StyleSheet.absoluteFillObject,
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 20,
  },
  crosshairHorizontal: {
    width: 24,
    height: 1.2,
    backgroundColor: 'rgba(255, 193, 7, 0.9)',
  },
  crosshairVertical: {
    width: 1.2,
    height: 24,
    backgroundColor: 'rgba(255, 193, 7, 0.9)',
  },
  carouselContainer: {
    position: 'absolute',
    bottom: 80, // Above tab bar
    width: '100%',
  },
  carouselContent: {
    paddingHorizontal: 16,
    paddingBottom: 8,
  },
  carouselCard: {
    width: SCREEN_WIDTH * 0.8,
    marginRight: 16,
    borderRadius: 18,
    backgroundColor: 'rgba(10, 10, 30, 0.85)', // Unified dark glass
    padding: 16,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)',
  },
  carouselCardActive: {
    borderColor: '#FFC107',
    shadowColor: '#FFC107',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.35,
    shadowRadius: 12,
  },
  askAiButton: {
    position: 'absolute',
    bottom: 12,
    right: 12,
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
    backgroundColor: '#FFC107',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#FFC107',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
  },
  askAiText: {
    fontSize: 12,
    fontWeight: '700',
    color: '#0a0a1e',
  },
  refreshButton: {
    position: 'absolute',
    bottom: 12,
    right: 12,
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: 'rgba(255, 193, 7, 0.9)',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
  },
  refreshIcon: {
    fontSize: 18,
  },
  carouselHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
    gap: 10,
  },
  carouselLogo: {
    width: 44,
    height: 44,
    borderRadius: 22,
  },
  carouselLogoFallback: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#FFC107',
    justifyContent: 'center',
    alignItems: 'center',
  },
  carouselLogoFallbackText: {
    color: '#0a0a1e',
    fontWeight: '700',
    fontSize: 18,
  },
  carouselName: {
    fontSize: 18,
    fontWeight: '700',
    color: '#ffffff',
  },
  carouselNeighborhood: {
    fontSize: 13,
    color: 'rgba(255, 255, 255, 0.6)',
  },
  carouselDistance: {
    color: '#FFC107',
    fontWeight: '600',
  },
  carouselMeta: {
    fontSize: 13,
    color: 'rgba(255, 255, 255, 0.8)',
  },
  carouselSkeletonCard: {
    width: SCREEN_WIDTH * 0.8,
    marginRight: 16,
    borderRadius: 18,
    padding: 16,
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.08)',
  },
  carouselSkeletonHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    marginBottom: 10,
  },
  carouselSkeletonAvatar: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: 'rgba(255, 255, 255, 0.12)',
  },
  carouselSkeletonLine: {
    height: 10,
    borderRadius: 5,
    backgroundColor: 'rgba(255, 255, 255, 0.12)',
    marginBottom: 8,
  },
  carouselEmptyState: {
    paddingHorizontal: 24,
    paddingVertical: 20,
    alignItems: 'center',
    justifyContent: 'center',
  },
  carouselEmptyTitle: {
    color: '#ffffff',
    fontWeight: '700',
    marginBottom: 6,
  },
  carouselEmptyText: {
    color: 'rgba(255, 255, 255, 0.7)',
    fontSize: 13,
  },
  listContent: {
    paddingBottom: Platform.OS === 'ios' ? 100 : 80,
  },
});
