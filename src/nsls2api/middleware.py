from starlette.types import ASGIApp, Message, Receive, Scope, Send
from starlette.datastructures import MutableHeaders
import time


class ProcessTimeMiddleware:
    app: ASGIApp

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        start_time = time.time()

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                end_time = time.time()
                process_time = end_time - start_time
                headers["x-process-time"] = str(process_time)
                headers["Server-Timing"] = f"total;dur={process_time:.3f}"
            await send(message)
        
        await self.app(scope, receive, send_wrapper)
