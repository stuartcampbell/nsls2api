from starlette.types import ASGIApp, Message, Receive, Scope, Send
from starlette.datastructures import MutableHeaders
import time
import logging
import http
from fastapi import Request

logger = logging.getLogger(__name__)

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


async def log_request(request: Request, call_next):
    url = (
        f"{request.url.path}?{request.query_params}"
        if request.query_params
        else request.url.path
    )
    start_time = time.monotonic()
    response = await call_next(request)
    end_time = time.monotonic()
    process_time = (end_time - start_time) * 1000
    formatted_process_time = "{0:.3f}".format(process_time)
    host = getattr(getattr(request, "client", None), "host", None)
    port = getattr(getattr(request, "client", None), "port", None)
    try:
        status_phrase = http.HTTPStatus(response.status_code).phrase
    except ValueError:
        status_phrase = ""
    logger.info(
        f'{host}:{port} - "{request.method} {url}" {response.status_code} {status_phrase} - {formatted_process_time} ms'
    )
    return response
