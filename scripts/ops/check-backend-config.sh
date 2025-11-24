#!/bin/bash

# Mobile App Fix - Switch Between Local and Cloud Backend

echo ""
echo "🔧 NYC POI Mobile App - Backend Configuration"
echo "=============================================="
echo ""

# Check current configuration
CURRENT_URL=$(grep EXPO_PUBLIC_MCP_SERVER_URL ../../frontend/expo-app/.env | cut -d'=' -f2)

echo "📍 Current backend URL:"
echo "   $CURRENT_URL"
echo ""

# Determine which backend it's pointing to
if [[ $CURRENT_URL == *"localhost"* ]] || [[ $CURRENT_URL == *"127.0.0.1"* ]]; then
    echo "✅ Mobile app is configured for LOCAL backend"
    echo ""
    echo "Make sure local backend is running:"
    echo "   cd ../../backend/mcp-server"
    echo "   python3 http_server.py"
    echo ""
elif [[ $CURRENT_URL == *"mcp-agent.com"* ]]; then
    echo "☁️  Mobile app is configured for MCP CLOUD backend"
    echo ""
    echo "Note: MCP Cloud may not have the /query-pois endpoint"
    echo "Consider switching to local backend for testing"
    echo ""
else
    echo "⚠️  Unknown backend configuration"
    echo ""
fi

echo "=============================================="
echo ""
echo "🔄 To switch backends:"
echo ""
echo "  Local Backend (recommended for development):"
echo "    sed -i '' 's|EXPO_PUBLIC_MCP_SERVER_URL=.*|EXPO_PUBLIC_MCP_SERVER_URL=http://localhost:8000|' ../../frontend/expo-app/.env"
echo ""
echo "  MCP Cloud Backend:"
echo "    sed -i '' 's|EXPO_PUBLIC_MCP_SERVER_URL=.*|EXPO_PUBLIC_MCP_SERVER_URL=https://15csm9y282hdasy6yvu2l7244j9vcrfc.deployments.mcp-agent.com|' ../../frontend/expo-app/.env"
echo ""
echo "After changing, reload your Expo app (press 'r')"
echo ""
