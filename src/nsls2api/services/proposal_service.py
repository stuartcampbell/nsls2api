from pathlib import Path
from typing import Optional

from beanie.odm.operators.find.array import ElemMatch
from beanie.operators import In, Text, RegEx

# from models.proposals import Proposal
from nsls2api.models.proposals import Proposal, User, ProposalIdView
from nsls2api.api.models.proposal_model import ProposalSummary
from nsls2api.services import beamline_service, pass_service


async def exists(proposal_id: int) -> bool:
    proposal = await Proposal.find_one(Proposal.proposal_id == str(proposal_id))
    return False if proposal is None else True


async def proposal_count() -> int:
    return await Proposal.count()


async def recently_updated(count=5, beamline: str | None = None):
    """
    Function to fetch recently updated proposals.

    :param beamline:
    :param count: Specifies the number of recently updated proposals to fetch. Defaults to 5.
    :type count: int

    :return: List of recently updated proposals.
    :rtype: list[Proposal]

    Args:
        beamline: Optional beamline to restrict list of proposals for.
    """
    if beamline:
        # Ensure we match the case in the database for the beamline name
        beamline = beamline.upper()
        # print(f"Searching for proposals within {beamline}...")
        query = In(Proposal.instruments, [beamline])
        updated = (
            await Proposal.find_many(query)
            .sort(-Proposal.last_updated)
            .limit(count)
            .to_list()
        )
    else:
        updated = (
            await Proposal.find_many()
            .sort(-Proposal.last_updated)
            .limit(count)
            .to_list()
        )
    return updated


async def fetch_proposals_for_cycle(cycle: str) -> list[str]:
    proposals = await Proposal.find(In(Proposal.cycles, [cycle])).to_list()
    print(proposals)
    result = [u.proposal_id for u in proposals if u.proposal_id is not None]
    return result


async def fetch_data_sessions_for_username(username: str) -> list[str]:
    proposals = await Proposal.find(
        ElemMatch(Proposal.users, {"username": username})
    ).to_list()
    data_sessions = [p.data_session for p in proposals if p.data_session is not None]
    return data_sessions


async def proposal_by_id(proposal_id: int) -> Optional[Proposal]:
    """
    Retrieve a proposal by its ID.

    :param proposal_id: The ID of the proposal to retrieve.
    :return: The proposal if found, or None if not found.
    """

    if not proposal_id:
        return None

    proposal: Proposal = await Proposal.find_one(
        Proposal.proposal_id == str(proposal_id)
    )

    if proposal is None:
        raise LookupError(f"Could not find a proposal with an ID of {proposal_id}")

    return proposal


async def fetch_proposals():  # -> Optional[list[ProposalSummary]]:
    proposals = await Proposal.find_all().to_list()
    # proposal_list = [ProposalSummary(**p) for p in proposals]
    proposal_list = []
    for proposal in proposals:
        # proposal_summary = ProposalSummary(proposal**)
        proposal_list.append()
    return proposal_list


async def fetch_users_on_proposal(proposal_id: int) -> Optional[list[User]]:
    proposal = await proposal_by_id(proposal_id)
    return proposal.users


async def fetch_usernames_from_proposal(
    proposal_id: int,
) -> Optional[list[str]]:
    proposal = await proposal_by_id(proposal_id)

    if proposal is None:
        raise LookupError(f"Proposal {proposal_id} not found")

    usernames = [u.username for u in proposal.users if u.username is not None]
    return usernames


async def pi_from_proposal(proposal_id: int) -> Optional[list[User]]:
    proposal = await proposal_by_id(proposal_id)

    pi = [u for u in proposal.users if u.is_pi]

    if len(pi) == 0:
        raise LookupError(f"Proposal {proposal_id} does not contain any PIs.")
    elif len(pi) > 1:
        raise LookupError(f"Proposal {proposal_id} contains {len(pi)} different PIs.")
    else:
        return pi


# TODO: There seems to be a data integrity issue that not all commissioning proposals have a beamline listed.
async def commissioning_proposals(beamline: str | None = None):
    if beamline:
        # Ensure we match the case in the database for the beamline name
        beamline = beamline.upper()

        query = In(Proposal.instruments, [beamline])
        proposals = Proposal.find(In(Proposal.instruments, [beamline])).find(
            Proposal.pass_type_id == "300005"
        )
    else:
        proposals = Proposal.find(
            Proposal.pass_type_id == "300005", projection_model=ProposalIdView
        )

    commissioning_proposal_list = [
        p.proposal_id for p in await proposals.to_list() if p.proposal_id is not None
    ]

    return commissioning_proposal_list


async def has_valid_cycle(proposal: Proposal):
    # If we don't have any cycles listed and this is not a commissioning
    # proposal then the cycle information is invalid
    return not (
        (len(proposal.cycles) == 0)
        and (
            proposal.pass_type_id != 300005
            or proposal.type == "Beamline Commissioning (beamline staff only)"
        )
    )


async def is_commissioning(proposal: Proposal):
    return (
        proposal.pass_type_id == "300005"
        or proposal.type == "Beamline Commissioning (beamline staff only)"
    )


async def search_proposals(search_text: str) -> list[Proposal]:
    results: list[Proposal] = []

    query = Text(search=search_text, case_sensitive=False)

    # Not sure we need to sort here - but hey why not!
    found_proposals = (
        await Proposal.find(query).sort([("score", {"$meta": "textScore"})]).to_list()
    )

    # Now do a special search just for the proposal id
    found_proposals += await Proposal.find(
        RegEx(Proposal.proposal_id, pattern=f"{search_text}")
    ).to_list()

    return found_proposals


# Return the directories and permissions that should be present for a given proposal
async def directories(proposal_id: int):
    proposal = await proposal_by_id(proposal_id)

    # if any of the following are null or zero length, then we don't have
    # enough information to create any directories
    insufficient_information = False
    error_msg = []

    if proposal.data_session is None:
        insufficient_information = True
        error_msg.append(
            f"Proposal {str(proposal.proposal_id)} does not contain a data_session."
        )

    if not await has_valid_cycle(proposal):
        insufficient_information = True
        error_msg.append(
            f"Proposal {str(proposal.proposal_id)} does not contain any cycle information."
        )

    if len(proposal.instruments) == 0:
        insufficient_information = True
        error_msg.append(
            f"Proposal {str(proposal.proposal_id)} does not contain any beamlines."
        )

    if len(error_msg) > 0:
        raise Exception(error_msg)

    directory_list = []

    for beamline in proposal.instruments:
        data_root = Path(await beamline_service.data_root_directory(beamline))
        # print(f"Data Root ({beamline}) = {data_root}")

        service_accounts = await beamline_service.service_accounts(beamline)
        # print(f"service_accounts: {service_accounts}")

        if is_commissioning(proposal):
            cycles = ["commissioning"]
        else:
            cycles = proposal.cycles

        for cycle in cycles:
            beamline_tla = str(beamline).lower()

            users_acl: list[dict[str, str]] = []
            groups_acl: list[dict[str, str]] = []

            users_acl.append({"nsls2data": "rw"})
            users_acl.append({f"{service_accounts.workflow}": "rw"})
            users_acl.append({f"{service_accounts.ioc}": "rw"})
            groups_acl.append({str(proposal.data_session): "rw"})

            # Add LSDC beamline users for the appropriate beamlines (i.e. if the account is defined)
            if service_accounts.lsdc:
                users_acl.append({f"{service_accounts.lsdc}": "rw"})

            groups_acl.append({"n2sn-right-dataadmin": "rw"})
            groups_acl.append({f"n2sn-right-dataadmin-{beamline_tla}": "rw"})

            directory = {
                "path": data_root / "proposals" / str(cycle) / proposal.data_session,
                "owner": "nsls2data",
                "group": proposal.data_session,
                "group_writable": True,
                "users": users_acl,
                "groups": groups_acl,
            }
            directory_list.append(directory)

    return directory_list


def create_or_update_proposal(proposal_id):
    # Does the proposal already exist in our system
    proposal_exists = exists(proposal_id)

    # Let's see what PASS has for this proposal.
    pass_proposal = pass_service.get_proposal(proposal_id)

    proposal = Proposal(proposal_id=pass_proposal)
