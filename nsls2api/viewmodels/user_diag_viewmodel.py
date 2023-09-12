from typing import Optional

from starlette.requests import Request

from nsls2api.api.models.person_model import Person
from nsls2api.services import person_service
from nsls2api.viewmodels.shared.viewmodelbase import ViewModelBase


class UserDiagnosticsViewModel(ViewModelBase):
    def __int__(self, request: Request):
        super().__init__(request)
        self.person: Optional[Person] = None

        async def load(self):
            self.person = await person_service.diagnostic_details_by_username(self.username)
