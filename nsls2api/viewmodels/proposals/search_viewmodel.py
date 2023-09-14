from fastapi import Request

from nsls2api.models.proposals import Proposal
from nsls2api.viewmodels.shared.viewmodelbase import ViewModelBase


class SearchViewModel(ViewModelBase):
    def __init__(self, request: Request):
        super().__init__(request)

        self.search_text: str = request.get('search_text')
        self.proposals: list[Proposal] = []

    async def load(self):
        print(f"Searching for {self.search_text}")
