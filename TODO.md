# NYC POI Concierge - MongoDB x Tavily x LastMile AI Hackathon
**Team:** SynchroniCities  
**Event:** Nov 21-24, 2025 | MongoDB HQ, NYC  
**Submission Deadline:** November 23, 2025 at 11:59 PM EST  
**Goal:** Prestige-first NYC concierge with Tavily curation, MongoDB Atlas, LastMile MCP, GPT-5.1 + Expo

---

## 🎯 MVP Scope (Hackathon Focus)
- **50-100 curated NYC restaurants** with Michelin/awards via Tavily
- **MongoDB Atlas** with geospatial + vector search
- **MCP server** with 2 core tools (query_pois, contextual_recommendations)
- **Expo mobile app** with chat UI + map view
- **Working demo** of context-aware recommendations

---

## 📊 Current Progress (Nov 23, 1:07 PM EST)

**Overall:** ~99% Complete | **Phase 1:** ✅ Complete | **Phase 2:** ✅ Complete | **Phase 3:** ✅ Complete | **Phase 4:** ✅ Complete | **Integration:** ✅ COMPLETE! | **MCP Cloud:** ✅ DEPLOYED!

### ✅ Completed:
- Infrastructure & security (API keys secured, .gitignore protected)
- POI schema design & data curation (7 premium + 468 candidates)
- **MongoDB import complete** (134 POIs live in production database)
- **MCP server complete** (2 tools built and tested)
- **MCP Cloud deployment LIVE** ✅ 
  - Endpoint: `https://15csm9y282hdasy6yvu2l7244j9vcrfc.deployments.mcp-agent.com`
  - Status: ONLINE and accessible
  - Authentication: No-auth mode for testing
- **Expo mobile app complete** (Dark glassmorphism theme, Native iOS tabs)
- **Mobile app fully responsive** (iPhone SE to Pro Max optimized)
- **Full stack integration complete** (Mobile app ↔ MCP Cloud ↔ MongoDB)
- **API endpoints updated** (mcpService.ts configured with cloud URL)
- Tavily search pipeline (468 candidates discovered)
- Mock data system for parallel dev
- Security documentation & audit
- Test suite (all passing) ✅ **100% Pass Rate**
- **Repo polish complete** (logs cleaned, secrets secured)


### ⏳ Next Up (19h remaining):
1. **[DONE] Test mobile app end-to-end** ✅
   - Verified live data loading from MongoDB
   - Verified Michelin filter and geospatial search
   - **Refactored folder structure** for better organization
2. **[OPTIONAL] Create ChatGPT GPT** (15 min) - **BONUS DEMO**
   - Follow guide: `backend/mcp-server/chatgpt_gpt/README.md`
   - Create Custom GPT at https://chatgpt.com/gpts/editor
   - Import OpenAPI schema from `chatgpt_gpt/openapi.yaml`
   - Test with example queries (shows MCP Cloud integration!)
   - Get shareable link for demo
3. **[DONE] Record 5-min demo video** ✅ **COMPLETE**
   - ✅ Show architecture & API docs
   - ✅ Demo mobile app with live data
   - ✅ Highlight Michelin stars, geospatial search, MCP Cloud
   - ✅ Upload to YouTube: https://youtu.be/zJF-ZN2inig
4. **Submit to Google Form** (5 min) - **FINAL STEP**
   - GitHub repo link
   - YouTube video link
   - **Deadline: 11:59 PM EST**

---

## FRIDAY NOV 21 (Kickoff 4-8pm) ✅ COMPLETE
### Hackathon Infrastructure
- [x] Team setup & role assignments
- [x] MongoDB Atlas cluster provisioned
- [x] API keys secured: Tavily, OpenAI, Weather (**Security hardened - all keys in .env**)
- [x] Git repo initialized with plan review

### Phase 1: Tavily POI Curation (PRIORITY 1)
- [x] Define core POI schema (name, location, prestige, hours, contact)
- [x] Implement Tavily search pipeline for fine dining (Michelin focus)
- [x] Extract POI candidates: **468 discovered** (134 Michelin, 211 casual, 123 bars)
- [x] Normalize metadata: address, coordinates, prestige score, signature dishes
- [x] Validate data quality - **7 premium POIs manually curated**

---

## SATURDAY NOV 22 (Remote Hacking) ✅ COMPLETE
### Phase 1: Complete Dataset (PRIORITY 1) ✅ COMPLETE
- [x] **Data curation complete:** 7 curated + 468 candidates available
  - ✅ 3 Michelin 3-star: Eleven Madison Park, Le Bernardin, Per Se
  - ✅ 2 Michelin 1-2 star: Gramercy Tavern, The Modern
  - ✅ 1 Casual: Joe's Pizza
  - ✅ 1 Bar: Death & Co
- [x] **Mock data system:** 3 POIs for parallel development
- [x] **MongoDB schema & indexes:** Geospatial (2dsphere), prestige, text search ready
- [x] **Import pipeline:** Created with validation
- [x] **Bulk import POIs to MongoDB** ✅ **7 POIs imported successfully**
- [x] **Test queries:** Geospatial radius, Michelin filter ✅ **All passing**
- [ ] Generate OpenAI embeddings for semantic search (deferred - not required for MVP)
- [ ] Create vector search index in Atlas UI (deferred - not required for MVP)

### Phase 2: MCP Server Core (PRIORITY 2) ✅ COMPLETE
- [x] **Scaffold LastMile MCP server** ✅ `backend/mcp-server/src/server.py`
- [x] **Implement `query_pois` tool** ✅ Geospatial search with filters working
- [x] **Implement `get_contextual_recommendations` tool** ✅ Context-aware suggestions working
- [x] **Test tools** ✅ All tests passing (test_server.py, test_tools.py)
- [x] **Document tool schemas & examples** ✅ README.md, TEST_RESULTS.md, INSPECTOR_GUIDE.md

---

## SUNDAY NOV 23 (Submission Prep)
### Phase 2: MCP Integration (PRIORITY 2)
- [x] Add MongoDB aggregation for hybrid scoring (prestige + proximity + context)
- [x] Integrate Tavily real-time enrichment (optional: `enrich_poi_live` tool)
- [x] Create MCP resources: neighborhood guides, category taxonomy
- [ ] Test GPT-5.1 with MCP tools via API _(deferred to post-submission due to limited runway)_

### Phase 3: Expo Mobile App (PRIORITY 3) ✅ COMPLETE
- [x] Scaffold Expo app with tabs (Home/Chat, Discover, Favorites)
- [x] Implement location services (expo-location)
- [x] Implement weather API integration (OpenWeatherMap)
- [x] Build chat UI with GPT + MCP client
- [x] Display POI cards with prestige badges (Michelin stars)
- [x] Add basic map view with POI markers (react-native-maps)

### Phase 4: Demo Prep (PRIORITY 4) ✅ COMPLETE
- [x] End-to-end test with mock data (all features working)
- [x] Mobile app with stunning dark glassmorphism UI
- [x] Native iOS tabs with SF Symbols integration
- [x] Responsive design (iPhone SE to Pro Max)
- [x] **MCP Cloud deployment COMPLETE** ✅ 
  - [x] Deployed to: `https://15csm9y282hdasy6yvu2l7244j9vcrfc.deployments.mcp-agent.com`
  - [x] Resolved Issue #620 (Docker registry access)
  - [x] Expo app configured with cloud endpoint
- [x] **Create Architecture Diagram** (`ARCHITECTURE.md`)
  - [x] Visual data flow (Client -> MCP Cloud -> MongoDB/OpenAI)
  - [x] Highlight "Production Quality" aspects
- [x] **Polish Mobile UI**
  - [x] Fix tab bar overlay issues
  - [x] Ensure consistent header styling
  - [x] Implement smooth "buttery" transitions (LayoutAnimation)
  - [x] Fix white flash on dark mode loading
- [x] **Record Demo Video** (5 min max) ✅ **COMPLETE**
  - [x] Show "Production Ready" architecture (diagram)
  - [x] Demo Mobile App (smooth transitions, real data)
  - [x] Explain MCP Cloud deployment success
  - [x] Upload to YouTube: https://youtu.be/zJF-ZN2inig
- [ ] **Submit to Hackathon**
  - [ ] Google Forms submission
  - [ ] Link GitHub Repo
  - [ ] Upload Video


---

## SUNDAY NOV 23 (Submission Deadline: 11:59 PM EST) ⏰
### Final Polish & Submission
- [x] Bug fixes from testing (Fixed Michelin filter data issues)
- [x] Code cleanup & documentation (Logs cleaned, .gitignore updated, Architecture documented)
- [x] Record 5-min demo video (YouTube) ✅ https://youtu.be/zJF-ZN2inig
- [ ] **SUBMIT GOOGLE FORM BY 11:59 PM EST** ⏰
  - [ ] Public GitHub Repository Link
  - [x] 5-min Video Demo Link (YouTube) ✅ https://youtu.be/zJF-ZN2inig

---

## MONDAY NOV 24 (Judging Day)
### Judging (No Presentation Required)
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
- Overall Best Project (Best AI agent that demonstrates real-world usability)
- Best Use of MongoDB (geospatial + vector search)
- Best Use of Tavily (AI-powered prestige curation)
- Best Use of LastMile AI (MCP architecture)
