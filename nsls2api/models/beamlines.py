import datetime
from typing import Optional

import beanie
import pydantic
from pydantic import Field


class Detector(pydantic.BaseModel):
    name: str


class BeamlineService(pydantic.BaseModel):
    name: str
    host: Optional[str]
    port: Optional[int]
    uri: Optional[str]


class ServiceAccounts(pydantic.BaseModel):
    ioc: Optional[str]
    workflow: Optional[str]
    bluesky: Optional[str]
    epics_services: Optional[str]
    operator: Optional[str]


class EndStation(pydantic.BaseModel):
    name: str
    service_accounts: Optional[ServiceAccounts]


class Beamline(beanie.Document):
    name: str
    long_name: Optional[str]
    alternative_name: Optional[str]
    port: str
    network_locations: Optional[list[str]]
    pass_name: Optional[str]
    pass_id: Optional[str]
    nsls2_redhat_satellite_location_name: Optional[str]
    service_accounts: ServiceAccounts
    endstations: Optional[list[EndStation]]
    data_admins: Optional[list[str]]
    github_org: Optional[str]
    ups_id: Optional[str]
    services: Optional[list[BeamlineService]]
    created_on: datetime.datetime = pydantic.Field(default_factory=datetime.datetime.now)
    last_updated: datetime.datetime = pydantic.Field(default_factory=datetime.datetime.now)

    class Settings:
        name = 'beamlines'
        indexes = []


class ServicesOnly(pydantic.BaseModel):
    services: list[BeamlineService]

    class Settings:
        projection = {
            "services": "$services",
        }
