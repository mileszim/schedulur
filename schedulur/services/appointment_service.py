import json
import os
import uuid
from typing import List, Optional, Dict
from datetime import datetime, timedelta

from schedulur.models.appointment import Appointment
from schedulur.services.doctor_service import DoctorService
from schedulur.integrations.calendar import CalendarService
from schedulur.integrations.communication import CommunicationService

class AppointmentService:
    """Service for managing appointments"""
    
    def __init__(self, data_file: str = None):
        self.data_file = data_file or os.path.join(os.path.dirname(__file__), "../data/appointments.json")
        self.appointments = {}
        self.doctor_service = DoctorService()
        self.calendar_service = CalendarService()
        self.communication_service = CommunicationService()
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
                    
                    if 'confirmation_timestamp' in appt_dict and isinstance(appt_dict['confirmation_timestamp'], str):
                        appt_dict['confirmation_timestamp'] = datetime.fromisoformat(appt_dict['confirmation_timestamp'])
                    
                    if 'followup_date' in appt_dict and isinstance(appt_dict['followup_date'], str):
                        appt_dict['followup_date'] = datetime.fromisoformat(appt_dict['followup_date'])
                    
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
                appt_dict = appointment.dict()
                
                # Convert datetime objects to strings for JSON serialization
                if 'start_time' in appt_dict and hasattr(appt_dict['start_time'], 'isoformat'):
                    appt_dict['start_time'] = appt_dict['start_time'].isoformat()
                
                if 'end_time' in appt_dict and hasattr(appt_dict['end_time'], 'isoformat'):
                    appt_dict['end_time'] = appt_dict['end_time'].isoformat()
                
                if 'confirmation_timestamp' in appt_dict and appt_dict['confirmation_timestamp'] and hasattr(appt_dict['confirmation_timestamp'], 'isoformat'):
                    appt_dict['confirmation_timestamp'] = appt_dict['confirmation_timestamp'].isoformat()
                
                if 'followup_date' in appt_dict and appt_dict['followup_date'] and hasattr(appt_dict['followup_date'], 'isoformat'):
                    appt_dict['followup_date'] = appt_dict['followup_date'].isoformat()
                
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
        
        # Check if the slot is available in personal calendar
        if not self.calendar_service.check_availability(appointment.start_time, 
                                                      (appointment.end_time - appointment.start_time).seconds // 60):
            print(f"Calendar slot not available: {appointment.start_time} - {appointment.end_time}")
            return None
        
        # Create the appointment
        if not appointment.id:
            appointment.id = str(uuid.uuid4())
        
        # Add to personal calendar
        self.calendar_service.schedule_appointment(
            doctor.name,
            appointment.start_time,
            appointment.end_time,
            f"Appointment with {doctor.name} ({doctor.specialization}). Phone: {doctor.phone}"
        )
        
        # Save the appointment
        self.appointments[appointment.id] = appointment
        self.save_appointments()
        
        return appointment
    
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
        if appointment_id in self.appointments:
            self.appointments[appointment_id].status = "cancelled"
            self.save_appointments()
            return True
        return False
    
    def delete_appointment(self, appointment_id: str) -> bool:
        """Delete an appointment"""
        if appointment_id in self.appointments:
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
                if a.start_time > now and a.status != "cancelled"]
    
    def send_appointment_request(self, appointment_id: str, method: str = None) -> bool:
        """Send an appointment request to a doctor"""
        appointment = self.get_appointment(appointment_id)
        if not appointment:
            return False
        
        doctor = self.doctor_service.get_doctor(appointment.doctor_id)
        if not doctor:
            return False
        
        # Use doctor's preferred contact method if not specified
        if not method:
            method = doctor.preferred_contact
        
        try:
            # Convert appointment to dict for the notification service
            appointment_dict = appointment.dict()
            doctor_dict = doctor.dict()
            
            success = self.communication_service.notify_appointment(appointment_dict, doctor_dict, method)
            
            if success:
                # Update appointment status
                appointment.is_confirmed = False
                self.update_appointment(appointment.id, appointment)
            
            return success
        except Exception as e:
            print(f"Failed to send appointment request: {e}")
            return False
    
    def confirm_appointment(self, appointment_id: str, method: str) -> bool:
        """Mark an appointment as confirmed"""
        appointment = self.get_appointment(appointment_id)
        if not appointment:
            return False
        
        appointment.is_confirmed = True
        appointment.confirmation_method = method
        appointment.confirmation_timestamp = datetime.now()
        
        self.update_appointment(appointment.id, appointment)
        return True