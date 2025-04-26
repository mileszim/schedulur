from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime

class AppointmentStatus:
    REQUESTED = "requested"
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class Appointment(BaseModel):
    id: Optional[str] = None
    user_id: Optional[str] = None
    doctor_id: str
    
    # Scheduling details
    start_time: datetime
    end_time: datetime
    
    # Status tracking
    status: str = AppointmentStatus.REQUESTED
    
    # Appointment details
    reason: Optional[str] = None
    notes: Optional[str] = None
    location: Optional[str] = None
    virtual: bool = False
    
    # Call details
    call_transcript: Optional[str] = None
    call_timestamp: Optional[datetime] = None
    call_duration_seconds: Optional[int] = None
    
    # Calendar event ID (once added to calendar)
    calendar_event_id: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert model to dictionary for easier JSON serialization."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "doctor_id": self.doctor_id,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "status": self.status,
            "reason": self.reason,
            "notes": self.notes,
            "location": self.location,
            "virtual": self.virtual,
            "call_transcript": self.call_transcript,
            "call_timestamp": self.call_timestamp.isoformat() if self.call_timestamp else None,
            "call_duration_seconds": self.call_duration_seconds,
            "calendar_event_id": self.calendar_event_id
        }