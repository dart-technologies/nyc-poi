# NYC POI Concierge - ChatGPT GPT Configuration

## GPT Setup Instructions

### 1. Go to ChatGPT GPT Builder
- Visit: https://chatgpt.com/gpts/editor
- Click "Create a GPT"

### 2. Configure GPT Details

**Name:** NYC POI Concierge

**Description:**
```
Discover NYC's best restaurants with prestige-first recommendations. I have access to 100+ curated POIs with Michelin stars, James Beard awards, and validated quality markers. I provide context-aware suggestions based on your location, occasion, weather, and preferences.
```

**Instructions:**
```
You are the NYC POI Concierge, an expert restaurant recommendation assistant for New York City.

Your capabilities:
- Search for restaurants by location, category, and prestige (Michelin stars, awards)
- Provide context-aware recommendations based on occasion, weather, time, and budget
- Explain why each recommendation fits the user's needs
- Highlight unique features: Michelin stars, James Beard awards, signature dishes

Data sources:
- Access to 100+ curated NYC POIs via MCP tools
- Real-time queries to MongoDB Atlas
- Geospatial search within user-specified radius
- Prestige-first ranking (Michelin, James Beard, NYT stars)

Personality:
- Knowledgeable but approachable
- Enthusiastic about NYC dining culture
- Concise yet informative
- Always explain the "why" behind recommendations

When users ask for recommendations:
1. Use get_contextual_recommendations for occasion-based queries
2. Use query_pois for specific searches (e.g., "Michelin 3-star restaurants")
3. Always mention standout features (Michelin stars, signature dishes, ambiance)
4. Provide practical details (price range, reservation difficulty, neighborhood)

Example interactions:
- "Find a romantic date night spot in Midtown" → Use get_contextual_recommendations
- "Show me all 3-Michelin-star restaurants" → Use query_pois with michelin_stars filter
- "What's good near Times Square for lunch?" → Combine location + time_of_day filtering
```

**Conversation starters:**
```
- "Find me a Michelin-starred restaurant for date night"
- "What's the best pizza in Greenwich Village?"
- "Show me all 3-Michelin-star restaurants in NYC"
- "I need a business dinner spot in Midtown"
```

### 3. Add Actions (MCP Cloud Integration)

#### Import OpenAPI Schema

Click **"Create new action"** and paste this OpenAPI spec:

```yaml
openapi: 3.1.0
info:
  title: NYC POI Concierge MCP Server
  description: Restaurant recommendations with prestige-first curation
  version: 1.0.0
servers:
  - url: https://15csm9y282hdasy6yvu2l7244j9vcrfc.deployments.mcp-agent.com
    description: MCP Cloud Deployment

paths:
  /tools/call:
    post:
      operationId: callMCPTool
      summary: Call any MCP tool
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                tool:
                  type: string
                  description: Name of the MCP tool to call
                  enum: [query_pois, get_contextual_recommendations]
                arguments:
                  type: object
                  description: Tool-specific arguments
              required: [tool, arguments]
      responses:
        '200':
          description: Successful tool call
          content:
            application/json:
              schema:
                type: object
                properties:
                  result:
                    type: object
                    description: Tool execution result

components:
  schemas:
    QueryPOIsArgs:
      type: object
      properties:
        latitude:
          type: number
          description: User's latitude
        longitude:
          type: number
          description: User's longitude
        radius_meters:
          type: number
          description: Search radius in meters (default 2000)
        categories:
          type: array
          items:
            type: string
            enum: [fine-dining, casual-dining, bars-cocktails]
        min_prestige_score:
          type: number
          description: Minimum prestige score (0-150)
        michelin_stars:
          type: array
          items:
            type: integer
            enum: [1, 2, 3]
        limit:
          type: integer
          description: Max results to return (default 10)
      required: [latitude, longitude]

    ContextualRecsArgs:
      type: object
      properties:
        latitude:
          type: number
        longitude:
          type: number
        radius_meters:
          type: number
          description: Search radius (default 3000)
        datetime:
          type: string
          format: date-time
          description: Target date/time ISO 8601
        weather:
          type: string
          enum: [sunny, rain, cold, snow, any]
        occasion:
          type: string
          enum: [date-night, business-dinner, casual, celebration, drinks, late-night]
        group_size:
          type: integer
          description: Number of people (default 2)
        budget:
          type: string
          enum: [$, $$, $$$, $$$$, any]
        limit:
          type: integer
          description: Max results (default 5)
      required: [latitude, longitude]
```

#### Authentication Settings
- **Authentication:** None (your MCP Cloud is in no-auth mode)
- **Privacy policy:** (Optional - add your privacy policy URL if needed)

### 4. Test the GPT

#### Test Query 1: Search POIs
```
Show me all Michelin 3-star restaurants in NYC
```

Should call:
```json
{
  "tool": "query_pois",
  "arguments": {
    "latitude": 40.7580,
    "longitude": -73.9851,
    "michelin_stars": [3],
    "limit": 10
  }
}
```

#### Test Query 2: Contextual Recommendations
```
Find me a romantic restaurant for dinner tonight in Midtown
```

Should call:
```json
{
  "tool": "get_contextual_recommendations",
  "arguments": {
    "latitude": 40.7580,
    "longitude": -73.9851,
    "occasion": "date-night",
    "datetime": "2025-11-23T19:00:00",
    "limit": 5
  }
}
```

### 5. Publish GPT

- **Visibility:** Choose "Anyone with a link" for hackathon demo
- **Category:** Lifestyle or Research & Analysis
- **Save:** Click "Create" to publish

---

## Usage in Demo Video

1. **Open ChatGPT GPT:** Share link with judges
2. **Show natural language queries:**
   - "I'm in Midtown and need a business dinner spot"
   - "Show me the best pizza in NYC"
   - "Find Michelin-starred restaurants near Central Park"
3. **Highlight MCP integration:** Show how GPT calls your MongoDB tools in real-time

---

## Alternative: Keep Expo App Chat

If you prefer to keep the **Expo mobile app** as your primary interface:

### Option A: Connect Expo to MCP Cloud Tools
Modify `mcpService.ts` to call MCP tools instead of direct OpenAI:
- Use OpenAI function calling with tool definitions
- Call your MCP Cloud endpoints as functions
- Let GPT decide when to use tools

### Option B: Dual Interface
- **ChatGPT GPT:** Desktop/web demo (judges can test)
- **Expo App:** Mobile demo with direct OpenAI + HTTP endpoints

---

## Recommendation

For your **hackathon demo** (deadline in 8 hours), I recommend:

1. ✅ **Keep Expo app as-is** (it works, looks great)
2. ✅ **Create ChatGPT GPT** (15 min setup, shows MCP Cloud integration)
3. ✅ **Demo both** in your video:
   - Mobile app for UX/design showcase
   - ChatGPT GPT for MCP Cloud + MongoDB integration

This gives you **two impressive demos** and proves your MCP Cloud deployment works!

Would you like me to:
1. Create the full OpenAPI schema file for the GPT?
2. Update your Expo app to use MCP tool calling?
3. Both?
