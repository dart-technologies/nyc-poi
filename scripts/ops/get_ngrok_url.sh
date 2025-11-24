#!/bin/bash
# Get the current ngrok public URL

NGROK_URL=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | python3 -c "import sys, json; data = json.load(sys.stdin); print(data['tunnels'][0]['public_url'] if data.get('tunnels') else 'Not running')" 2>/dev/null)

if [ "$NGROK_URL" = "Not running" ] || [ -z "$NGROK_URL" ]; then
    echo "❌ ngrok is not running"
    echo "Run: ./start_local_server.sh"
    exit 1
fi

echo "✅ ngrok Public URL:"
echo "$NGROK_URL"
echo ""
echo "📱 Update your Expo app with this URL"
echo "🌐 View ngrok dashboard: http://localhost:4040"
