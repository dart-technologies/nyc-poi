# NYC POI Concierge - MongoDB x Tavily x LastMile AI Hackathon
**Event:** Nov 21-24, 2025 | MongoDB HQ, NYC  
**Goal:** Prestige-first NYC concierge with Tavily curation, MongoDB Atlas, LastMile MCP, GPT-5.1 + Expo

---

## 🎯 MVP Scope (Hackathon Focus)
- **50-100 curated NYC restaurants** with Michelin/awards via Tavily
- **MongoDB Atlas** with geospatial + vector search
- **MCP server** with 2 core tools (query_pois, contextual_recommendations)
- **Expo mobile app** with chat UI + map view
- **Working demo** of context-aware recommendations

---

## FRIDAY NOV 21 (Kickoff 4-8pm)
### Hackathon Infrastructure
- [ ] Team setup & role assignments
- [ ] MongoDB Atlas cluster provisioned
- [ ] API keys secured: Tavily, OpenAI, Weather
- [ ] Git repo initialized with plan review

### Phase 1: Tavily POI Curation (PRIORITY 1)
- [ ] Define core POI schema (name, location, prestige, hours, contact)
- [ ] Implement Tavily search pipeline for fine dining (Michelin focus)
- [ ] Extract 30 POIs: restaurants with Michelin stars, James Beard, NYT reviews
- [ ] Normalize metadata: address, coordinates, prestige score, signature dishes
- [ ] Validate data quality (duplicate check, geocoding accuracy)

---

## SATURDAY NOV 22 (Remote Hacking)
### Phase 1: Complete Dataset (PRIORITY 1)
- [ ] Expand to 100 POIs across categories (dining, bars, culture)
- [ ] Generate OpenAI embeddings for semantic search (text-embedding-3-small)
- [ ] Bulk import POIs to MongoDB with geospatial index (2dsphere)
- [ ] Create vector search index in Atlas UI
- [ ] Test queries: geospatial radius, Michelin filter, semantic search

### Phase 2: MCP Server Core (PRIORITY 2)
- [ ] Scaffold LastMile MCP server (Python/TypeScript)
- [ ] Implement `query_pois` tool (location, categories, prestige filters)
- [ ] Implement `get_contextual_recommendations` tool (location, datetime, occasion, weather)
- [ ] Test tools with MCP inspector/CLI
- [ ] Document tool schemas & examples

---

## SUNDAY NOV 23 (Submission Prep)
### Phase 2: MCP Integration (PRIORITY 2)
- [ ] Add MongoDB aggregation for hybrid scoring (prestige + proximity + context)
- [ ] Integrate Tavily real-time enrichment (optional: `enrich_poi_live` tool)
- [ ] Create MCP resources: neighborhood guides, category taxonomy
- [ ] Test GPT-5.1 with MCP tools via API

### Phase 3: Expo Mobile App (PRIORITY 3)
- [ ] Scaffold Expo app with tabs (Home/Chat, Discover, Favorites)
- [ ] Implement location services (expo-location)
- [ ] Implement weather API integration (OpenWeatherMap)
- [ ] Build chat UI with GPT-5.1 + MCP client
- [ ] Display POI cards with prestige badges (Michelin stars)
- [ ] Add basic map view with POI markers (react-native-maps)

### Phase 4: Demo Prep (PRIORITY 4)
- [ ] End-to-end test: "Find Michelin star restaurant near me"
- [ ] Verify context-aware flow: location → weather → time → recommendations
- [ ] Screenshot key screens for presentation
- [ ] Draft demo script (1-2 min walkthrough)

---

## MONDAY NOV 24 (Judging Day)
### Final Polish
- [ ] Bug fixes from Sunday testing
- [ ] Code cleanup & documentation (README with architecture diagram)
- [ ] Record 1-min demo video (mobile flow)
- [ ] Prepare presentation deck (problem, solution, tech stack, demo)
- [ ] Submit project by deadline

### Judging Preparation
- [ ] Highlight MongoDB features: geospatial, vector search, aggregations
- [ ] Highlight Tavily: prestige curation, multi-source validation
- [ ] Highlight LastMile MCP: composable tools, GPT-5.1 integration
- [ ] Emphasize differentiation: prestige-first vs generic recommendations

---

## 📊 Success Criteria
- **Data:** 100+ POIs with validated prestige markers
- **MCP:** 2+ working tools with MongoDB integration
- **Mobile:** Conversational UI with live recommendations
- **Demo:** End-to-end context-aware recommendation flow

---

## 🚧 Deferred (Post-Hackathon)
- search_by_vibe semantic search tool
- Multiple neighborhood coverage (focus Manhattan MVP)
- Advanced filters (price, cuisine, dietary)
- Favorites/history persistence
- Push notifications
- Production deployment (focus local demo)

---

## 🎁 Prize Categories
- Overall Best Project
- Best Use of MongoDB (geospatial + vector search)
- Best Use of Tavily (AI-powered prestige curation)
- Best Use of LastMile AI (MCP architecture)