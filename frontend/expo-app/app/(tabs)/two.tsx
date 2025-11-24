/**
 * Chat Screen - Main conversational interface
 */

import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TextInput,
  TouchableOpacity,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  Dimensions,
  Animated,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useLocalSearchParams } from 'expo-router';
import Markdown from 'react-native-markdown-display';
import { locationService, Coordinates } from '../../services/locationService';
import { weatherService, WeatherData } from '../../services/weatherService';
import { mcpService, POI, ChatMessage } from '../../services/mcpService';
import { POICard } from '../../components/POICard';

const { width: SCREEN_WIDTH } = Dimensions.get('window');
const IS_SMALL_DEVICE = SCREEN_WIDTH < 375; // iPhone SE
const IS_LARGE_DEVICE = SCREEN_WIDTH >= 428; // iPhone Pro Max

export default function ChatScreen() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [location, setLocation] = useState<Coordinates | null>(null);
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const scrollViewRef = useRef<ScrollView>(null);
  const params = useLocalSearchParams();

  // Animation values
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const slideAnim = useRef(new Animated.Value(20)).current;
  const hasTriggeredRefresh = useRef(false);

  // Handle POI refresh from Discover screen
  useEffect(() => {
    console.log('🔔 Params changed:', params);
    if (params.action === 'refresh' && params.poiId && params.poiName && !hasTriggeredRefresh.current) {
      console.log('🔄 Triggering POI refresh for:', params.poiName);
      hasTriggeredRefresh.current = true;
      handlePOIRefresh(params.poiId as string, params.poiName as string);

      // Reset after a delay to allow future refreshes
      setTimeout(() => {
        hasTriggeredRefresh.current = false;
      }, 2000);
    }
  }, [params.action, params.poiId, params.poiName]);

  useEffect(() => {
    // Fade in and slide up on mount
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

    loadInitialData();
    addWelcomeMessage();
  }, []);

  const loadInitialData = async () => {
    const loc = await locationService.getCurrentLocation();
    if (loc) {
      setLocation(loc.coords);
      const w = await weatherService.getCurrentWeather(loc.coords);
      if (w) {
        setWeather(w);
      }
    }
  };

  const addWelcomeMessage = () => {
    const welcomeMsg: ChatMessage = {
      role: 'assistant',
      content: "👋 Hi! I'm your NYC concierge. I can help you discover amazing dining experiences, especially Michelin-starred restaurants and award-winning establishments.\n\nTry asking me:\n• \"Find Michelin restaurants near me\"\n• \"Best place for a date night\"\n• \"Where should I eat right now?\"",
      timestamp: Date.now(),
    };
    setMessages([welcomeMsg]);
  };

  const handlePOIRefresh = async (poiId: string, poiName: string) => {
    setIsLoading(true);

    try {
      // For demo: ALWAYS fetch fresh data from Tavily to show the magic!
      const refreshingMsg: ChatMessage = {
        role: 'assistant',
        content: `🔄 Refreshing **${poiName}**...\n\n🌐 Fetching latest information from the web:\n• Holiday hours\n• Special events & menus\n• Recent news\n• Social media buzz\n• Current availability\n• Latest recognition`,
        timestamp: Date.now(),
      };
      setMessages(prev => [...prev, refreshingMsg]);

      // ALWAYS force refresh to show Tavily magic
      const updated = await mcpService.refreshPOI(poiId, true);

      if (updated) {
        // Build rich message with Tavily enrichment data
        let content = `✅ **${poiName}** - Refreshed successfully!\n\n`;

        // Contact info
        content += `📞 **Phone:** ${updated.contact?.phone || 'Not available'}\n`;
        content += `🌐 **Website:** ${updated.contact?.website || 'Not available'}\n`;
        content += `📍 **Address:** ${updated.address?.street ? `${updated.address.street}, ${updated.address.city}` : 'Not available'}\n\n`;

        // Check for enrichment data (from Tavily)
        const enrichment = (updated as any).enrichment_data;

        if (enrichment) {
          // Holiday hours (THANKSGIVING SPECIAL!)
          if (enrichment.holiday_hours && enrichment.holiday_hours.trim()) {
            content += `🦃 **HOLIDAY HOURS:**\n${enrichment.holiday_hours}\n\n`;
          }

          // Special events/menus
          if (enrichment.special_events && enrichment.special_events.trim()) {
            content += `🍽️ **SPECIAL EVENTS:**\n${enrichment.special_events}\n\n`;
          }

          // Recent news
          if (enrichment.recent_news && enrichment.recent_news.trim()) {
            content += `📰 **RECENT NEWS:**\n${enrichment.recent_news}\n\n`;
          }

          // Social buzz
          if (enrichment.social_buzz && enrichment.social_buzz.trim()) {
            content += `📱 **TRENDING NOW:**\n${enrichment.social_buzz}\n\n`;
          }

          // Current availability
          if (enrichment.current_availability && enrichment.current_availability.trim()) {
            content += `🎫 **RESERVATIONS:**\n${enrichment.current_availability}\n\n`;
          }

          // Latest recognition
          if (enrichment.latest_recognition && enrichment.latest_recognition.trim()) {
            content += `🏆 **LATEST RECOGNITION:**\n${enrichment.latest_recognition}\n\n`;
          }
        } else {
          // No enrichment data - show basic hours message
          content += `🕒 **Hours:** Check website for current hours\n\n`;
        }

        content += `_✨ Fresh data from the web via Tavily • Saved to database!_`;

        const updatedMsg: ChatMessage = {
          role: 'assistant',
          content,
          timestamp: Date.now(),
        };
        setMessages(prev => [...prev, updatedMsg]);
      } else {
        const errorMsg: ChatMessage = {
          role: 'assistant',
          content: `❌ Sorry, I couldn't refresh the data for ${poiName}. Please try again later.`,
          timestamp: Date.now(),
        };
        setMessages(prev => [...prev, errorMsg]);
      }
    } catch (error) {
      console.error('Error refreshing POI:', error);
      const errorMsg: ChatMessage = {
        role: 'assistant',
        content: `❌ An error occurred while checking data. Please try again.`,
        timestamp: Date.now(),
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
      setTimeout(() => scrollViewRef.current?.scrollToEnd({ animated: true }), 100);
    }
  };


  const handleSend = useCallback(async () => {
    if (!inputText.trim()) return;

    const userText = inputText.trim();
    setInputText('');
    setIsLoading(true);

    try {
      const context: any = {};
      if (location) context.location = location;
      if (weather) {
        context.weather = `${weather.temperature}°F, ${weather.description}`;
        context.timeOfDay = getTimeOfDay();
      }

      await mcpService.chat(userText, context);
      setMessages(prev => [...prev, ...mcpService.getHistory().slice(-2)]);
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setIsLoading(false);
      setTimeout(() => scrollViewRef.current?.scrollToEnd({ animated: true }), 100);
    }
  }, [inputText, location, weather]);

  const handleQuickAction = async (action: 'nearby' | 'michelin' | 'recommend') => {
    if (!location) {
      alert('Please enable location services');
      return;
    }

    setIsLoading(true);
    try {
      let result: { pois: POI[]; explanation: string };
      const timeOfDay = getTimeOfDay();
      const weatherDesc = weather ? `${Math.round(weather.temperature)}°F and ${weather.description}` : 'nice weather';

      switch (action) {
        case 'nearby':
          const nearbyPOIs = await mcpService.queryPOIs({ location, radius: 2000, limit: 5 });
          const nearbyCount = nearbyPOIs.length;
          result = {
            pois: nearbyPOIs,
            explanation: `📍 **Nearby Top Picks** (within 1 mile)\n\nI found **${nearbyCount} exceptional ${nearbyCount === 1 ? 'restaurant' : 'restaurants'}** near you, ranked by prestige and proximity.\n\n${nearbyPOIs.slice(0, 3).map((p, i) =>
              `${i + 1}. **${p.name}**${p.prestige?.michelin_stars ? ` ⭐ ${p.prestige.michelin_stars} Michelin star${p.prestige.michelin_stars > 1 ? 's' : ''}` : ''}${p.experience?.price_range ? ` • ${p.experience.price_range}` : ''}`
            ).join('\n')}\n\nTap any card below to see full details and make a reservation!`
          };
          break;

        case 'michelin':
          const michelinPOIs = await mcpService.queryPOIs({
            location,
            radius: 5000,
            category: 'fine-dining',
            limit: 5
          });

          console.log('Michelin POIs:', michelinPOIs.length);
          michelinPOIs.forEach(p => console.log(`  - ${p.name}: ${p.prestige?.michelin_stars || 'no'} stars`));

          // Count stars (if any POIs have them)
          const withStars = michelinPOIs.filter(p => p.prestige?.michelin_stars && p.prestige.michelin_stars > 0);
          const totalStars = michelinPOIs.reduce((sum, p) => sum + (p.prestige?.michelin_stars || 0), 0);

          result = {
            pois: michelinPOIs,
            explanation: totalStars > 0
              ? `⭐ **Michelin Excellence**\n\nI've curated **${michelinPOIs.length} prestigious ${michelinPOIs.length === 1 ? 'establishment' : 'establishments'}** within 3 miles, featuring **${totalStars} Michelin stars** total.\n\n` +
              michelinPOIs.slice(0, 3).map((p, i) => {
                const stars = p.prestige?.michelin_stars || 0;
                const since = p.prestige?.michelin_since ? ` (since ${p.prestige.michelin_since})` : '';
                return `${i + 1}. **${p.name}**\n   ${stars > 0 ? `${'⭐'.repeat(stars)} ${stars}-star${stars > 1 ? 's' : ''}${since}` : 'Fine dining'}\n   ${p.address?.neighborhood || ''}`;
              }).join('\n\n') +
              `\n\nThese represent the pinnacle of NYC dining—perfect for special occasions!`
              : `⭐ **Fine Dining Excellence**\n\nI've curated **${michelinPOIs.length} exceptional fine dining ${michelinPOIs.length === 1 ? 'establishment' : 'establishments'}** within 3 miles.\n\n` +
              michelinPOIs.slice(0, 3).map((p, i) => {
                return `${i + 1}. **${p.name}**\n   ${p.experience?.price_range || ''} • ${p.address?.neighborhood || ''}`;
              }).join('\n\n') +
              `\n\nThese represent premium NYC dining experiences—perfect for special occasions!`
          };
          break;

        case 'recommend':
          result = await mcpService.getRecommendations({
            location,
            weather_condition: weather?.condition,
            time_of_day: timeOfDay,
            limit: 5,
          });

          // Enhance the recommendation explanation
          const occasion = timeOfDay === 'lunch' ? 'lunch' : timeOfDay === 'dinner' ? 'dinner' : 'dining';
          result.explanation = `✨ **Personalized Recommendations**\n\n` +
            `Based on it being **${timeOfDay}** with ${weatherDesc}, here are my top picks:\n\n` +
            result.pois.slice(0, 3).map((p, i) => {
              const highlights = [];
              if (p.prestige?.michelin_stars) highlights.push(`${p.prestige.michelin_stars}★ Michelin`);
              if (p.experience?.ambiance?.length) highlights.push(p.experience.ambiance[0]);

              // Contextual "Why"
              let contextNote = "Great choice right now.";
              if (weather && (weather.condition.toLowerCase().includes('rain') || weather.condition.toLowerCase().includes('drizzle'))) {
                contextNote = "Cozy spot to escape the rain ☔";
              } else if (timeOfDay === 'morning') {
                contextNote = "Perfect start to the day ☕";
              } else if (timeOfDay === 'lunch') {
                contextNote = "Ideal lunch spot 🍽️";
              } else if (timeOfDay === 'night') {
                contextNote = "Vibrant late-night vibe 🌙";
              } else if (p.prestige?.michelin_stars) {
                contextNote = "World-class culinary experience 🏆";
              } else if (p.best_for?.occasions?.length) {
                contextNote = `Perfect for ${p.best_for.occasions[0].replace(/-/g, ' ')} ✨`;
              }

              return `${i + 1}. **${p.name}**\n   _${contextNote}_\n   ${highlights.length > 0 ? highlights.join(' • ') : 'Highly rated'} • ${p.experience?.price_range || ''}`;
            }).join('\n\n') +
            `\n\nTap to explore these curated options!`;
          break;

        default:
          return;
      }

      const aiMsg: ChatMessage = {
        role: 'assistant',
        content: result.explanation,
        timestamp: Date.now(),
        pois: result.pois,
      };

      setMessages(prev => [...prev, aiMsg]);
      setTimeout(() => scrollViewRef.current?.scrollToEnd({ animated: true }), 100);
    } catch (error) {
      console.error('Error with quick action:', error);
      const errorMsg: ChatMessage = {
        role: 'assistant',
        content: '❌ Sorry, I encountered an error fetching recommendations. Please try again.',
        timestamp: Date.now(),
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const getTimeOfDay = (): string => {
    const hour = new Date().getHours();
    if (hour < 11) return 'breakfast';
    if (hour < 15) return 'lunch';
    if (hour < 17) return 'afternoon';
    if (hour < 21) return 'dinner';
    return 'late-night';
  };

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <KeyboardAvoidingView
        style={styles.keyboardView}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        keyboardVerticalOffset={0}
      >
        <Animated.View
          style={[
            { flex: 1 },
            {
              opacity: fadeAnim,
              transform: [{ translateY: slideAnim }],
            },
          ]}
        >
          {/* Header */}
          <View style={styles.header}>
            <Text style={styles.headerTitle}>Concierge</Text>
            {weather && location && (
              <Text style={styles.headerSubtitle}>
                {Math.round(weather.temperature)}°F • {weather.description}
              </Text>
            )}
          </View>

          {/* Quick Actions */}
          <View style={styles.quickActions}>
            <TouchableOpacity
              style={styles.quickButton}
              onPress={() => handleQuickAction('nearby')}
              disabled={!location}
            >
              <Text style={styles.quickButtonText}>📍 Nearby</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={styles.quickButton}
              onPress={() => handleQuickAction('michelin')}
              disabled={!location}
            >
              <Text style={styles.quickButtonText}>⭐ Michelin</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={styles.quickButton}
              onPress={() => handleQuickAction('recommend')}
              disabled={!location}
            >
              <Text style={styles.quickButtonText}>✨ Recommend</Text>
            </TouchableOpacity>
          </View>

          {/* Messages */}
          <ScrollView
            ref={scrollViewRef}
            style={styles.messagesContainer}
            contentContainerStyle={styles.messagesContent}
            keyboardShouldPersistTaps="handled"
          >
            {messages.map((msg, index) => (
              <View key={index}>
                <View
                  style={[
                    styles.messageBubble,
                    msg.role === 'user' ? styles.userBubble : styles.assistantBubble,
                  ]}
                >
                  {msg.role === 'assistant' ? (
                    <Markdown
                      style={{
                        body: {
                          color: '#E0E0E0',
                          fontSize: 15,
                          lineHeight: 22,
                        },
                        strong: {
                          color: '#FFFFFF',
                          fontWeight: '700',
                        },
                        em: {
                          color: '#B0B0B0',
                          fontStyle: 'italic',
                        },
                      }}
                    >
                      {msg.content}
                    </Markdown>
                  ) : (
                    <Text
                      style={[
                        styles.messageText,
                        styles.userText,
                      ]}
                    >
                      {msg.content}
                    </Text>
                  )}
                </View>

                {msg.pois && msg.pois.length > 0 && (
                  <View style={styles.poisContainer}>
                    {msg.pois.map((poi, poiIndex) => (
                      <POICard key={poi._id || poiIndex} poi={poi} />
                    ))}
                  </View>
                )}
              </View>
            ))}

            {isLoading && (
              <View style={styles.loadingContainer}>
                <ActivityIndicator size="small" color="#FFC107" />
                <Text style={styles.loadingText}>Thinking...</Text>
              </View>
            )}
          </ScrollView>

          {/* Input */}
          <View style={styles.inputContainer}>
            <TextInput
              style={styles.input}
              value={inputText}
              onChangeText={setInputText}
              placeholder="Ask about restaurants..."
              placeholderTextColor="rgba(255, 255, 255, 0.4)"
              multiline
              maxLength={500}
              editable={!isLoading}
            />
            <TouchableOpacity
              style={[styles.sendButton, (!inputText.trim() || isLoading) && styles.sendButtonDisabled]}
              onPress={handleSend}
              disabled={!inputText.trim() || isLoading}
            >
              <Text style={styles.sendButtonText}>Send</Text>
            </TouchableOpacity>
          </View>
        </Animated.View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0a0a1e',
  },
  keyboardView: {
    flex: 1,
    paddingBottom: Platform.OS === 'ios' ? 0 : 16,
  },
  header: {
    backgroundColor: 'transparent',
    paddingTop: IS_SMALL_DEVICE ? 12 : 16,
    paddingBottom: IS_SMALL_DEVICE ? 12 : 16,
    paddingHorizontal: IS_SMALL_DEVICE ? 16 : 20,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255, 255, 255, 0.1)',
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
    color: 'rgba(255, 255, 255, 0.6)',
  },
  quickActions: {
    flexDirection: 'row',
    padding: IS_SMALL_DEVICE ? 12 : 16,
    gap: IS_SMALL_DEVICE ? 8 : 10,
    backgroundColor: 'rgba(26, 26, 46, 0.6)',
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255, 255, 255, 0.05)',
  },
  quickButton: {
    flex: 1,
    paddingVertical: IS_SMALL_DEVICE ? 8 : 10,
    paddingHorizontal: IS_SMALL_DEVICE ? 4 : 6,
    borderRadius: 14,
    backgroundColor: 'rgba(255, 193, 7, 0.15)',
    borderWidth: 1,
    borderColor: 'rgba(255, 193, 7, 0.3)',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 40,
    shadowColor: '#FFC107',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 8,
    elevation: 5,
  },
  quickButtonText: {
    fontSize: IS_SMALL_DEVICE ? 10 : 12,
    fontWeight: '600',
    color: '#FFC107',
    textAlign: 'center',
  },
  messagesContainer: {
    flex: 1,
  },
  messagesContent: {
    paddingVertical: 16,
    paddingBottom: Platform.OS === 'ios' ? 100 : 80,
  },
  messageBubble: {
    maxWidth: '85%',
    padding: IS_SMALL_DEVICE ? 12 : 14,
    borderRadius: 20,
    marginHorizontal: IS_SMALL_DEVICE ? 12 : 16,
    marginVertical: 5,
    borderWidth: 1,
  },
  userBubble: {
    alignSelf: 'flex-end',
    backgroundColor: 'rgba(255, 193, 7, 0.2)',
    borderColor: 'rgba(255, 193, 7, 0.4)',
  },
  assistantBubble: {
    alignSelf: 'flex-start',
    backgroundColor: 'rgba(255, 255, 255, 0.08)',
    borderColor: 'rgba(255, 255, 255, 0.15)',
  },
  messageText: {
    fontSize: IS_SMALL_DEVICE ? 14 : 15,
    lineHeight: IS_SMALL_DEVICE ? 20 : 22,
  },
  userText: {
    color: '#ffffff',
  },
  assistantText: {
    color: 'rgba(255, 255, 255, 0.9)',
  },
  poisContainer: {
    marginTop: 8,
  },
  loadingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    backgroundColor: 'rgba(255, 193, 7, 0.1)',
    marginHorizontal: 16,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: 'rgba(255, 193, 7, 0.2)',
  },
  loadingText: {
    marginLeft: 10,
    fontSize: 14,
    color: '#FFC107',
    fontStyle: 'italic',
  },
  inputContainer: {
    flexDirection: 'row',
    padding: IS_SMALL_DEVICE ? 12 : 16,
    paddingBottom: Platform.OS === 'ios' ? 90 : 70,
    backgroundColor: 'rgba(26, 26, 46, 0.95)',
    borderTopWidth: 1,
    borderTopColor: 'rgba(255, 255, 255, 0.1)',
    gap: IS_SMALL_DEVICE ? 8 : 10,
  },
  input: {
    flex: 1,
    minHeight: 44,
    maxHeight: 100,
    paddingHorizontal: IS_SMALL_DEVICE ? 14 : 18,
    paddingVertical: IS_SMALL_DEVICE ? 10 : 12,
    backgroundColor: 'rgba(255, 255, 255, 0.08)',
    borderRadius: 22,
    fontSize: IS_SMALL_DEVICE ? 14 : 15,
    color: '#ffffff',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.15)',
  },
  sendButton: {
    paddingHorizontal: IS_SMALL_DEVICE ? 18 : 24,
    paddingVertical: 12,
    backgroundColor: 'rgba(255, 193, 7, 0.25)',
    borderRadius: 22,
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: 'rgba(255, 193, 7, 0.4)',
    shadowColor: '#FFC107',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
  },
  sendButtonDisabled: {
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    borderColor: 'rgba(255, 255, 255, 0.1)',
  },
  sendButtonText: {
    color: '#FFC107',
    fontSize: IS_SMALL_DEVICE ? 14 : 15,
    fontWeight: '700',
  },
});
