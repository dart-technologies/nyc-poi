#!/bin/bash
# MCP Inspector Test Script
# Launches the MCP Inspector to test NYC POI Concierge server

echo "🔍 MCP Inspector Test Setup"
echo "=" 
echo ""

# Check if npx is available
if ! command -v npx &> /dev/null; then
    echo "❌ npx not found. Please install Node.js first:"
    echo "   brew install node"
    exit 1
fi

echo "✅ Node.js/npx found"

# Load environment variables
if [ -f ../../.env ]; then
    echo "📂 Loading environment variables..."
    export $(cat ../../.env | grep -v '^#' | xargs)
    echo "✅ Environment loaded"
else
    echo "⚠️  .env file not found, continuing without it..."
fi

echo ""
echo "🚀 Starting MCP Inspector..."
echo ""
echo "The Inspector will open in your browser with a UI to test the MCP tools."
echo ""
echo "Available tools:"
echo "  1. query_pois - Search POIs with filters"
echo "  2. get_contextual_recommendations - Context-aware suggestions"
echo ""
echo "Example test (Times Square location):"
echo "  Latitude: 40.7580"
echo "  Longitude: -73.9851"
echo ""
echo "="
echo ""

# Run MCP Inspector
npx @modelcontextprotocol/inspector python3 src/server.py
