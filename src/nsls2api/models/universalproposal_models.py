import pydantic

from pydantic import ConfigDict

class ServiceNowValue(pydantic.BaseModel):
    value: str
    display_value: str

class ServiceNowValueWithLink(ServiceNowValue):
    link: str | None = None

class UpsCycle(pydantic.BaseModel):
    """
    Representation of the sn_customerservice_run_cycle table.
    """
    sys_created_on: ServiceNowValue
    sys_id: ServiceNowValue
    sys_mod_count: ServiceNowValue
    sys_tags: ServiceNowValue
    sys_updated_on: ServiceNowValue
    u_active: ServiceNowValue
    u_end_date: ServiceNowValue
    u_facility: ServiceNowValueWithLink
    u_name: ServiceNowValue
    u_number: ServiceNowValue
    u_start_date: ServiceNowValue
    u_title: ServiceNowValue

class UpsProposalType(pydantic.BaseModel):
    sys_created_on: ServiceNowValue
    sys_id: ServiceNowValue
    sys_mod_count: ServiceNowValue
    sys_tags: ServiceNowValue
    sys_updated_on: ServiceNowValue
    u_name: ServiceNowValue
    u_active: ServiceNowValue
    u_facility: ServiceNowValueWithLink
    u_proposal_review_required: ServiceNowValue
    u_type: ServiceNowValue

class UpsUser(pydantic.BaseModel):
    active: ServiceNowValue
    avatar: ServiceNowValue
    building: ServiceNowValue
    email: ServiceNowValue
    first_name: ServiceNowValue
    last_login: ServiceNowValue
    last_login_time: ServiceNowValue
    last_name: ServiceNowValue
    location: ServiceNowValue
    middle_name: ServiceNowValue
    name: ServiceNowValue
    photo: ServiceNowValue
    source: ServiceNowValue
    sso_source: ServiceNowValue
    sys_created_on: ServiceNowValue
    sys_id: ServiceNowValue
    sys_mod_count: ServiceNowValue
    sys_tags: ServiceNowValueWithLink
    sys_updated_on: ServiceNowValue
    title: ServiceNowValue
    u_alternate_email: ServiceNowValue
    u_brookhaven_badge: ServiceNowValue
    u_country: ServiceNowValue
    u_employer_institution: ServiceNowValue
    u_employment_level: ServiceNowValue
    u_institution_name: ServiceNowValue
    u_keywords: ServiceNowValue
    u_missing_institution: ServiceNowValue
    u_orcid: ServiceNowValue
    u_slac_badge: ServiceNowValue
    user_name: ServiceNowValue
    web_service_access_only: ServiceNowValue

class UpsProposalRecord(pydantic.BaseModel):
    sys_class_name: ServiceNowValue
    sys_created_on: ServiceNowValue
    sys_id: ServiceNowValue
    sys_mod_count: ServiceNowValue
    sys_tags: ServiceNowValue
    sys_updated_on: ServiceNowValue
    u_abstract_of_proposed_research: ServiceNowValue
    u_active: ServiceNowValue
    u_age_count: ServiceNowValue
    u_co_proposers: ServiceNowValue
    u_contributor_users: ServiceNowValue
    u_display_name: ServiceNowValue
    u_etr_created: ServiceNowValue | None = None
    u_etr_questions_completed: ServiceNowValue | None = None
    u_etr_reviews_completed: ServiceNowValue | None = None
    u_expiration_date: ServiceNowValue
    u_expired: ServiceNowValue
    u_keywords: ServiceNowValue
    u_number: ServiceNowValue
    u_other_subject_of_research: ServiceNowValue
    u_primary_subject_of_research: ServiceNowValue
    u_principal_investigator_pi: ServiceNowValueWithLink
    u_progression_steps: ServiceNowValue
    u_project_created: ServiceNowValue
    u_proposal_call: ServiceNowValueWithLink
    u_proposal_id: ServiceNowValue
    u_proposal_number: ServiceNowValue
    u_proposal_questions_complete: ServiceNowValue
    u_proposal_submitter: ServiceNowValue
    u_proposal_type: ServiceNowValueWithLink
    u_proprietary: ServiceNowValue
    u_review_status: ServiceNowValue
    u_status: ServiceNowValue
    u_submission_date: ServiceNowValue
    u_supporting_documentation: ServiceNowValue
    u_title: ServiceNowValue

class UpsRunCycleProposalMapping(pydantic.BaseModel):
    sys_created_on: ServiceNowValue
    sys_id: ServiceNowValue
    sys_mod_count: ServiceNowValue
    sys_tags: ServiceNowValue
    sys_updated_on: ServiceNowValue
    u_available_start: ServiceNowValue
    u_available_end: ServiceNowValue
    u_proposal: ServiceNowValueWithLink
    u_run_cycle: ServiceNowValueWithLink

class UpsExperimentTimeRequest(pydantic.BaseModel):
    sys_created_on: ServiceNowValue
    sys_id: ServiceNowValue
    sys_mod_count: ServiceNowValue
    sys_tags: ServiceNowValue
    sys_updated_on: ServiceNowValue
    u_beamline_one: ServiceNowValueWithLink
    u_beamline_one_instrument: ServiceNowValueWithLink
    u_beamline_one_techique: ServiceNowValueWithLink
    u_beamline_two: ServiceNowValueWithLink
    u_beamline_two_instrument: ServiceNowValueWithLink
    u_beamline_two_technique: ServiceNowValueWithLink
    u_allocated_on: ServiceNowValue
    u_status: ServiceNowValue
    u_number: ServiceNowValue
    u_submission_date: ServiceNowValue
    u_title: ServiceNowValue
    u_proposal: ServiceNowValueWithLink
    u_run_cycle: ServiceNowValueWithLink

class UpsBeamline(pydantic.BaseModel):
    sys_created_on: ServiceNowValue
    sys_id: ServiceNowValue
    sys_mod_count: ServiceNowValue
    sys_tags: ServiceNowValue
    sys_class_name: ServiceNowValue
    sys_updated_on: ServiceNowValue
    u_beamline_long_name: ServiceNowValue
    u_shift_types: ServiceNowValue
    u_order: ServiceNowValue
    u_techniques: ServiceNowValue
    u_beamline_group: ServiceNowValueWithLink
    u_instruments: ServiceNowValue
    u_proposal_review_panel: ServiceNowValue
    u_keywords: ServiceNowValue
    u_description: ServiceNowValue
    u_active: ServiceNowValue
    u_facility: ServiceNowValueWithLink
    u_beamline: ServiceNowValue
    u_status: ServiceNowValue
    
