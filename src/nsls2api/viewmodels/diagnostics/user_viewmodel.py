from typing import Optional

from starlette.requests import Request

from nsls2api.models.person_models import Person
from nsls2api.services import person_service
from nsls2api.viewmodels.shared.viewmodelbase import ViewModelBase


class UserDiagnosticsViewModel(ViewModelBase):
    def __init__(self, username: str, request: Request):
        super().__init__(request)

        self.username = username
        self.person: Optional[Person] = None
        self.diagnostic_message: Optional[str] = None

    async def load(self):
        try:
            self.person = await person_service.diagnostic_details_by_username(
                self.username
            )
        except LookupError as error:
            self.error = f"{error}"
            # self.error = f"No user with a username of {self.username} could be found."
