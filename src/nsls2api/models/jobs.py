import datetime
from enum import StrEnum
from typing import Optional

import beanie
import pydantic
import pymongo

from nsls2api.api.models.facility_model import FacilityName

# If we want to use Python < 3.11 then replace the above line with
# from strenum import StrEnum


class JobStatus(StrEnum):
    awaiting = "awaiting"
    processing = "processing"
    unneeded = "unneeded"
    failed = "failed"
    success = "success"


class JobSyncSource(StrEnum):
    PASS = "PASS"
    universal_proposal_system = "universal_proposal_system"


class JobActions(StrEnum):
    synchronize_admins = "synchronize_admins"
    synchronize_cycles = "synchronize_cycles"
    synchronize_proposal = "synchronize_proposal"
    synchronize_proposals_for_cycle = "synchronize_proposals_for_cycle"
    synchronize_proposal_types = "synchronize_proposal_types"
    update_cycle_information = "update_cycle_information"
    create_slack_channel = "create_slack_channel"


class JobSyncParameters(pydantic.BaseModel):
    proposal_id: Optional[str] = None
    facility: Optional[FacilityName] = None
    year: Optional[int] = None
    cycle: Optional[str] = None
    proposal_type_id: Optional[str] = None
    beamline: Optional[str] = None
    sync_source: Optional[JobSyncSource] = JobSyncSource.PASS


class BackgroundJob(beanie.Document):
    created_date: datetime.datetime = pydantic.Field(
        default_factory=datetime.datetime.now
    )
    started_date: Optional[datetime.datetime] = None
    finished_date: Optional[datetime.datetime] = None
    processing_status: str = JobStatus.awaiting
    is_finished: bool = False
    action: str
    sync_parameters: Optional[JobSyncParameters] = None
    log_message: Optional[str] = None

    class Settings:
        name = "jobs"
        indexes = [
            pymongo.IndexModel(
                keys=[("is_finished", pymongo.ASCENDING)], name="finished_ascend"
            ),
            pymongo.IndexModel(
                keys=[("processing_status", pymongo.ASCENDING)], name="status_ascend"
            ),
            pymongo.IndexModel(
                keys=[("sync_parameters.proposal_id", pymongo.ASCENDING)],
                name="proposal_ascend",
            ),
            pymongo.IndexModel(
                keys=[("created_date", pymongo.ASCENDING)],
                name="created_date_expiring",
                expireAfterSeconds=int(datetime.timedelta(days=7).total_seconds()),
            ),
        ]
