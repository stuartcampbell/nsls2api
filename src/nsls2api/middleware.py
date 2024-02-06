import time

from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send


class ProcessTimeMiddleware:
    app: ASGIApp

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        start_time = time.perf_counter()

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                end_time = time.perf_counter()
                lapsed_time = (end_time - start_time) * 1000
                headers["Server-Timing"] = f"total;dur={lapsed_time:.3f} ms"
            await send(message)

        await self.app(scope, receive, send_wrapper)
