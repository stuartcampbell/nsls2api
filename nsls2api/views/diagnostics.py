import fastapi
from fastapi import HTTPException
from starlette.requests import Request
from starlette.templating import Jinja2Templates

from nsls2api.viewmodels.user_diag_viewmodel import UserDiagnosticsViewModel

templates = Jinja2Templates("templates")
router = fastapi.APIRouter()


@router.get("/diagnostics/username/{username}", include_in_schema=False)
async def diag_username(username: str, request: Request):
    vm = UserDiagnosticsViewModel(username, request)
    await vm.load()

    # if there was a problem in getting the information for a user then the error will not be None.
    if vm.error:
        raise HTTPException(status_code=404, detail=vm.error)

    print(vm.to_dict())

    return templates.TemplateResponse("diagnostics/diagnostics.html", vm.to_dict())
