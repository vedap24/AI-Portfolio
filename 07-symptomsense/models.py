from pydantic import BaseModel, field_validator
from typing import List

class TriageResult(BaseModel):
    triage_level: str
    urgency_score: int
    reasoning: str
    red_flags_present: List[str]
    red_flags_to_watch: List[str]
    immediate_steps: List[str]
    what_to_tell_doctor: List[str]
    disclaimer: str

    @field_validator("triage_level")
    @classmethod
    def validate_triage_level(cls, v):
        valid = [
            "SEEK_EMERGENCY",
            "SEE_DOCTOR",
            "MONITOR_HOME"
        ]
        if v not in valid:
            # Default to SEE_DOCTOR on invalid
            # — never default down to MONITOR_HOME
            return "SEE_DOCTOR"
        return v

    @field_validator("urgency_score")
    @classmethod
    def validate_urgency_score(cls, v):
        # Clamp between 1-10
        return max(1, min(10, int(v)))

    @field_validator("disclaimer")
    @classmethod
    def ensure_disclaimer(cls, v):
        # Disclaimer is non-negotiable
        # Even if Gemini removes it, we add it back
        if not v or len(v) < 20:
            return (
                "I am a triage assistant, not a "
                "medical professional. This is not "
                "a diagnosis or medical advice. "
                "Always consult a qualified "
                "healthcare provider."
            )
        return v


class PatientInput(BaseModel):
    symptoms: str
    age: str
    duration: str
    severity: int
    context: str = ""

    @field_validator("symptoms")
    @classmethod
    def validate_symptoms(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError(
                "Please describe your symptoms "
                "in at least 10 characters."
            )
        if len(v) > 2000:
            raise ValueError(
                "Symptom description too long. "
                "Max 2000 characters."
            )
        return v.strip()

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, v):
        if not 1 <= v <= 10:
            raise ValueError(
                "Severity must be between 1 and 10."
            )
        return v

    @field_validator("age")
    @classmethod
    def validate_age(cls, v):
        if not v or not v.strip():
            raise ValueError(
                "Please provide patient age."
            )
        return v.strip()