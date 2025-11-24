# 🎬 NYC POI Concierge - Hackathon Demo Script

**Target Length:** 3-5 Minutes
**Goal:** Win "Overall Best Project" by demonstrating real-world usability backed by a powerful tech stack.

---

## 🎙️ Introduction (30s)

"Hi, I'm Mike from Team SynchroniCities. We built **NYC Concierge**, an intelligent dining assistant that moves beyond generic 5-star reviews to provide **prestige-first, context-aware recommendations**."

"We're targeting **Best AI Agent** by demonstrating real-world usability powered by the hattrick of hackathon technologies: **MongoDB**, **Tavily**, and **LastMile AI**."

---

## 🎭 Scenario 1: "Real-Time Intelligence" (Tavily)
**Highlight:** Best Use of Tavily (Live Web Enrichment)

**Action:**
1. Open the **Expo Mobile App**.
2. Tap on **Le Bernardin** Ask AI to open enriched details card.
3. Scroll to the **"Holiday Hours"** section.

**Voiceover:**
"Static databases get stale fast. We solved this with **Tavily's Real-Time AI Search**."

"I'm tapping on Le Bernardin. Notice this holiday schedule? This isn't in our database. The system just used Tavily to scan Yelp and the web in real-time, confirming they have a special **Thanksgiving menu** this week."

"This ensures you never book a closed restaurant or miss a special event."

**Tech Callout:**
> "We use Tavily's `search` endpoint to fetch live metadata that would be impossible to keep up-to-date manually."

---

## 🎭 Scenario 2: "The Contextual Concierge" (LastMile AI + Context)
**Highlight:** Best Use of LastMile AI (MCP Architecture)

**Action:**
1. Switch to the **Chat Tab**.
2. Type: *"Where can I get a late night drink within walking distance?"*
3. Show the "Thinking..." state (MCP working).
4. Reveal the response recommending **Death & Co** or a nearby cocktail bar.

**Voiceover:**
"Here's where the **LastMile AI Model Context Protocol (MCP)** shines. The agent doesn't just search text; it understands *context*."

"It sees it's late, checks my exact location, and knows 'walking distance' implies a tight radius. It routes this intent through the MCP server to find top-rated bars that are *actually open* right now."

**Tech Callout:**
> "The MCP server orchestrates the tools: checking real-time opening hours, calculating geospatial distance, and filtering for 'Bars & Cocktails' automatically."

---

## 🎭 Scenario 3: "The Hyperlocal Power User" (MongoDB Geospatial)
**Highlight:** Best Use of MongoDB (Geospatial) & Future Roadmap

**Action:**
1. Switch to the **Discover (Map) Tab**.
2. Zoom in/out to show markers updating.
3. Tap a filter: **"Fine Dining"**.
4. Tap a marker to show the **POI Card** with the distance calculation (e.g., "0.3 mi").

**Voiceover:**
"Under the hood, **MongoDB Atlas** is doing the heavy lifting. We use MongoDB's **Geospatial Indexing** to perform lightning-fast `$geoNear` queries."

"Every time I move the map or apply a filter, MongoDB re-ranks the results based on a hybrid score of **Distance + Prestige**. It ensures I'm not just seeing *close* places, but the *best* places close to me."

**Tech Callout:**
> "Our schema is already prepped for **Vector Search**. Post-hackathon, we'll enable semantic queries like 'quiet atmosphere', making this a fully multimodal search engine."

---

## 🏁 Conclusion (30s)

"NYC Concierge isn't just a wrapper around ChatGPT. It's a **production-grade architecture**:"

1.  **Tavily** ensures high-quality data.
2.  **MongoDB** powers fast, location-based discovery.
3.  **LastMile MCP** provides the intelligent orchestration.
4.  **Expo** delivers a premium mobile user experience.

"Thank you!"