from typing import Optional

import httpx

from nsls2api.cli.settings import get_base_url, get_token
from nsls2api.cli.utils.console import console


def call_nsls2api_endpoint(
    endpoint: str, method: str = "GET", data: dict = None
) -> Optional[httpx.Response]:
    """
    Call the NSLS-II API endpoint and return the response.
    """
    url = f"{get_base_url()}/{endpoint}"
    try:
        with httpx.Client() as client:
            token = get_token()
            headers = {"Authorization": f"{token}"} if token else {}
            if method == "GET":
                response = client.get(url, headers=headers)
            elif method == "POST":
                response = client.post(url, json=data, headers=headers)
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 401:
            console.print("[red]Invalid API token[/red]")
            return None
        elif exc.response.status_code == 403:
            console.print("[red]Access denied[/red]")
            return None
        elif exc.response.status_code == 404:
            console.print(f"[red]Endpoint not found: {url}[/red]")
            return None
        else:
            console.print(
                f"[red]An error occurred while trying to contact the API: {exc}[/red]"
            )
            return None
    except httpx.RequestError as exc:
        console.print(
            f"[red]An error occurred while trying to contact the API: {exc}[/red]"
        )
        return None
    return response
