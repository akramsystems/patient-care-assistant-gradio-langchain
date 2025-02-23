from typing import TypedDict
from pydantic import BaseModel, field_validator
from typing import Any

class PatientData(BaseModel):
    name: str = ""
    dob: str = ""
    pcp: str = ""
    ehrId: str = ""
    appointments: str = ""
    referred_providers: str = ""
    insurance_provider: str = ""

    # validate all fields
    @field_validator('*', mode='before')
    @classmethod
    def validate_fields(cls, v: Any) -> str:
        if not isinstance(v, str):
            return str(v)
        return v

class State(TypedDict):
    patient_id: str
    patient_data: PatientData
    feedback_required: bool
    missing_info: list[str]
    care_recommendations: str
    human_input: str
    provider_availability: dict
    insurance_info: dict


# CONSTANTS

INITIAL_STATE = State(
    patient_id="",
    patient_data=PatientData(name="", dob="", pcp="", ehrId=""),
    missing_info=[],
    care_recommendations="",
    human_input="",
    feedback_required=False,
    provider_availability={},
    insurance_info={}
)