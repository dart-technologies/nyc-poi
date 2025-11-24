# Vector Search Setup Guide

## Overview
This guide shows how to set up MongoDB Atlas Vector Search for the `search_by_vibe` semantic search tool.

## ✅ Step 1: Generate Embeddings (COMPLETE)

All 69 POIs now have embeddings generated using OpenAI's `text-embedding-3-small` model.

```bash
python3 scripts/data_pipeline/generate_embeddings.py
```

**Result:** Each POI document now has:
- `embedding`: 1536-dimensional vector
- `embedding_text`: Rich text description used for embedding
- `embedding_model`: "text-embedding-3-small"
- `embedding_dimensions`: 1536

---

## 📋 Step 2: Create Vector Search Index in Atlas

### Atlas UI Steps:

1. **Navigate to Atlas Search**
   - Go to your MongoDB Atlas dashboard
   - Click on your cluster: `nyc-poi`
   - Click on the **"Atlas Search"** tab
   - Click **"Create Search Index"**

2. **Select Index Type**
   - Choose **"Atlas Vector Search"**
   - Click **"Next"**

3. **Configure Index**
   - **Database:** `nyc-poi`
   - **Collection:** `pois`
   - **Index Name:** `vector_index`

4. **Index Definition (JSON Editor)**

```json
{
  "fields": [
    {
      "type": "vector",
      "path": "embedding",
      "numDimensions": 1536,
      "similarity": "cosine"
    }
  ]
}
```

5. **Create Index**
   - Click **"Create Search Index"**
   - Wait for index to build (usually 1-2 minutes)
   - Status should show "Active" when ready

---

## 🧪 Step 3: Test Vector Search

After index creation, test with a MongoDB aggregation query:

```javascript
db.pois.aggregate([
  {
    $vectorSearch: {
      index: "vector_index",
      path: "embedding",
      queryVector: [...], // 1536-dim vector from OpenAI
      numCandidates: 100,
      limit: 10
    }
  },
  {
    $project: {
      name: 1,
      category: 1,
      "address.neighborhood": 1,
      score: { $meta: "vectorSearchScore" }
    }
  }
])
```

---

## 🔧 Step 4: Implement search_by_vibe Tool

See `backend/mcp-server/src/server.py` for the implementation.

**Tool accepts:**
- `vibe_query`: Natural language description (e.g., "romantic and quiet")
- `limit`: Maximum results (default: 10)
- `min_score`: Similarity threshold (default: 0.7)

**Returns:**
- List of POIs matching the vibe with similarity scores

---

## 📊 Index Status Check

To verify index status in MongoDB Shell:

```javascript
db.pois.getSearchIndexes("vector_index")
```

Expected output:
```json
{
  "name": "vector_index",
  "type": "vectorSearch",
  "status": "READY",
  "latestDefinition": {
    "fields": [...]
  }
}
```

---

## 💡 Next Steps

1. ✅ Embeddings generated (69 POIs)
2. ⏳ Create vector index in Atlas UI (manual step)
3. ⏳ Implement `search_by_vibe` MCP tool
4. ⏳ Test with sample queries
5. ⏳ Update documentation

---

## 🐛 Troubleshooting

### Index Not Building
- Verify collection has documents with `embedding` field
- Check field path is exactly `embedding` (case-sensitive)
- Ensure dimensions match (1536)

### Poor Search Results
- Try lowering `min_score` threshold
- Increase `numCandidates` for better recall
- Verify embedding quality with sample queries

### Performance Issues
- Vector search is optimized for similarity queries
- Index build time scales with dataset size
- Consider adding filters (category, location) to narrow results
