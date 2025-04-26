import os
import json
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from abc import ABC, abstractmethod

class CalendarProvider(ABC):
    """Abstract base class for calendar providers"""
    
    @abstractmethod
    def get_events(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get events within a date range"""
        pass
    
    @abstractmethod
    def add_event(self, title: str, start_time: datetime, end_time: datetime, description: str = None) -> Dict:
        """Add a new event to the calendar"""
        pass
    
    @abstractmethod
    def get_free_busy(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get free/busy information within a date range"""
        pass

class GoogleCalendarProvider(CalendarProvider):
    """Google Calendar integration"""
    
    def __init__(self, credentials_path: str = None, token_path: str = None):
        self.credentials_path = credentials_path or os.environ.get('GOOGLE_CREDENTIALS_PATH')
        self.token_path = token_path or os.environ.get('GOOGLE_TOKEN_PATH')
        # TODO: Initialize Google Calendar API client
    
    def get_events(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        # TODO: Implement Google Calendar API integration
        print(f"Getting events from {start_date} to {end_date}")
        return []
    
    def add_event(self, title: str, start_time: datetime, end_time: datetime, description: str = None) -> Dict:
        # TODO: Implement Google Calendar API integration
        print(f"Adding event: {title} from {start_time} to {end_time}")
        return {"id": "sample-event-id", "title": title, "start": start_time, "end": end_time}
    
    def get_free_busy(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        # TODO: Implement Google Calendar API integration
        print(f"Getting free/busy from {start_date} to {end_date}")
        return []

class OutlookCalendarProvider(CalendarProvider):
    """Microsoft Outlook integration"""
    
    def __init__(self, credentials_path: str = None):
        self.credentials_path = credentials_path or os.environ.get('OUTLOOK_CREDENTIALS_PATH')
        # TODO: Initialize Outlook API client
    
    def get_events(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        # TODO: Implement Outlook API integration
        print(f"Getting events from {start_date} to {end_date}")
        return []
    
    def add_event(self, title: str, start_time: datetime, end_time: datetime, description: str = None) -> Dict:
        # TODO: Implement Outlook API integration
        print(f"Adding event: {title} from {start_time} to {end_time}")
        return {"id": "sample-event-id", "title": title, "start": start_time, "end": end_time}
    
    def get_free_busy(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        # TODO: Implement Outlook API integration
        print(f"Getting free/busy from {start_date} to {end_date}")
        return []

class CalendarService:
    """Calendar service facade that works with different calendar providers"""
    
    def __init__(self, provider: str = "google"):
        if provider.lower() == "google":
            self.provider = GoogleCalendarProvider()
        elif provider.lower() == "outlook":
            self.provider = OutlookCalendarProvider()
        else:
            raise ValueError(f"Unsupported calendar provider: {provider}")
    
    def check_availability(self, date: datetime, duration_minutes: int = 30) -> bool:
        """Check if a specific time slot is available"""
        start_time = date
        end_time = date + timedelta(minutes=duration_minutes)
        
        # Get events for the day
        day_start = datetime(date.year, date.month, date.day, 0, 0, 0)
        day_end = datetime(date.year, date.month, date.day, 23, 59, 59)
        events = self.provider.get_events(day_start, day_end)
        
        # Check for overlapping events
        for event in events:
            event_start = event.get("start")
            event_end = event.get("end")
            
            if event_start and event_end:
                # Check for overlap
                if (start_time < event_end and end_time > event_start):
                    return False
        
        return True
    
    def find_available_slots(self, start_date: datetime, days: int = 7, 
                           start_hour: int = 9, end_hour: int = 17, 
                           duration_minutes: int = 30) -> List[Dict]:
        """Find available time slots within a date range"""
        available_slots = []
        current_date = start_date
        end_date = start_date + timedelta(days=days)
        
        while current_date < end_date:
            # Skip weekends (customize as needed)
            if current_date.weekday() < 5:  # Monday to Friday
                day_start = datetime(current_date.year, current_date.month, current_date.day, start_hour, 0, 0)
                day_end = datetime(current_date.year, current_date.month, current_date.day, end_hour, 0, 0)
                
                # Get events for the day
                events = self.provider.get_events(day_start, day_end)
                
                # Create time slots
                current_slot = day_start
                while current_slot + timedelta(minutes=duration_minutes) <= day_end:
                    slot_end = current_slot + timedelta(minutes=duration_minutes)
                    
                    # Check if slot overlaps with any events
                    is_available = True
                    for event in events:
                        event_start = event.get("start")
                        event_end = event.get("end")
                        
                        if event_start and event_end:
                            if (current_slot < event_end and slot_end > event_start):
                                is_available = False
                                break
                    
                    if is_available:
                        available_slots.append({
                            "start": current_slot,
                            "end": slot_end
                        })
                    
                    # Move to next slot (15-minute increments)
                    current_slot += timedelta(minutes=15)
            
            # Move to next day
            current_date += timedelta(days=1)
        
        return available_slots
    
    def schedule_appointment(self, doctor_name: str, start_time: datetime, end_time: datetime, 
                          details: str = None) -> Dict:
        """Schedule an appointment in the calendar"""
        title = f"Appointment with {doctor_name}"
        description = details or f"Medical appointment with {doctor_name}"
        
        return self.provider.add_event(title, start_time, end_time, description)