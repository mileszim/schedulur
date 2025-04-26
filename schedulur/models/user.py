from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import time

class UserAvailability(BaseModel):
    days: List[int] = []  # 0 = Monday, 6 = Sunday
    time_slots: List[Dict] = []  # [{"day": 0, "start": "09:00", "end": "17:00"}, ...]

class User(BaseModel):
    id: Optional[str] = None
    name: str
    email: str
    phone: Optional[str] = None
    
    # Insurance information
    insurance_provider: Optional[str] = None
    insurance_id: Optional[str] = None
    
    # Scheduling preferences
    scheduling_preferences: Optional[Dict] = None
    
    # User preferences
    preferred_contact_method: str = "email"  # email, sms, call
    availability: Optional[UserAvailability] = None
    max_travel_distance_miles: Optional[int] = 25
    
    # Urgency - prioritize appointments that can be scheduled sooner
    urgency_level: int = Field(1, ge=1, le=5)  # 1-5 scale, 5 being most urgent
    
    # Location
    zip_code: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None