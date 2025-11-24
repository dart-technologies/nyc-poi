#!/bin/bash
# Quick MCP Cloud Deployment Script

echo "🚀 NYC POI Concierge - MCP Cloud Deployment"
echo "==========================================="
echo ""

# Step 1: Check if mcp-agent is installed
echo "📋 Step 1: Checking mcp-agent installation..."
if ! command -v mcp-agent &> /dev/null; then
    echo "❌ mcp-agent not found. Installing..."
    uv tool install mcp-agent
    echo "✅ mcp-agent installed!"
else
    echo "✅ mcp-agent already installed"
fi

# Step 2: Fill secrets
echo ""
echo "📋 Step 2: Configure secrets"
echo "Please edit ../../backend/mcp-server/mcp_agent.secrets.yaml"
echo "Replace YOUR_*_HERE with your actual API keys"
echo ""
read -p "Have you filled in mcp_agent.secrets.yaml? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Please edit the file and run this script again"
    exit 1
fi

# Step 3: Login
echo ""
echo "📋 Step 3: Logging in to MCP Agent Cloud..."
cd ../../backend/mcp-server
mcp-agent login

# Step 4: Deploy
echo ""
echo "📋 Step 4: Deploying to MCP Agent Cloud..."
mcp-agent deploy nyc-poi-server \
  --app-description "NYC restaurant discovery with AI-powered prestige-first curation" \
  --no-auth

# Step 5: Get deployment info
echo ""
echo "📋 Step 5: Getting deployment details..."
mcp-agent cloud servers describe nyc-poi-server

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Copy the Server URL from above"
echo "2. Update ../../frontend/expo-app/config/index.ts with the URL"
echo "3. Test your mobile app!"
echo ""
