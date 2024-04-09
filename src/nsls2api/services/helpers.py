import httpx
import httpx_socks
from httpx import Response

from nsls2api.infrastructure import config
from nsls2api.models.validation_error import ValidationError

settings = config.get_settings()


async def _call_async_webservice(url: str, headers: dict = None) -> Response:
    transport = None

    if settings.use_socks_proxy:
        transport = httpx_socks.AsyncProxyTransport.from_url(settings.socks_proxy)

    async with httpx.AsyncClient(
        timeout=httpx.Timeout(5.0, read=20.0), transport=transport
    ) as client:
        resp: Response = await client.get(url)
        if resp.status_code != 200:
            raise ValidationError(resp.text, status_code=resp.status_code)
    results = resp.json()
    return results
