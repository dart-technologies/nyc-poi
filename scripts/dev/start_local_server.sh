#!/bin/bash
# NYC POI Concierge - Local Development Server with ngrok
# Starts HTTP API server and exposes it via ngrok tunnel

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 NYC POI Concierge - Local Dev Server${NC}"
echo -e "${BLUE}===========================================${NC}\n"

# Start HTTP server in background
echo -e "${YELLOW}🌐 Starting HTTP API server on port 8000...${NC}"
python3 http_server.py &
SERVER_PID=$!

# Wait for server to start
sleep 3

# Check if server is running
if ! ps -p $SERVER_PID > /dev/null; then
    echo -e "${RED}❌ Failed to start HTTP server${NC}"
    exit 1
fi

echo -e "${GREEN}✅ HTTP server running (PID: $SERVER_PID)${NC}"
echo -e "${BLUE}📍 Local: http://localhost:8000${NC}"
echo -e "${BLUE}📖 Docs: http://localhost:8000/docs${NC}"

# Start ngrok tunnel
echo -e "\n${YELLOW}🌍 Starting ngrok tunnel...${NC}"
ngrok http 8000 &
NGROK_PID=$!

# Wait for ngrok to start
sleep 2

echo -e "${GREEN}✅ ngrok tunnel started (PID: $NGROK_PID)${NC}"
echo -e "\n${BLUE}===========================================${NC}"
echo -e "${GREEN}🎉 Server is ready!${NC}\n"
echo -e "${YELLOW}📱 To get your public ngrok URL:${NC}"
echo -e "   1. Visit: ${BLUE}http://localhost:4040${NC} (ngrok web interface)"
echo -e "   2. Or run: ${BLUE}curl http://localhost:4040/api/tunnels | jq '.tunnels[0].public_url'${NC}\n"
echo -e "${YELLOW}💡 Update your Expo app with the HTTPS URL from ngrok${NC}\n"
echo -e "${RED}🛑 Press Ctrl+C to stop both servers${NC}\n"

# Cleanup function
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down servers...${NC}"
    kill $SERVER_PID 2>/dev/null || true
    kill $NGROK_PID 2>/dev/null || true
    echo -e "${GREEN}✅ Servers stopped${NC}"
    exit 0
}

# Trap Ctrl+C
trap cleanup INT TERM

# Wait for user to stop
wait
