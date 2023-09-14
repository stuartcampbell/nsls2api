from starlette.requests import Request

from nsls2api.viewmodels.proposals.details_viewmodel import DetailsViewModel


class ProposalDiagnosticsViewModel(DetailsViewModel):
    def __init__(self, proposal_id: int, request: Request):
        super().__init__(proposal_id, request)
