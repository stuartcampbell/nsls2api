from uuid import UUID, uuid4

import beanie
from pydantic import Field


class PrincipalType(str, enum.Enum):
    user = "user"
    service = "service"


class Principal(beanie.Document):
    id: UUID = Field(default_factory=uuid4)
    type: PrincipalType
    identities: list[Identity] = []
    roles: list[Role] = []
    api_keys: list[APIKey] = []
    sessions: list[Session] = []
