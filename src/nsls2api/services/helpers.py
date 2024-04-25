import httpx
import httpx_socks
from httpx import Response

from nsls2api.infrastructure import config
from nsls2api.infrastructure.logging import logger

settings = config.get_settings()


class HTTPXClientWrapper:
    async_client = None

    def start(self):
        self.async_client = httpx.AsyncClient()
        logger.info(f"HTTPXClientWrapper started. {id(self.async_client)}")

    async def stop(self):
        logger.info(f"HTTPXClientWrapper stopped. {id(self.async_client)}")
        await self.async_client.aclose()

    def __call__(self):
        # logger.info(f"HTTPXClientWrapper called. {id(self.async_client)}")
        return self.async_client


async def _call_async_webservice(
    url: str,
    headers: dict = None,
) -> Response:
    transport = None

    if settings.use_socks_proxy:
        transport = httpx_socks.AsyncProxyTransport.from_url(settings.socks_proxy)

    async with httpx.AsyncClient(
        timeout=httpx.Timeout(5.0, read=20.0),
        transport=transport,
        limits=httpx.Limits(max_keepalive_connections=5, max_connections=5),
    ) as client:
        logger.debug(f"Calling {url}")
        resp: Response = await client.get(url)
        resp.raise_for_status()
        # if resp.status_code != 200:
        #      raise ValidationError(resp.text, status_code=resp.status_code)
    results = resp.json()
    return results


async def _call_async_webservice_with_client(
    url: str, headers: dict = None, client: httpx.AsyncClient = None
) -> Response:
    if client is None:
        # Then just use the general method that creates a client each time
        return await _call_async_webservice(url, headers)
    else:
        resp: Response = await client.get(url)
        resp.raise_for_status()
        results = resp.json()
        return results
