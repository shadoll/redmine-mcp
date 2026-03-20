from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.responses import Response


class BearerAuthMiddleware:
    """
    ASGI middleware that enforces Bearer token authentication.
    Only active when MCP_AUTH_TOKEN is set — if empty the request passes through.
    """

    def __init__(self, app: ASGIApp, token: str) -> None:
        self.app = app
        self.token = token

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http":
            headers = dict(scope.get("headers", []))
            auth = headers.get(b"authorization", b"").decode()
            if not auth.startswith("Bearer ") or auth[7:].strip() != self.token:
                response = Response("Unauthorized", status_code=401, media_type="text/plain")
                await response(scope, receive, send)
                return
        await self.app(scope, receive, send)
