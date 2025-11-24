
import uvicorn
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import Response
from mcp.server.sse import SseServerTransport
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions
import sys
from pathlib import Path

# Add current directory to sys.path to import server
sys.path.append(str(Path(__file__).parent))

from server import server, init_mongo

# Create SSE transport
sse = SseServerTransport("/messages")

async def handle_sse(request):
    async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
        await server.run(
            streams[0], 
            streams[1], 
            InitializationOptions(
                server_name="nyc-poi-concierge",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            )
        )

async def handle_messages(request):
    await sse.handle_post_message(request.scope, request.receive, request._send)

routes = [
    Route("/sse", endpoint=handle_sse),
    Route("/messages", endpoint=handle_messages, methods=["POST"]),
]

app = Starlette(debug=True, routes=routes)

@app.on_event("startup")
async def startup():
    print("🚀 Starting SSE Server...")
    success = await init_mongo()
    if not success:
        print("❌ Failed to initialize MongoDB")
        sys.exit(1)

if __name__ == "__main__":
    # Run on 0.0.0.0 to be accessible via LAN
    uvicorn.run(app, host="0.0.0.0", port=8000)
