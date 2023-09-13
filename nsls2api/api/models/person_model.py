from typing import Optional

import pydantic


class BNLPerson(pydantic.BaseModel):
    ActiveDirectoryName: Optional[str] = None
    AltEmail: Optional[str] = None
    AppointmentEndDate: Optional[str] = None
    BNLEmail: Optional[str] = None
    BNLExtension: Optional[str] = None
    BNLFax: Optional[str] = None
    BNLPager: Optional[str] = None
    BNLStreet: Optional[str] = None
    IsUSCitizen: Optional[bool] = None
    CyberAgreementSigned: Optional[str] = None
    DeliveryOffice: Optional[str] = None
    DepartmentCode: Optional[str] = None
    DepartmentId: Optional[int] = None
    DepartmentName: Optional[str] = None
    DisplayContactInformation: Optional[bool] = None
    EmployeeNumber: Optional[str] = None
    EmployeeStatus: Optional[str] = None
    EmployeeType: Optional[str] = None
    Facility: Optional[str] = None
    FacilityCode: Optional[str] = None
    FirstName: Optional[str] = None
    Institution: Optional[str] = None
    LastName: Optional[str] = None
    ManagerEmail: Optional[str] = None
    ManagerEmployeeNumber: Optional[str] = None
    ManagerFirstName: Optional[str] = None
    ManagerLastName: Optional[str] = None
    TermDate: Optional[str] = None
    TimeStamp: Optional[str] = None


class ActiveDirectoryUser(pydantic.BaseModel):
    sAMAccountName: Optional[str] = None
    distinguishedName: Optional[str] = None
    displayName: Optional[str] = None
    employeeID: Optional[str] = None
    mail: Optional[str] = None
    description: Optional[str] = None
    userPrincipalName: Optional[str] = None
    pwdLastSet: Optional[str] = None
    userAccountControl: Optional[str] = None
    lockoutTime: Optional[str] = None
    set_passwd: Optional[bool] = None
    locked: Optional[bool] = None
    was_locked: Optional[bool] = None


class ActiveDirectoryUserGroups(pydantic.BaseModel):
    sAMAccountName: Optional[str] = None
    distinguishedName: Optional[str] = None
    member: Optional[list[str]] = None
    memberOf: Optional[list[str]] = None


class Person(pydantic.BaseModel):
    firstname: str
    lastname: str
    email: str
    username: str
    bnl_id: Optional[str]
    institution: str
    account_locked: bool

class PersonSummary(pydantic.BaseModel):
    firstname: str
    lastname: str
    email: str
    username: str
    institution: str
