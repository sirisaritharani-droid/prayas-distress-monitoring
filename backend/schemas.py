from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    role: str = "survivor"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    anonymous_case_id: str

class ConsentRequest(BaseModel):
    accepted: bool
    share_optional_signals: bool

class CheckInCreate(BaseModel):
    mood: float = Field(ge=1, le=10)
    stress: float = Field(ge=1, le=10)
    anxiety: float = Field(ge=1, le=10)
    sleep_hours: float = Field(ge=0, le=24)
    social_connection: float = Field(ge=1, le=10)
    safety: float = Field(ge=1, le=10)
    energy: float = Field(ge=1, le=10)
    optional_text: Optional[str] = None
    custom_timestamp: Optional[datetime] = None

class CheckInResponse(BaseModel):
    id: int
    timestamp: datetime
    mood: float
    stress: float
    anxiety: float
    sleep_hours: float
    social_connection: float
    safety: float
    energy: float

    class Config:
        from_attributes = True

class RiskEstimateResponse(BaseModel):
    disclaimer: str = "PRAYAS provides an AI-assisted distress-risk estimate for support prioritization. It is not a medical diagnosis and does not replace qualified mental-health professionals."
    anonymous_case_id: str
    risk_level: str
    risk_probability: float
    risk_percentage: int
    confidence: float
    trend_direction: str
    action_recommendation: str
    explanations: List[Dict[str, Any]]
    baseline: Dict[str, float]

class CounsellorCaseSummary(BaseModel):
    case_id: str
    user_db_id: int
    risk_level: str
    risk_percentage: int
    trend: str
    last_checkin_date: Optional[str]
    followup_status: str
    needs_attention: bool

class CounsellorUpdateFollowup(BaseModel):
    case_id: str
    status: str
    notes: Optional[str] = None
