import os
import json
from typing import List, Dict, Optional
from datetime import datetime, timedelta, time
from abc import ABC, abstractmethod

class CalendarProvider(ABC):
    """Abstract base class for calendar providers"""
    
    @abstractmethod
    def get_events(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get events within a date range"""
        pass
    
    @abstractmethod
    def add_event(self, title: str, start_time: datetime, end_time: datetime, description: str = None, location: str = None) -> Dict:
        """Add a new event to the calendar"""
        pass
    
    @abstractmethod
    def get_free_busy(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get free/busy information within a date range"""
        pass
    
    @abstractmethod
    def delete_event(self, event_id: str) -> bool:
        """Delete an event from the calendar"""
        pass

class MockCalendarProvider(CalendarProvider):
    """Mock calendar provider for testing"""
    
    def __init__(self):
        self.events = []
        self.data_file = os.path.join(os.path.dirname(__file__), "../data/mock_calendar.json")
        self.load_events()
    
    def load_events(self):
        """Load events from data file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    events_data = json.load(f)
                
                for event in events_data:
                    if isinstance(event['start'], str):
                        event['start'] = datetime.fromisoformat(event['start'])
                    if isinstance(event['end'], str):
                        event['end'] = datetime.fromisoformat(event['end'])
                
                self.events = events_data
        except Exception as e:
            print(f"Error loading calendar events: {e}")
            self.events = []
    
    def save_events(self):
        """Save events to data file"""
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            
            events_data = []
            for event in self.events:
                event_copy = event.copy()
                if hasattr(event_copy['start'], 'isoformat'):
                    event_copy['start'] = event_copy['start'].isoformat()
                if hasattr(event_copy['end'], 'isoformat'):
                    event_copy['end'] = event_copy['end'].isoformat()
                events_data.append(event_copy)
            
            with open(self.data_file, 'w') as f:
                json.dump(events_data, f, indent=2)
        except Exception as e:
            print(f"Error saving calendar events: {e}")
    
    def get_events(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get events within a date range"""
        return [event for event in self.events 
                if event['start'] >= start_date and event['end'] <= end_date]
    
    def add_event(self, title: str, start_time: datetime, end_time: datetime, description: str = None, location: str = None) -> Dict:
        """Add a new event to the calendar"""
        event = {
            'id': f"event-{len(self.events) + 1}",
            'title': title,
            'start': start_time,
            'end': end_time,
            'description': description,
            'location': location
        }
        self.events.append(event)
        self.save_events()
        return event
    
    def get_free_busy(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get free/busy information within a date range"""
        busy_periods = []
        for event in self.get_events(start_date, end_date):
            busy_periods.append({
                'start': event['start'],
                'end': event['end']
            })
        return busy_periods
    
    def delete_event(self, event_id: str) -> bool:
        """Delete an event from the calendar"""
        for i, event in enumerate(self.events):
            if event['id'] == event_id:
                del self.events[i]
                self.save_events()
                return True
        return False

class GoogleCalendarProvider(CalendarProvider):
    """Google Calendar integration"""
    
    def __init__(self, credentials_path: str = None, token_path: str = None):
        self.credentials_path = credentials_path or os.environ.get('GOOGLE_CREDENTIALS_PATH')
        self.token_path = token_path or os.environ.get('GOOGLE_TOKEN_PATH')
        
        # TODO: Implement proper Google Calendar API client initialization
        # For now, just show that we'd need to set up the API client here
        self.mock_provider = MockCalendarProvider()
    
    def get_events(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get events within a date range"""
        # TODO: Replace with real Google Calendar API call
        return self.mock_provider.get_events(start_date, end_date)
    
    def add_event(self, title: str, start_time: datetime, end_time: datetime, description: str = None, location: str = None) -> Dict:
        """Add a new event to the calendar"""
        # TODO: Replace with real Google Calendar API call
        return self.mock_provider.add_event(title, start_time, end_time, description, location)
    
    def get_free_busy(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get free/busy information within a date range"""
        # TODO: Replace with real Google Calendar API call
        return self.mock_provider.get_free_busy(start_date, end_date)
    
    def delete_event(self, event_id: str) -> bool:
        """Delete an event from the calendar"""
        # TODO: Replace with real Google Calendar API call
        return self.mock_provider.delete_event(event_id)

class OutlookCalendarProvider(CalendarProvider):
    """Microsoft Outlook integration"""
    
    def __init__(self, credentials_path: str = None):
        self.credentials_path = credentials_path or os.environ.get('OUTLOOK_CREDENTIALS_PATH')
        # TODO: Initialize Outlook API client
        self.mock_provider = MockCalendarProvider()
    
    def get_events(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get events within a date range"""
        # TODO: Replace with real Outlook API call
        return self.mock_provider.get_events(start_date, end_date)
    
    def add_event(self, title: str, start_time: datetime, end_time: datetime, description: str = None, location: str = None) -> Dict:
        """Add a new event to the calendar"""
        # TODO: Replace with real Outlook API call
        return self.mock_provider.add_event(title, start_time, end_time, description, location)
    
    def get_free_busy(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get free/busy information within a date range"""
        # TODO: Replace with real Outlook API call
        return self.mock_provider.get_free_busy(start_date, end_date)
    
    def delete_event(self, event_id: str) -> bool:
        """Delete an event from the calendar"""
        # TODO: Replace with real Outlook API call
        return self.mock_provider.delete_event(event_id)

class CalendarService:
    """Calendar service facade that works with different calendar providers"""
    
    def __init__(self, provider_type: str = "google", user_id: str = None):
        self.user_id = user_id
        
        if provider_type.lower() == "google":
            self.provider = GoogleCalendarProvider()
        elif provider_type.lower() == "outlook":
            self.provider = OutlookCalendarProvider()
        elif provider_type.lower() == "mock":
            self.provider = MockCalendarProvider()
        else:
            # Default to mock provider for testing
            self.provider = MockCalendarProvider()
    
    def check_availability(self, start_time: datetime, duration_minutes: int = 30) -> bool:
        """Check if a specific time slot is available"""
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        # Get busy periods for the day
        day_start = datetime(start_time.year, start_time.month, start_time.day, 0, 0, 0)
        day_end = datetime(start_time.year, start_time.month, start_time.day, 23, 59, 59)
        busy_periods = self.provider.get_free_busy(day_start, day_end)
        
        # Check for overlapping busy periods
        for period in busy_periods:
            period_start = period.get("start")
            period_end = period.get("end")
            
            if period_start and period_end:
                # Check for overlap
                if (start_time < period_end and end_time > period_start):
                    return False
        
        return True
    
    def find_available_slots(self, 
                           start_date: datetime, 
                           days: int = 7, 
                           time_preferences: Optional[List[Dict]] = None,
                           duration_minutes: int = 30) -> List[Dict]:
        """
        Find available time slots within a date range based on user preferences
        
        Args:
            start_date: Beginning date to check
            days: Number of days to check
            time_preferences: List of preferred time slots, e.g. [
                {"day": 0, "start": "09:00", "end": "12:00"},
                {"day": 2, "start": "13:00", "end": "17:00"}
            ]
            duration_minutes: Appointment duration in minutes
            
        Returns:
            List of available time slots
        """
        available_slots = []
        current_date = start_date
        end_date = start_date + timedelta(days=days)
        
        # If no preferences are set, use business hours (9-5) on weekdays
        if not time_preferences:
            time_preferences = [
                {"day": 0, "start": "09:00", "end": "17:00"},  # Monday
                {"day": 1, "start": "09:00", "end": "17:00"},  # Tuesday
                {"day": 2, "start": "09:00", "end": "17:00"},  # Wednesday
                {"day": 3, "start": "09:00", "end": "17:00"},  # Thursday
                {"day": 4, "start": "09:00", "end": "17:00"},  # Friday
            ]
        
        while current_date < end_date:
            # Get the weekday (0 = Monday, 6 = Sunday)
            weekday = current_date.weekday()
            
            # Check if this day is in the user's preferences
            day_prefs = [p for p in time_preferences if p.get("day") == weekday]
            
            for pref in day_prefs:
                # Parse the time range for this day
                start_hour, start_minute = map(int, pref.get("start", "09:00").split(":"))
                end_hour, end_minute = map(int, pref.get("end", "17:00").split(":"))
                
                day_start = datetime(
                    current_date.year, current_date.month, current_date.day, 
                    start_hour, start_minute, 0
                )
                day_end = datetime(
                    current_date.year, current_date.month, current_date.day, 
                    end_hour, end_minute, 0
                )
                
                # Get busy periods for this day
                busy_periods = self.provider.get_free_busy(day_start, day_end)
                
                # Create time slots with 15-minute increments
                current_slot = day_start
                while current_slot + timedelta(minutes=duration_minutes) <= day_end:
                    slot_end = current_slot + timedelta(minutes=duration_minutes)
                    
                    # Check if slot overlaps with any busy periods
                    is_available = True
                    for period in busy_periods:
                        period_start = period.get("start")
                        period_end = period.get("end")
                        
                        if period_start and period_end:
                            if (current_slot < period_end and slot_end > period_start):
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
    
    def schedule_appointment(self, 
                            title: str, 
                            start_time: datetime, 
                            end_time: datetime, 
                            description: str = None,
                            location: str = None) -> Dict:
        """
        Schedule an appointment in the calendar
        
        Args:
            title: Event title
            start_time: Appointment start time
            end_time: Appointment end time
            description: Event description
            location: Event location
            
        Returns:
            Created calendar event
        """
        return self.provider.add_event(title, start_time, end_time, description, location)
    
    def cancel_appointment(self, event_id: str) -> bool:
        """Cancel an appointment in the calendar"""
        return self.provider.delete_event(event_id)