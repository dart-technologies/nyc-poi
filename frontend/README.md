# NYC POI Concierge - Frontend (Expo Mobile App)

React Native mobile app with GPT-5.1 conversational interface for NYC restaurant discovery.

## Tech Stack
- **Framework:** Expo (React Native)
- **AI:** OpenAI GPT-5.1 with MCP integration
- **Maps:** react-native-maps
- **Location:** expo-location
- **Weather:** OpenWeatherMap API

## Structure
```
frontend/
├── app/                   # Expo Router screens
│   ├── (tabs)/
│   │   ├── index.tsx      # Home/Chat screen
│   │   ├── discover.tsx   # Browse POIs (deferred)
│   │   └── favorites.tsx  # Saved venues (deferred)
│   ├── poi/
│   │   └── [id].tsx       # POI detail screen
│   └── _layout.tsx
├── components/            # React components
│   ├── Chat/
│   │   ├── MessageBubble.tsx
│   │   ├── ChatInput.tsx
│   │   └── POICard.tsx
│   ├── Map/
│   │   ├── MapView.tsx
│   │   └── POIMarker.tsx
│   └── POI/
│       ├── POIList.tsx
│       └── PrestigeBadge.tsx
├── services/              # API clients
│   ├── mcp-client.ts      # MCP client implementation
│   ├── gpt.ts             # GPT-5.1 integration
│   ├── location.ts        # Location services
│   └── weather.ts         # Weather API
├── hooks/                 # Custom React hooks
│   ├── useLocation.ts
│   ├── useWeather.ts
│   └── useMCP.ts
├── types/                 # TypeScript types
│   ├── poi.ts
│   └── mcp.ts
├── package.json
├── tsconfig.json
└── .env.example
```

## Setup

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Run Development Server
```bash
npx expo start
```

Scan the QR code with:
- **iOS:** Expo Go app
- **Android:** Expo Go app

## Key Features (MVP)

### Chat Interface
- Conversational UI with GPT-5.1
- MCP tool integration for restaurant queries
- Context-aware recommendations

### Map View
- Display restaurants on interactive map
- POI markers with prestige indicators
- Navigation to selected venue

### POI Cards
- Prestige badges (Michelin stars, awards)
- Distance from current location
- Signature dishes
- Reservation links

## Environment Variables
```
EXPO_PUBLIC_MCP_SERVER_URL=http://localhost:3000
EXPO_PUBLIC_OPENAI_API_KEY=sk-...
EXPO_PUBLIC_WEATHER_API_KEY=...
```

## Development Notes
- MCP server must be running locally for testing
- Location permissions required for context-aware recommendations
- Uses Expo Go for quick iteration (no need to build native apps)
