from datetime import datetime, time
from typing import Dict, List
import calendar

def parse_time_string(time_str: str) -> time:
    """Parse a time string (HH:MM) into a time object."""
    return datetime.strptime(time_str, "%H:%M").time()

def format_time(t: time) -> str:
    """Format a time object into a string."""
    return t.strftime("%I:%M %p")

def day_name(day_index: int) -> str:
    """Convert day index (0 = Monday) to name."""
    return calendar.day_name[day_index]

def format_availability(days: List[int], times: List[Dict]) -> str:
    """Format availability information in a human-readable way."""
    if not days or not times:
        return "No availability set"
    
    result = []
    for day in days:
        day_str = day_name(day)
        time_strs = []
        
        for time_slot in times:
            if 'day' not in time_slot or time_slot.get('day') == day:
                start = format_time(time_slot['start_time'])
                end = format_time(time_slot['end_time'])
                time_strs.append(f"{start} - {end}")
        
        if time_strs:
            result.append(f"{day_str}: {', '.join(time_strs)}")
    
    return "\n".join(result)