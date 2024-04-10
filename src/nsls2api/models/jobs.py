import datetime
from typing import Optional

import beanie
import pydantic
import pymongo

from enum import StrEnum
# If we want to use Python < 3.11 then replace the above line with
# from strenum import StrEnum


class JobStatus(StrEnum):
    awaiting = "awaiting"
    processing = "processing"
    unneeded = "unneeded"
    failed = "failed"
    success = "success"


class JobActions(StrEnum):
    synchronize_proposal = "synchronize_proposal"
    synchronize_proposal_types = "synchronize_proposal_types"
    create_slack_channel = "create_slack_channel"


class BackgroundJob(beanie.Document):
    created_date: datetime.datetime = pydantic.Field(
        default_factory=datetime.datetime.now
    )
    started_date: Optional[datetime.datetime] = None
    finished_date: Optional[datetime.datetime] = None
    processing_status: str = JobStatus.awaiting
    is_finished: bool = False
    action: str
    proposal_id: Optional[str] = None

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
                keys=[("proposal_id", pymongo.ASCENDING)], name="proposal_ascend"
            ),
            pymongo.IndexModel(
                keys=[("created_date", pymongo.ASCENDING)],
                name="created_date_expiring",
                expireAfterSeconds=int(datetime.timedelta(days=7).total_seconds()),
            ),
        ]
