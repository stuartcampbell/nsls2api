from nsls2api.models import (
    facilities,
    cycles,
    proposal_types,
    beamlines,
    proposals,
    apikeys,
    jobs,
)

all_models = [
    facilities.Facility,
    cycles.Cycle,
    proposal_types.ProposalType,
    beamlines.Beamline,
    proposals.Proposal,
    apikeys.ApiKey,
    apikeys.ApiUser,
    jobs.BackgroundJob,
]
