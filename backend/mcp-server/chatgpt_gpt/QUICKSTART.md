# ChatGPT GPT - Quick Start Checklist

**Time:** 15 minutes | **Difficulty:** Easy | **Impact:** High

---

## ☑️ Pre-Flight Check

- [ ] MCP Cloud deployed: https://15csm9y282hdasy6yvu2l7244j9vcrfc.deployments.mcp-agent.com
- [ ] MongoDB has 134 POIs imported
- [ ] You have ChatGPT Plus account (required for creating GPTs)

---

## 📋 Step-by-Step (15 min)

### Step 1: Open GPT Editor (1 min)
- [ ] Go to: https://chatgpt.com/gpts/editor
- [ ] Click **"Create a GPT"**

### Step 2: Configure GPT (5 min)
- [ ] **Name:** `NYC POI Concierge`
- [ ] **Description:** 
  ```
  Discover NYC's best restaurants with prestige-first recommendations. 
  I have access to 100+ curated POIs with Michelin stars, James Beard 
  awards, and validated quality markers.
  ```
- [ ] **Instructions:** Copy from `gpt_config.md` lines 23-65
- [ ] **Conversation starters:** Add these 4:
  ```
  - "Find me a Michelin-starred restaurant for date night"
  - "What's the best pizza in Greenwich Village?"
  - "Show me all 3-Michelin-star restaurants in NYC"
  - "I need a business dinner spot in Midtown"
  ```

### Step 3: Add Actions (5 min)
- [ ] Click **"Create new action"**
- [ ] Click **"Import from URL"** (or paste manually)
- [ ] **If importing:** Use `https://raw.githubusercontent.com/[your-repo]/nyc-poi/main/backend/mcp-server/chatgpt_gpt/openapi.yaml`
- [ ] **If pasting:** Copy entire contents of `openapi.yaml`
- [ ] **Authentication:** Select **"None"**
- [ ] **Privacy Policy:** Leave blank (or add if you have one)
- [ ] Click **"Save"**

### Step 4: Test (3 min)
- [ ] Click **"Preview"** in top right
- [ ] Try: `"Show me all Michelin 3-star restaurants"`
- [ ] Verify it calls your MCP Cloud endpoint
- [ ] Check response includes Le Bernardin, Eleven Madison Park, Per Se
- [ ] Try: `"Find a romantic restaurant in Midtown"`
- [ ] Verify it returns contextual recommendations

### Step 5: Publish (1 min)
- [ ] Click **"Update"** or **"Create"** (top right)
- [ ] **Sharing:** Select **"Anyone with a link"**
- [ ] Click **"Confirm"**
- [ ] **Copy the share link** (you'll need this for demo!)

---

## ✅ Verification

Your GPT should:
- [ ] Respond to natural language queries
- [ ] Call MCP Cloud tools automatically
- [ ] Return POIs from your MongoDB database
- [ ] Show Michelin stars and prestige scores
- [ ] Explain why recommendations fit the context

---

## 🎬 For Your Demo Video

**What to show:**
1. **Share the GPT link** (judges can test it themselves!)
2. **Demo a query:** "Find me a Michelin-starred date night spot"
3. **Show it working:** GPT calls tools → MongoDB → returns results
4. **Highlight features:**
   - Prestige-first ranking
   - Geospatial search
   - Context awareness (occasion, weather, time)
   - Michelin stars & awards

**Script idea:**
```
"I've also created a ChatGPT GPT that lets anyone discover NYC 
restaurants through natural conversation. Watch as I ask it to 
find Michelin-starred restaurants..."

[Type query, show response]

"Notice how it's calling my MCP Cloud server in real-time, which 
queries our MongoDB database of 134 curated POIs. The results are 
ranked by prestige score and include Michelin stars, signature 
dishes, and practical details."

[Show share link]

"Judges, you can test this yourselves at [your-link] - it's 
fully functional and connected to our live MongoDB database."
```

---

## 🐛 Troubleshooting

**"Action schema invalid"**
- Check that `openapi.yaml` is valid YAML (no syntax errors)
- Verify the server URL matches your MCP Cloud deployment

**"Tool call failed"**
- Verify MCP Cloud is running: Visit the endpoint in browser
- Check MongoDB is accessible from MCP Cloud
- Review MCP Cloud logs for errors

**"Can't create GPT"**
- Ensure you have ChatGPT Plus subscription
- Try refreshing the page and starting over

**"No results returned"**
- Verify MongoDB has POIs: Check import status
- Test tools directly via MCP Inspector
- Check geospatial indexes exist

---

## 📦 Files Reference

```
backend/mcp-server/chatgpt_gpt/
├── README.md              ← Full documentation
├── gpt_config.md          ← Detailed GPT configuration
├── openapi.yaml           ← Import this into ChatGPT Actions
├── EXAMPLES.md            ← Example conversations
└── QUICKSTART.md          ← This file
```

---

## ⏱️ Timeline

- **Now:** Create GPT (15 min)
- **Next:** Test thoroughly (5 min)
- **Then:** Record demo (include GPT segment)
- **Finally:** Submit with GPT link included

---

## 🎯 Success Metrics

Your GPT is ready when:
- ✅ Responds to natural queries naturally
- ✅ Calls MCP tools without errors
- ✅ Returns real data from MongoDB
- ✅ Share link works for anyone
- ✅ You feel confident demoing it

---

**Ready? Start here: https://chatgpt.com/gpts/editor**

Good luck! 🚀
