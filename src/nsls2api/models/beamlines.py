import datetime
from typing import Optional

import beanie
import pydantic


class Detector(pydantic.BaseModel):
    name: str
    directory_name: str | None = None

class DetectorView(pydantic.BaseModel):
    detectors: list[Detector] | None = None
    
    class Settings:
        projection = {
            "detectors": "$detectors",
        }


class DetectorList(pydantic.BaseModel):
    detectors: list[Detector] | None = None
    count: int | None = None



class BeamlineService(pydantic.BaseModel):
    name: str
    host: Optional[str]
    port: Optional[int]
    uri: Optional[str]


class ServicesOnly(pydantic.BaseModel):
    services: list[BeamlineService] | None = None

    class Settings:
        projection = {
            "services": "$services",
        }


class ServiceAccounts(pydantic.BaseModel):
    ioc: Optional[str]
    workflow: Optional[str]
    bluesky: Optional[str]
    epics_services: Optional[str]
    operator: Optional[str]
    lsdc: Optional[str] = None

    class Settings:
        keep_nulls = False


class ServiceAccountsView(pydantic.BaseModel):
    service_accounts: Optional[ServiceAccounts]


class WorkflowServiceAccountView(pydantic.BaseModel):
    username: str

    class Settings:
        projection = {"username": "$service_accounts.workflow"}


class IOCServiceAccountView(pydantic.BaseModel):
    username: str

    class Settings:
        projection = {"username": "$service_accounts.ioc"}


class BlueskyServiceAccountView(pydantic.BaseModel):
    username: str

    class Settings:
        projection = {"username": "$service_accounts.bluesky"}


class OperatorServiceAccountView(pydantic.BaseModel):
    username: str

    class Settings:
        projection = {"username": "$service_accounts.operator"}


class EpicsServicesServiceAccountView(pydantic.BaseModel):
    username: str

    class Settings:
        projection = {"username": "$service_accounts.epics_services"}


class LsdcServiceAccountView(pydantic.BaseModel):
    username: str

    class Settings:
        projection = {"username": "$service_accounts.lsdc"}


class DataRootDirectoryView(pydantic.BaseModel):
    data_root: Optional[str] = None

    class Settings:
        projection = {"data_root": "$custom_root_directory"}


class EndStation(pydantic.BaseModel):
    name: str
    service_accounts: Optional[ServiceAccounts] = None


class Beamline(beanie.Document):
    name: str
    long_name: Optional[str]
    alternative_name: Optional[str]
    port: str
    network_locations: Optional[list[str]]
    pass_name: Optional[str]
    pass_id: Optional[str]
    nsls2_redhat_satellite_location_name: Optional[str]
    service_accounts: ServiceAccounts | None = None
    endstations: Optional[list[EndStation]]
    data_admins: Optional[list[str]]
    github_org: Optional[str]
    ups_id: Optional[str]
    data_root: Optional[str] = None
    services: Optional[list[BeamlineService]] = []
    detectors: Optional[list[Detector]] = []
    created_on: datetime.datetime = pydantic.Field(
        default_factory=datetime.datetime.now
    )
    last_updated: datetime.datetime = pydantic.Field(
        default_factory=datetime.datetime.now
    )

    class Settings:
        name = "beamlines"
        keep_nulls = False
        indexes = []
