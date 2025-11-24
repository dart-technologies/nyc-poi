#!/bin/bash
# Update Expo app .env with ngrok URL

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🔄 Updating Expo App Configuration${NC}\n"

# Get ngrok URL
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | python3 -c "import sys, json; data = json.load(sys.stdin); print(data['tunnels'][0]['public_url'] if data.get('tunnels') else '')" 2>/dev/null)

if [ -z "$NGROK_URL" ]; then
    echo -e "${YELLOW}⚠️  ngrok not running, using localhost${NC}"
    API_URL="http://localhost:8000"
else
    echo -e "${GREEN}✅ ngrok URL found: ${NGROK_URL}${NC}"
    API_URL="$NGROK_URL"
fi

# Update .env file
ENV_FILE=".env"

if [ ! -f "$ENV_FILE" ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    cp .env.template "$ENV_FILE"
fi

# Update or add MCP server URL
if grep -q "EXPO_PUBLIC_MCP_SERVER_URL" "$ENV_FILE"; then
    # Update existing line (macOS compatible)
    sed -i '' "s|EXPO_PUBLIC_MCP_SERVER_URL=.*|EXPO_PUBLIC_MCP_SERVER_URL=$API_URL|" "$ENV_FILE"
else
    # Add new line
    echo "EXPO_PUBLIC_MCP_SERVER_URL=$API_URL" >> "$ENV_FILE"
fi

echo -e "\n${GREEN}✅ Configuration updated!${NC}\n"
echo -e "${BLUE}API Endpoint: ${API_URL}${NC}"
echo -e "\n${YELLOW}💡 Restart your Expo app to apply changes:${NC}"
echo -e "   Press ${BLUE}r${NC} in the Expo terminal to reload\n"
