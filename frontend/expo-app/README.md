# NYC POI Concierge - Mobile App 📱

Expo React Native app for discovering prestige-first NYC restaurants with AI-powered recommendations.

## 🎯 Features
- **Chat Interface**: GPT-4o-mini + MCP integration
- **Interactive Map**: Discover restaurants with filters
- **Context Aware**: Weather & time-based suggestions
- **Prestige Badges**: Michelin stars, James Beard awards

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd frontend/expo-app
npm install
```

### 2. Configure Environment
Create `.env` with:
```bash
EXPO_PUBLIC_OPENAI_API_KEY=sk-...
EXPO_PUBLIC_OPENWEATHER_API_KEY=...
EXPO_PUBLIC_MCP_SERVER_URL=http://localhost:8000
```

### 3. Run App
```bash
npm start
# Press 'i' for iOS Simulator
# Press 'a' for Android Emulator
```

## 🏗️ Structure
- `app/(tabs)/`: Main screens (Chat, Discover)
- `components/`: UI components (POICard, Map)
- `services/`: API integrations (Location, Weather, MCP)
- `config/`: App configuration

## 🔧 Troubleshooting
- **Map not showing?** Check Google Maps API key for Android.
- **No POIs?** Ensure backend is running on port 8000.
