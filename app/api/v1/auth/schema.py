from datetime import date, datetime
from typing import List, Optional, Any

import pydantic
from pydantic import BaseModel, Field, HttpUrl


class User(BaseModel, extra="forbid"):
    user_id: int
    user_role: str
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = False
    user_registration_timestamp: Optional[date]


class UserInDB(User, extra="forbid"):
    hashed_password: str


class ApiUser(BaseModel, extra="forbid"):
    api_user_id: int


class Token(BaseModel, extra="forbid"):
    user_id: Optional[int]
    access_token: str
    token_type: str
    refresh_token: str


class TokenData(BaseModel, extra="forbid"):
    username: Optional[str] = None
    clientId: Optional[str] = None
    scopes: List[str] = []


class LogoutResponse(BaseModel, extra="forbid"):
    """
    Response for successful logout
    """

    data: Optional[str] = None
    message: str
    status: int
    success: bool


class TokenValidationResponse(BaseModel, extra="forbid"):
    """
    Response for a token validation
    """

    data: Optional[str] = None
    message: str
    status: int
    success: bool

class fileuploadvalidationResponse(BaseModel, extra="forbid"):
    """
    Response for a file upload validation
    """
    data: Optional[str] = None

class Organization(BaseModel, extra="forbid"):
    ORGANISATION_ID: Optional[int]
    ORGANISATION_NAME: Optional[str] = None
    ORGANISATION_VAT_ID: Optional[str] = None
    ORGANISATION_LEGAL_FORM: Optional[str] = None
    ORGANISATION_LEGAL_REGISTRATION_NUMBER: Optional[str] = None
    ORGANISATION_LEGAL_REGISTRY: Optional[str] = None
    ORGANISATION_STREET: Optional[str] = None
    ORGANISATION_ZIP: Optional[str] = None
    ORGANISATION_STATE: Optional[str] = None
    ORGANISATION_CITY: Optional[str] = None
    ORGANISATION_COUNTRY_ISO: Optional[str] = None
    ORGANISATION_CREATED: Optional[datetime]
    ORGANISATION_UPDATED: Optional[datetime] = None
    ORGANISATION_CREATED_BY: Optional[int] = None
    ORGANISATION_UPDATED_BY: Optional[int] = None
    ORGANISATION_LOGO_URL: Optional[str] = None
    ORGANISATION_PRIM_COLOR: Optional[str] = None
    ORGANISATION_SEC_COLOR: Optional[str] = None


class GetOrganizationsResponse(BaseModel, extra="forbid"):
    """
    Response for Get /organizations endpoint
    """
    response: List[dict]


class Esg_measures(BaseModel, extra='forbid'):
    ESG_MEASURE_ID: int
    ESG_MEASURE_PARENT_ID: Optional[int] = None
    ESG_MEASURE_KEY: Optional[str] = ""
    ESG_MEASURE_STATUS: Optional[int] = 1
    ESG_MEASURE_CREATED: Optional[datetime] = None
    ESG_MEASURE_UPDATED: Optional[datetime] = None
    ESG_MEASURE_CREATED_BY: Optional[int] = 1
    ESG_MEASURE_UPDATED_BY: Optional[int] = None

class GetEsgMeasuresResponse(BaseModel, extra="forbid"):
    "Response for Get /esg_measures endpoint"
    response: List[Esg_measures]


class Esg_Measure_Description(BaseModel, extra='forbid'):
    ESG_MEASURE_DESCRIPTION_ID: Optional[int]
    ESG_MEASURE_ID: Optional[int] = None
    ESG_MEASURE_DESCRIPTION: Optional[str] = None
    ESG_MEASURE_DESCRIPTION_TOPIC: Optional[int] = None
    ESG_MEASURE_DESCRIPTION_ANSWERS: Optional[str] = None
    ESG_MEASURE_DESCRIPTION_COUNTRY_ISO: Optional[str] = None
    ESG_MEASURE_DESCRIPTION_CREATED: Optional[datetime] = None
    ESG_MEASURE_DESCRIPTION_UPDATED: Optional[datetime] = None
    ESG_MEASURE_DESCRIPTION_CREATED_BY: Optional[int] = None
    ESG_MEASURE_DESCRIPTION_UPDATED_BY: Optional[int] = None
    ESG_MEASURE_DESCRIPTION_SHORT_NAME: Optional[str] = ""

class GetEsgMeasureDescriptionsResponse(BaseModel, extra="forbid"):
    "Response for Get /esg_measure_descriptions endpoint"
    response: List[Esg_Measure_Description]


class Esg_questionaires(BaseModel, extra='forbid'):
    ESG_QUESTIONAIRE_ID: Optional[int]  
    QUESTIONAIRE_TYPE: Optional[str] = None
    PERSON_ID: Optional[int] = None  
    ORGANISATION_ID : Optional[int] = None 
    QUESTIONAIRE_COMMENT : Optional[str] = None 
    QUESTIONAIRE_DATE : Optional[datetime] = None 
    ESG_QUESTIONAIRE_ANSWER_CREATED : Optional[datetime] = None 
    ESG_QUESTIONAIRE_ANSWER_UPDATED : Optional[datetime] = None 
    ESG_QUESTIONAIRE_ANSWER_CREATED_BY : Optional[int] = None 
    ESG_QUESTIONAIRE_ANSWER_UPDATED_BY : Optional[int] = None 
    RELATED_ORGANISATION_ID : Optional[int] = None

class getEsgQuestionairesResponse(BaseModel, extra='forbid'):
    "Response for Get /esg_questionaires endpoint"
    response: List[Esg_questionaires]

class Esg_Questionaires_answers(BaseModel, extra='forbid'):

    ESG_QUESTIONAIRE_ANSWER_ID:  Optional[int] 
    ESG_QUESTIONAIRE_ID:  Optional[int]
    ESG_MEASURE_ID:  Optional[int]
    STAKEHOLDER_ID:  Optional[int]
    ESG_QUESTIONAIRE_ANSWER_PRIORITY:  Optional[int]  
    ESG_QUESTIONAIRE_ANSWER_STATUS:  Optional[int]
    ESG_QUESTIONAIRE_ANSWER_COMMENTS: Optional[str] = None
    ESG_QUESTIONAIRE_ANSWER_COUNTRY_ISO: Optional[str]  = None
    ESG_QUESTIONAIRE_ANSWER_CREATED: Optional[datetime] = None
    ESG_QUESTIONAIRE_ANSWER_UPDATED:  Optional[datetime] = None
    ESG_QUESTIONAIRE_ANSWER_CREATED_BY:  Optional[int]= None
    ESG_QUESTIONAIRE_ANSWER_UPDATED_BY: Optional[int]= None
class getEsg_Questionaires_answers(BaseModel, extra='forbid'):
    response : list[Esg_Questionaires_answers]

class Person(BaseModel , extra = 'forbid'):

    PERSON_ID: Optional[int]
    STAKEHOLDER_ID: Optional[int]
    PERSON_SALUTATION: Optional[str] = None
    PERSON_FIRSTNAME: Optional[str] = None
    PERSON_LASTNAME: Optional[str] = None
    PERSON_GENDER: Optional[str] = None
    PERSON_PHONE: Optional[str] = None
    PERSON_MOBILE: Optional[str] = None
    PERSON_MAIL: Optional[str] = None
    PERSON_BIRTHDAY: Optional[int] = None
    PERSON_STREET: Optional[str] = None
    PERSON_ZIP: Optional[str] = None
    PERSON_STATE: Optional[str] = None
    PERSON_CITY: Optional[str] = None
    PERSON_COUNTRY_ISO: Optional[str] = None
    PERSON_CUSTOMER_FLAG: Optional[int] = None
    PERSON_COMMENTS: Optional[str] = None
    PERSON_CREATED: Optional[datetime] = None
    PERSON_UPDATED: Optional[datetime] = None
    PERSON_CREATED_BY: Optional[int] = None
    PERSON_UPDATED_BY: Optional[int] = None

class getPerson(BaseModel, extra = 'forbid'):
    response: list[Person]

class Stakeholder(BaseModel, extra = 'forbid'):
    STAKEHOLDER_ID : Optional[int] 
    STAKEHOLDER_PARENT_ID : Optional[int] = None
    STAKEHOLDER_NACE :  Optional[str] = None 
    STAKEHOLDER_CREATED : Optional[datetime] = None
    STAKEHOLDER_UPDATED : Optional[datetime] = None 
    STAKEHOLDER_CREATED_BY : Optional[int] = None 
    STAKEHOLDER_UPDATED_BY : Optional[int] = None

class getStakeholder(BaseModel, extra= 'forbid'):
    response : list[Stakeholder]

class Stakeholder_names(BaseModel, extra ='forbid'):
    STAKEHOLDER_NAME_ID :  Optional[int] 
    STAKEHOLDER_ID : Optional[int] 
    STAKEHOLDER_NAME :  Optional[str] = None 
    STAKEHOLDER_NAME_COUNTRY_ISO : Optional[str] = None
    STAKEHOLDER_NAME_CREATED : Optional[datetime] = None
    STAKEHOLDER_NAME_UPDATED : Optional[datetime] = None
    STAKEHOLDER_NAME_CREATED_BY : Optional[int] = None  
    STAKEHOLDER_NAME_UPDATED_BY : Optional[int] = None 

class getStakeholder_names(BaseModel, extra = 'forbid'):
    response : list[Stakeholder_names]


# customers
# Schema for individual grading within measureGradings
class MeasureGrading(BaseModel, extra="forbid"):
    """
    Schema for individual measure gradings within a customer.
    """
    key: str
    prio: int
    statusQuo: float = Field(..., alias="statusQuo")


class StakeholderGrading(BaseModel, extra="forbid"):
    """
    Schema for individual gradings within a stakeholder's measure gradings.
    """
    key: str
    prio: int


class StakeholderMeasureGrading(BaseModel, extra="forbid"):
    """
    Schema for stakeholder-specific measure gradings.
    """
    stakeholder: int
    gradings: List[StakeholderGrading]


class ChosenStakeholder(BaseModel, extra="forbid"):
    """
    Schema for chosen stakeholders with their weight and justification.
    """
    id: str
    weight: int
    justification: Optional[str] = None


class IROAssessment(BaseModel, extra="forbid"):
    """
    Schema for Impact, Risk, and Opportunity (IRO) assessment.
    """
    key: str
    impact: int
    risk: int
    opportunity: int
    justification: str
    chosen: bool


class IROSelection(BaseModel, extra="forbid"):
    """
    Schema for Impact, Risk, and Opportunity (IRO) selection.
    """
    key: str
    prio: float
    relevant: bool
    justification: str


class Customer(BaseModel, extra="forbid"):
    """
    Main schema for a Customer, including their various ESG-related data.
    """
    id: int
    name: str
    # measureGradings: List[MeasureGrading]
    # stakeholderMeasureGradings: List[StakeholderMeasureGrading] = Field(..., alias="stakeholderMeasureGradings")
    # chosenStakeholders: List[ChosenStakeholder] = Field(..., alias="chosenStakeholders")
    # iroAssessment: List[IROAssessment] = Field(..., alias="iroAssessment")
    # iroSelection: List[IROSelection] = Field(..., alias="iroSelection")
    # reportings: List[Any] 
    base64Image: Optional[str] = Field(None, alias="base64Image")


class GetCustomersResponse(BaseModel, extra="forbid"):
    """
    Response schema for fetching a list of Customer objects.
    """
    response: List[Customer]