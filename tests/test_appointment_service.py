import unittest
import tempfile
import os
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from schedulur.models.doctor import Doctor
from schedulur.models.appointment import Appointment
from schedulur.services.doctor_service import DoctorService
from schedulur.services.appointment_service import AppointmentService

class TestAppointmentService(unittest.TestCase):
    
    def setUp(self):
        # Create temporary data files for testing
        self.doctor_temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.appt_temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.doctor_temp_file.close()
        self.appt_temp_file.close()
        
        # Create a test doctor
        self.doctor_service = DoctorService(self.doctor_temp_file.name)
        self.test_doctor = Doctor(
            name="Dr. Test",
            specialization="Testing",
            location="Test Hospital",
            email="test@example.com",
            phone="123-456-7890"
        )
        self.created_doctor = self.doctor_service.create_doctor(self.test_doctor)
        
        # Mock the calendar and communication services
        self.mock_calendar = MagicMock()
        self.mock_calendar.check_availability.return_value = True
        self.mock_calendar.schedule_appointment.return_value = {"id": "test-event"}
        
        self.mock_communication = MagicMock()
        self.mock_communication.notify_appointment.return_value = True
        
        # Initialize appointment service with mocked dependencies
        with patch('schedulur.services.appointment_service.CalendarService', return_value=self.mock_calendar), \
             patch('schedulur.services.appointment_service.CommunicationService', return_value=self.mock_communication):
            self.appointment_service = AppointmentService(self.appt_temp_file.name)
            # Replace doctor service with our test instance
            self.appointment_service.doctor_service = self.doctor_service
    
    def tearDown(self):
        # Clean up the temp files
        os.unlink(self.doctor_temp_file.name)
        os.unlink(self.appt_temp_file.name)
    
    def test_create_appointment(self):
        # Create a test appointment
        now = datetime.now()
        appointment = Appointment(
            doctor_id=self.created_doctor.id,
            start_time=now,
            end_time=now + timedelta(minutes=30),
            notes="Test appointment"
        )
        
        created_appt = self.appointment_service.create_appointment(appointment)
        
        self.assertIsNotNone(created_appt)
        self.assertIsNotNone(created_appt.id)
        self.assertEqual(created_appt.doctor_id, self.created_doctor.id)
        self.assertEqual(created_appt.notes, "Test appointment")
        
        # Verify calendar service was called
        self.mock_calendar.check_availability.assert_called_once()
        self.mock_calendar.schedule_appointment.assert_called_once()
    
    def test_create_appointment_nonexistent_doctor(self):
        # Try to create an appointment with a non-existent doctor
        now = datetime.now()
        appointment = Appointment(
            doctor_id="nonexistent-id",
            start_time=now,
            end_time=now + timedelta(minutes=30)
        )
        
        created_appt = self.appointment_service.create_appointment(appointment)
        
        self.assertIsNone(created_appt)
        # Calendar should not be checked
        self.mock_calendar.check_availability.assert_not_called()
    
    def test_send_appointment_request(self):
        # First create an appointment
        now = datetime.now()
        appointment = Appointment(
            doctor_id=self.created_doctor.id,
            start_time=now,
            end_time=now + timedelta(minutes=30)
        )
        
        created_appt = self.appointment_service.create_appointment(appointment)
        
        # Now send a request
        result = self.appointment_service.send_appointment_request(created_appt.id, "email")
        
        self.assertTrue(result)
        self.mock_communication.notify_appointment.assert_called_once()
        
        # Check that the appointment was updated
        updated_appt = self.appointment_service.get_appointment(created_appt.id)
        self.assertFalse(updated_appt.is_confirmed)

if __name__ == "__main__":
    unittest.main()