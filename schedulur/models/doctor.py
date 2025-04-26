from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import time

class Doctor(BaseModel):
    id: Optional[str] = None
    name: str
    specialization: str
    location: str
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    
    # Availability information - this will be synced with external data
    available_days: List[int] = []  # 0 = Monday, 6 = Sunday
    available_times: List[dict] = []  # List of {day: int, start_time: time, end_time: time}
    
    # Insurance accepted
    accepted_insurance: List[str] = []
    
    # Average appointment duration in minutes
    appointment_duration: int = 30
    
    # Notes about this doctor
    notes: Optional[str] = None
    
    # Preferred contact method
    preferred_contact: str = "phone"  # phone, email