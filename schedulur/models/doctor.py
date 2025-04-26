from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import time

class DoctorAvailability(BaseModel):
    days: List[int] = []  # 0 = Monday, 6 = Sunday
    time_slots: List[dict] = []  # [{"day": 0, "start": "09:00", "end": "17:00"}, ...]

class Doctor(BaseModel):
    id: Optional[str] = None
    name: str
    specialization: str
    npi: Optional[str] = None  # National Provider Identifier
    
    # Contact information
    email: Optional[str] = None
    phone: Optional[str] = None
    fax: Optional[str] = None
    
    # Practice information
    practice_name: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # Insurance and appointment details
    accepted_insurance: List[str] = []
    appointment_duration: int = 30  # Default duration in minutes
    
    # Availability information
    availability: Optional[DoctorAvailability] = None
    
    # Search metadata
    distance_miles: Optional[float] = None  # Distance from user's location
    earliest_available_slot: Optional[str] = None  # Earliest available appointment 
    
    # Call tracking
    has_been_called: bool = False
    call_notes: Optional[str] = None
    call_transcript: Optional[str] = None
    
    # User preferences
    user_approval: Optional[bool] = None  # Whether user has approved calling this doctor

    def to_dict(self) -> Dict:
        """Convert model to dictionary for easier JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "specialization": self.specialization,
            "practice_name": self.practice_name,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "zip_code": self.zip_code,
            "phone": self.phone,
            "email": self.email,
            "website": self.website,
            "accepted_insurance": self.accepted_insurance,
            "appointment_duration": self.appointment_duration,
            "distance_miles": self.distance_miles,
            "earliest_available_slot": self.earliest_available_slot,
            "has_been_called": self.has_been_called,
            "user_approval": self.user_approval
        }