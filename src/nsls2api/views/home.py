from pathlib import Path

import fastapi
import jinja_partials
from starlette.requests import Request
from starlette.templating import Jinja2Templates

from nsls2api.viewmodels.proposals.details_viewmodel import DetailsViewModel
from nsls2api.viewmodels.proposals.search_viewmodel import SearchViewModel

templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))
jinja_partials.register_starlette_extensions(templates)

router = fastapi.APIRouter()


@router.get("/", include_in_schema=False)
def index(request: Request):
    data = {"request": request}
    return templates.TemplateResponse("home/index.html", data)


# This is a test endpoint to make sure the server is running
# It is used by haproxy to determine if the server is healthy
@router.get("/healthy", include_in_schema=False)
async def healthy():
    return fastapi.responses.PlainTextResponse(
        "OK", status_code=fastapi.status.HTTP_200_OK
    )


@router.get("/default", include_in_schema=False)
def index(request: Request):
    data = {"request": request}
    return templates.TemplateResponse("home/default.html", data)


@router.get("/search/proposals", include_in_schema=False)
async def search_proposals(request: Request):
    vm = SearchViewModel(request)
    await vm.load()

    print(f"Searching for {vm.search_text}")
    if vm.is_htmx_request:
        return templates.TemplateResponse(
            "shared/partials/proposals_search_results.html", vm.to_dict()
        )

    return templates.TemplateResponse("home/proposals_search.html", vm.to_dict())


@router.get("/proposal-details", include_in_schema=False)
async def proposals(request: Request):
    vm = DetailsViewModel(311130, request)
    await vm.load()

    print(vm.to_dict())

    return templates.TemplateResponse("home/proposals.html", vm.to_dict())


@router.get("/favicon.ico", include_in_schema=False)
def favicon():
    return fastapi.responses.RedirectResponse(url="/static/images/favicon.ico")


@router.get("/favicon-16x16.png", include_in_schema=False)
def favicon16():
    return fastapi.responses.RedirectResponse(url="/static/images/favicon-16x16.png")


@router.get("/favicon-32x32.png", include_in_schema=False)
def favicon32():
    return fastapi.responses.RedirectResponse(url="/static/images/favicon-32x32.png")


@router.get("/site.webmanifest", include_in_schema=False)
def webmanifest():
    return fastapi.responses.RedirectResponse(url="/static/site.webmanifest")
