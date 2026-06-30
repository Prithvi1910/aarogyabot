from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class FacilityResult(BaseModel):
    name: str
    type: str
    district: str
    phone: Optional[str] = None
    distance_km: float

class ChatResponse(BaseModel):
    reply: str
    triage: Dict[str, Any]
    facilities: List[FacilityResult]
    session_id: str
    lang: str = "en"
    sources: List[str] = []

