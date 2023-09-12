import fastapi
from starlette.requests import Request
from starlette.templating import Jinja2Templates

from nsls2api.viewmodels.user_diag_viewmodel import UserDiagnosticsViewModel

templates = Jinja2Templates('templates')
router = fastapi.APIRouter()

@router.get('/diagnostics/username/{username}', include_in_schema=False)
async def diag_username(username: str, request: Request):

    vm = UserDiagnosticsViewModel(username, request)
    await vm.load()

    print(vm.to_dict())

    return templates.TemplateResponse('diagnostics/diagnostics.html', vm.to_dict())

