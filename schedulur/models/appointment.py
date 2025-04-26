from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Appointment(BaseModel):
    id: Optional[str] = None
    doctor_id: str
    start_time: datetime
    end_time: datetime
    status: str = "scheduled"  # scheduled, completed, cancelled
    notes: Optional[str] = None
    
    # Booking status
    is_confirmed: bool = False
    confirmation_method: Optional[str] = None  # phone, email, online
    confirmation_timestamp: Optional[datetime] = None
    
    # Follow-up information
    requires_followup: bool = False
    followup_date: Optional[datetime] = None