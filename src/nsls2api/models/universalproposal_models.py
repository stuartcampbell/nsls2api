import pydantic

from pydantic import ConfigDict

class ServiceNowValue(pydantic.BaseModel):
    value: str
    display_value: str

class ServiceNowValueWithLink(ServiceNowValue):
    link: str

class UpsProposalType(pydantic.BaseModel):
    sys_id: ServiceNowValue
    u_name: ServiceNowValue
    u_active: ServiceNowValue
    u_facility: ServiceNowValue
    u_type: ServiceNowValue


class UpsProposalRecord(pydantic.BaseModel):
    sys_id: ServiceNowValue
    u_proposal_number: ServiceNowValue 
    u_proposal_type: ServiceNowValue
    u_keywords: ServiceNowValue
    u_expired: ServiceNowValue
    u_active: ServiceNowValue
    u_principal_investigator_pi: ServiceNowValue
    u_display_name: ServiceNowValue
    u_review_status: ServiceNowValue
    u_project_created: ServiceNowValue
    u_proprietary: ServiceNowValue
    u_proposal_call: ServiceNowValueWithLink
    u_status: ServiceNowValue
    u_number: ServiceNowValue
    u_proposal_id: ServiceNowValue
    u_title: ServiceNowValue
