import json
import os
import uuid
from typing import List, Optional, Dict, Tuple
from datetime import datetime, timedelta

from schedulur.models.appointment import Appointment, AppointmentStatus
from schedulur.models.doctor import Doctor
from schedulur.models.user import User
from schedulur.services.doctor_service import DoctorService
from schedulur.integrations.calendar import CalendarService
from schedulur.integrations.communication import CommunicationService

class AppointmentService:
    """Service for managing appointments"""
    
    def __init__(self, data_file: str = None, user_id: str = None):
        self.data_file = data_file or os.path.join(os.path.dirname(__file__), "../data/appointments.json")
        self.appointments = {}
        self.doctor_service = DoctorService()
        self.calendar_service = CalendarService()
        self.communication_service = CommunicationService()
        self.user_id = user_id
        self.load_appointments()
    
    def load_appointments(self) -> None:
        """Load appointments from data file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    appointment_data = json.load(f)
                    
                for appt_id, appt_dict in appointment_data.items():
                    # Convert datetime strings to datetime objects
                    if 'start_time' in appt_dict and isinstance(appt_dict['start_time'], str):
                        appt_dict['start_time'] = datetime.fromisoformat(appt_dict['start_time'])
                    
                    if 'end_time' in appt_dict and isinstance(appt_dict['end_time'], str):
                        appt_dict['end_time'] = datetime.fromisoformat(appt_dict['end_time'])
                    
                    if 'call_timestamp' in appt_dict and isinstance(appt_dict['call_timestamp'], str):
                        appt_dict['call_timestamp'] = datetime.fromisoformat(appt_dict['call_timestamp'])
                    
                    self.appointments[appt_id] = Appointment(**appt_dict)
        except Exception as e:
            print(f"Error loading appointments: {e}")
            self.appointments = {}
    
    def save_appointments(self) -> None:
        """Save appointments to data file"""
        try:
            # Ensure data directory exists
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            
            appointment_data = {}
            for appt_id, appointment in self.appointments.items():
                # Convert model to dict for serialization
                appt_dict = appointment.to_dict()
                appointment_data[appt_id] = appt_dict
            
            with open(self.data_file, 'w') as f:
                json.dump(appointment_data, f, indent=2)
        except Exception as e:
            print(f"Error saving appointments: {e}")
    
    def create_appointment(self, appointment: Appointment) -> Optional[Appointment]:
        """Create a new appointment"""
        # Check if doctor exists
        doctor = self.doctor_service.get_doctor(appointment.doctor_id)
        if not doctor:
            print(f"Doctor not found: {appointment.doctor_id}")
            return None
        
        # Check if the slot is available in user's calendar
        if not self.calendar_service.check_availability(appointment.start_time, 
                                                     (appointment.end_time - appointment.start_time).seconds // 60):
            print(f"Calendar slot not available: {appointment.start_time} - {appointment.end_time}")
            return None
        
        # Create the appointment
        if not appointment.id:
            appointment.id = str(uuid.uuid4())
        
        # Add user ID if not provided
        if not appointment.user_id and self.user_id:
            appointment.user_id = self.user_id
        
        # Save the appointment
        self.appointments[appointment.id] = appointment
        self.save_appointments()
        
        return appointment
    
    def add_to_calendar(self, appointment_id: str) -> bool:
        """Add an appointment to the user's calendar"""
        appointment = self.get_appointment(appointment_id)
        if not appointment:
            return False
        
        doctor = self.doctor_service.get_doctor(appointment.doctor_id)
        if not doctor:
            return False
        
        # Create calendar event
        event = self.calendar_service.schedule_appointment(
            f"Appointment with {doctor.name}",
            appointment.start_time,
            appointment.end_time,
            f"Appointment with {doctor.name} ({doctor.specialization}). Phone: {doctor.phone}",
            doctor.address
        )
        
        if event and 'id' in event:
            # Update appointment with calendar event ID
            appointment.calendar_event_id = event['id']
            self.update_appointment(appointment_id, appointment)
            return True
        
        return False
    
    def get_appointment(self, appointment_id: str) -> Optional[Appointment]:
        """Get an appointment by ID"""
        return self.appointments.get(appointment_id)
    
    def update_appointment(self, appointment_id: str, appointment: Appointment) -> Optional[Appointment]:
        """Update an appointment"""
        if appointment_id in self.appointments:
            appointment.id = appointment_id
            self.appointments[appointment_id] = appointment
            self.save_appointments()
            return appointment
        return None
    
    def cancel_appointment(self, appointment_id: str) -> bool:
        """Cancel an appointment"""
        appointment = self.get_appointment(appointment_id)
        if appointment:
            appointment.status = AppointmentStatus.CANCELLED
            
            # Remove from calendar if added
            if appointment.calendar_event_id:
                self.calendar_service.cancel_appointment(appointment.calendar_event_id)
            
            self.update_appointment(appointment_id, appointment)
            return True
        return False
    
    def delete_appointment(self, appointment_id: str) -> bool:
        """Delete an appointment"""
        appointment = self.get_appointment(appointment_id)
        if appointment:
            # Remove from calendar if added
            if appointment.calendar_event_id:
                self.calendar_service.cancel_appointment(appointment.calendar_event_id)
                
            del self.appointments[appointment_id]
            self.save_appointments()
            return True
        return False
    
    def list_appointments(self) -> List[Appointment]:
        """List all appointments"""
        return list(self.appointments.values())
    
    def get_upcoming_appointments(self) -> List[Appointment]:
        """Get upcoming appointments"""
        now = datetime.now()
        return [a for a in self.appointments.values() 
                if a.start_time > now and a.status != AppointmentStatus.CANCELLED]
    
    def get_user_appointments(self, user_id: str) -> List[Appointment]:
        """Get appointments for a specific user"""
        return [a for a in self.appointments.values() if a.user_id == user_id]
    
    def schedule_with_doctor(self, 
                           doctor: Doctor, 
                           user: User,
                           reason: str,
                           preferred_date: Optional[datetime] = None) -> Tuple[Optional[Appointment], Dict]:
        """
        Schedule an appointment with a doctor by calling their office
        
        Args:
            doctor: Doctor to schedule with
            user: User to schedule for
            reason: Reason for the appointment
            preferred_date: Preferred appointment date/time
            
        Returns:
            Tuple of (appointment, call_details)
        """
        if not doctor.phone:
            print(f"Cannot schedule appointment - doctor has no phone number")
            return None, {"error": "Doctor has no phone number"}
        
        # Get user's available dates
        if preferred_date:
            # Use the preferred date and 2 more days after that
            preferred_dates = [
                preferred_date.strftime("%Y-%m-%d"),
                (preferred_date + timedelta(days=1)).strftime("%Y-%m-%d"),
                (preferred_date + timedelta(days=2)).strftime("%Y-%m-%d")
            ]
        else:
            # Get next 5 available dates from user's calendar
            available_slots = self.calendar_service.find_available_slots(
                datetime.now(),
                days=14,
                duration_minutes=doctor.appointment_duration
            )
            
            # Group by date and get first 5 unique dates
            dates = []
            for slot in available_slots:
                date_str = slot['start'].strftime("%Y-%m-%d")
                if date_str not in dates:
                    dates.append(date_str)
                if len(dates) >= 5:
                    break
            
            preferred_dates = dates if dates else [
                datetime.now().strftime("%Y-%m-%d"),
                (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
                (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
            ]
        
        # Call the doctor's office
        insurance = user.insurance_provider or "private insurance"
        call_result = self.communication_service.call_doctor_for_appointment(
            doctor_name=doctor.name,
            doctor_phone=doctor.phone,
            patient_name=user.name,
            insurance=insurance,
            reason=reason,
            preferred_dates=preferred_dates
        )
        
        # In a real implementation, we would parse the call transcript
        # For this mock, we'll just create an appointment for a fixed time
        # based on the mock transcript
        
        # Extract appointment details from transcript
        # For the mock, we know the appointment is always on "next Tuesday at 10:30 AM"
        today = datetime.now()
        days_until_tuesday = (1 - today.weekday()) % 7  # 1 = Tuesday
        if days_until_tuesday == 0:
            days_until_tuesday = 7  # Next Tuesday, not today
        
        appointment_date = today + timedelta(days=days_until_tuesday)
        appointment_time = appointment_date.replace(hour=10, minute=30, second=0, microsecond=0)
        
        # Create the appointment
        new_appointment = Appointment(
            doctor_id=doctor.id,
            user_id=user.id if user.id else self.user_id,
            start_time=appointment_time,
            end_time=appointment_time + timedelta(minutes=doctor.appointment_duration),
            status=AppointmentStatus.SCHEDULED,
            reason=reason,
            call_transcript=call_result.get('transcript'),
            call_timestamp=datetime.now(),
            call_duration_seconds=call_result.get('duration')
        )
        
        # Save the appointment
        created_appointment = self.create_appointment(new_appointment)
        
        # Add to calendar
        if created_appointment:
            self.add_to_calendar(created_appointment.id)
        
        return created_appointment, call_result
    
    def approve_doctor_for_scheduling(self, doctor_id: str, approved: bool = True) -> bool:
        """Approve or reject a doctor for scheduling"""
        doctor = self.doctor_service.get_doctor(doctor_id)
        if doctor:
            doctor.user_approval = approved
            self.doctor_service.update_doctor(doctor_id, doctor)
            return True
        return False