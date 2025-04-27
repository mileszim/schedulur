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
        self.data_file = data_file or os.path.join(
            os.path.dirname(__file__), "../data/appointments.json")
        self.appointments = {}
        self.doctor_service = DoctorService()
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
                        appt_dict['start_time'] = datetime.fromisoformat(
                            appt_dict['start_time'])

                    if 'end_time' in appt_dict and isinstance(appt_dict['end_time'], str):
                        appt_dict['end_time'] = datetime.fromisoformat(
                            appt_dict['end_time'])

                    if 'call_timestamp' in appt_dict and isinstance(appt_dict['call_timestamp'], str):
                        appt_dict['call_timestamp'] = datetime.fromisoformat(
                            appt_dict['call_timestamp'])

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
            self.update_appointment(appointment_id, appointment)
            return True
        return False

    def delete_appointment(self, appointment_id: str) -> bool:
        """Delete an appointment"""
        appointment = self.get_appointment(appointment_id)
        if appointment:
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
                             scheduling_preferences: Optional[Dict] = None) -> Tuple[Optional[Appointment], Dict]:
        """
        Schedule an appointment with a doctor by calling their office

        Args:
            doctor: Doctor to schedule with
            user: User to schedule for
            reason: Reason for the appointment
            scheduling_preferences: User's scheduling preferences

        Returns:
            Tuple of (appointment, call_details)
        """
        # Use Retell to make the phone call
        from schedulur.integrations.retell import call_doctor as retell_call_doctor

        # Hardcode the phone number to 847-814-3999 as requested
        doctor_phone = "+1-925-451-4431"

        # Call the doctor using Retell
        try:
            retell_call_doctor(
                to_number=doctor_phone,
                user_name=user.name,
                doctor_name=doctor.name,
                insurance_type=user.insurance_provider or "private insurance"
            )
            print(f"Initiated Retell call to {doctor_phone} for {doctor.name}")
        except Exception as e:
            print(f"Error using Retell to call doctor: {e}")

        # Get scheduling preferences
        timeframe = scheduling_preferences.get(
            'timeframe', '2weeks') if scheduling_preferences else '2weeks'
        preferred_days = scheduling_preferences.get(
            'preferred_days', []) if scheduling_preferences else []
        preferred_times = scheduling_preferences.get(
            'preferred_times', []) if scheduling_preferences else []

        # Determine the date range based on timeframe
        today = datetime.now()
        if timeframe == 'asap':
            days_range = 7
        elif timeframe == '1week':
            days_range = 7
        elif timeframe == '2weeks':
            days_range = 14
        elif timeframe == '1month':
            days_range = 30
        else:  # flexible
            days_range = 30

        # Find dates that match preferred days
        preferred_dates = []
        current_date = today
        end_date = today + timedelta(days=days_range)

        # If no specific days are provided, use all days
        if not preferred_days:
            preferred_days = list(range(7))  # 0-6 for Monday-Sunday

        # Collect dates that match the preferred days
        while current_date < end_date:
            if current_date.weekday() in preferred_days:
                preferred_dates.append(current_date.strftime("%Y-%m-%d"))
            current_date += timedelta(days=1)

        # Ensure we have at least some dates
        if not preferred_dates:
            preferred_dates = [
                today.strftime("%Y-%m-%d"),
                (today + timedelta(days=1)).strftime("%Y-%m-%d"),
                (today + timedelta(days=2)).strftime("%Y-%m-%d")
            ]

        # For backward compatibility, also use the communication service
        insurance = user.insurance_provider or "private insurance"
        call_result = self.communication_service.call_doctor_for_appointment(
            doctor_name=doctor.name,
            doctor_phone=doctor_phone,  # Use the hardcoded number
            patient_name=user.name,
            insurance=insurance,
            reason=reason,
            preferred_dates=preferred_dates,
            preferred_times=preferred_times
        )

        # Find a date that matches user's preferred day
        today = datetime.now()

        # Default to Tuesday at 10:30 AM if no preferences
        days_until_tuesday = (1 - today.weekday()) % 7  # 1 = Tuesday
        if days_until_tuesday == 0:
            days_until_tuesday = 7  # Next Tuesday, not today

        appointment_date = today + timedelta(days=days_until_tuesday)

        # Check if we should use a different day based on user preferences
        if preferred_days and days_until_tuesday not in preferred_days:
            # Find the next preferred day
            for days_ahead in range(1, days_range):
                day = (today + timedelta(days=days_ahead)).weekday()
                if day in preferred_days:
                    appointment_date = today + timedelta(days=days_ahead)
                    break

        # Set time based on preferred time of day
        if 'morning' in preferred_times:
            hour, minute = 10, 30
        elif 'afternoon' in preferred_times:
            hour, minute = 14, 0  # 2:00 PM
        elif 'evening' in preferred_times:
            hour, minute = 17, 0  # 5:00 PM
        else:
            hour, minute = 10, 30  # Default to 10:30 AM

        appointment_time = appointment_date.replace(
            hour=hour, minute=minute, second=0, microsecond=0)

        # Create the appointment
        new_appointment = Appointment(
            doctor_id=doctor.id,
            user_id=user.id if user.id else self.user_id,
            start_time=appointment_time,
            end_time=appointment_time +
            timedelta(minutes=doctor.appointment_duration),
            status=AppointmentStatus.SCHEDULED,
            reason=reason,
            call_transcript=call_result.get('transcript'),
            call_timestamp=datetime.now(),
            call_duration_seconds=call_result.get('duration')
        )

        # Save the appointment
        created_appointment = self.create_appointment(new_appointment)

        return created_appointment, call_result

    def approve_doctor_for_scheduling(self, doctor_id: str, approved: bool = True) -> bool:
        """Approve or reject a doctor for scheduling"""
        doctor = self.doctor_service.get_doctor(doctor_id)
        if doctor:
            doctor.user_approval = approved
            self.doctor_service.update_doctor(doctor_id, doctor)
            return True
        return False
