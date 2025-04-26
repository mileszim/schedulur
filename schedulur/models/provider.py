from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, time

class Provider(BaseModel):
    id: Optional[str] = None
    name: str
    specialization: str
    location: str
    email: str
    phone: str
    
    # Availability information
    available_days: List[int] = []  # 0 = Monday, 6 = Sunday
    available_times: List[dict] = []  # List of {day: int, start_time: time, end_time: time}
    
    # Insurance accepted
    accepted_insurance: List[str] = []
    
    # Average appointment duration in minutes
    appointment_duration: int = 30