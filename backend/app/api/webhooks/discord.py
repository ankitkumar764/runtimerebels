# Note: Discord uses WebSockets (Gateway API) instead of traditional webhooks.
# The WebSocket listener is implemented inside app/services/discord.py and
# integrated into the FastAPI lifespan startup in app/api/routes.py.
