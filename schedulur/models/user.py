from pydantic import BaseModel
from typing import List, Optional
from datetime import time

class User(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    calendar_id: Optional[str] = None
    
    # Insurance information
    insurance_provider: Optional[str] = None
    insurance_id: Optional[str] = None
    
    # Preferences
    preferred_contact_time: Optional[dict] = None  # e.g., {"start": "09:00", "end": "17:00"}
    preferred_appointment_days: List[int] = []  # 0 = Monday, 6 = Sunday