import os
import json
import time
from typing import Dict, List, Optional
from datetime import datetime
from abc import ABC, abstractmethod

class CommunicationProvider(ABC):
    """Abstract base class for communication providers"""
    
    @abstractmethod
    def send_message(self, to: str, subject: str, body: str) -> bool:
        """Send a message to a recipient"""
        pass
    
    @abstractmethod
    def make_call(self, to: str, message: str) -> Dict:
        """Make a voice call to a recipient"""
        pass

class MockCommunicationProvider(CommunicationProvider):
    """Mock communication provider for testing"""
    
    def __init__(self):
        self.sent_messages = []
        self.calls = []
        self.data_file = os.path.join(os.path.dirname(__file__), "../data/communication.json")
        self.load_data()
    
    def load_data(self):
        """Load communication data from file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.sent_messages = data.get('messages', [])
                    self.calls = data.get('calls', [])
        except Exception as e:
            print(f"Error loading communication data: {e}")
            self.sent_messages = []
            self.calls = []
    
    def save_data(self):
        """Save communication data to file"""
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            
            with open(self.data_file, 'w') as f:
                json.dump({
                    'messages': self.sent_messages,
                    'calls': self.calls
                }, f, indent=2)
        except Exception as e:
            print(f"Error saving communication data: {e}")
    
    def send_message(self, to: str, subject: str, body: str) -> bool:
        """Send a message to a recipient"""
        message = {
            'to': to,
            'subject': subject,
            'body': body,
            'timestamp': datetime.now().isoformat(),
            'status': 'sent'
        }
        self.sent_messages.append(message)
        self.save_data()
        return True
    
    def make_call(self, to: str, message: str) -> Dict:
        """Make a voice call to a recipient"""
        call = {
            'to': to,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'status': 'completed',
            'call_id': f"call-{len(self.calls) + 1}",
            'duration': 120,  # 2 minutes in seconds
            'transcript': self._generate_mock_transcript(message, to)
        }
        self.calls.append(call)
        self.save_data()
        return call
    
    def _generate_mock_transcript(self, message: str, to: str) -> str:
        """Generate a fake call transcript for testing"""
        # Create a somewhat realistic appointment scheduling conversation
        
        receptionist_name = "Sarah"
        doctor_name = "Dr. Smith"
        if "Dr." in message:
            doctor_name = message.split("Dr.")[1].split()[0]
        
        return f"""
SCHEDULUR: Hello, I'm calling to schedule an appointment with {doctor_name}. This is an automated call from Schedulur, a medical appointment scheduling service.

RECEPTIONIST ({receptionist_name}): Hello, {doctor_name}'s office. This is {receptionist_name} speaking. How can I help you?

SCHEDULUR: I'd like to schedule an appointment with {doctor_name}. I'm calling on behalf of a patient.

RECEPTIONIST: Sure, I can help with that. What's the patient's name and date of birth?

SCHEDULUR: The patient's name is John Doe, date of birth January 15, 1980. They're looking for an appointment in the next two weeks.

RECEPTIONIST: Okay, let me check our availability. What's the reason for the visit?

SCHEDULUR: It's for a regular checkup and consultation. The patient has {message.split("appointment with")[1].split(".")[0]} if relevant.

RECEPTIONIST: I see. We have an opening next Tuesday at 10:30 AM or Thursday at 2:15 PM. Which would work better?

SCHEDULUR: The Tuesday 10:30 AM slot would be perfect. Can we book that time?

RECEPTIONIST: Yes, I can schedule that. Does the patient have insurance?

SCHEDULUR: Yes, they have BlueCross BlueShield. Policy number BCX123456789.

RECEPTIONIST: Great, we accept that insurance. I'll schedule John Doe for Tuesday at 10:30 AM with {doctor_name}. The appointment will be approximately 30 minutes. Please arrive 15 minutes early to complete paperwork if this is their first visit. Would you like me to send an email confirmation?

SCHEDULUR: Yes, please send a confirmation to johndoe@example.com.

RECEPTIONIST: Perfect. I've booked the appointment and will send the confirmation. Is there anything else you need help with today?

SCHEDULUR: No, that's all. Thank you for your help.

RECEPTIONIST: You're welcome. Have a great day!

SCHEDULUR: You too. Goodbye.
"""

class EmailProvider(CommunicationProvider):
    """Email communication provider"""
    
    def __init__(self, smtp_server: str = None, smtp_port: int = None, 
                 username: str = None, password: str = None):
        self.smtp_server = smtp_server or os.environ.get('SMTP_SERVER')
        self.smtp_port = smtp_port or int(os.environ.get('SMTP_PORT', 587))
        self.username = username or os.environ.get('SMTP_USERNAME')
        self.password = password or os.environ.get('SMTP_PASSWORD')
        
        # Fallback to mock provider for testing
        self.mock_provider = MockCommunicationProvider()
    
    def send_message(self, to: str, subject: str, body: str) -> bool:
        # TODO: Implement real email sending logic
        return self.mock_provider.send_message(to, subject, body)
    
    def make_call(self, to: str, message: str) -> Dict:
        # Email provider cannot make calls
        raise NotImplementedError("Email provider cannot make voice calls")

class TwilioProvider(CommunicationProvider):
    """Twilio communication provider for voice and SMS"""
    
    def __init__(self, account_sid: str = None, auth_token: str = None, phone_number: str = None):
        self.account_sid = account_sid or os.environ.get('TWILIO_ACCOUNT_SID')
        self.auth_token = auth_token or os.environ.get('TWILIO_AUTH_TOKEN')
        self.phone_number = phone_number or os.environ.get('TWILIO_PHONE_NUMBER')
        
        # Fallback to mock provider for testing
        self.mock_provider = MockCommunicationProvider()
    
    def send_message(self, to: str, subject: str, body: str) -> bool:
        # Send SMS via Twilio
        # TODO: Implement real Twilio SMS sending
        return self.mock_provider.send_message(to, subject, body)
    
    def make_call(self, to: str, message: str) -> Dict:
        # Make voice call via Twilio
        # TODO: Implement real Twilio call
        return self.mock_provider.make_call(to, message)

class CommunicationService:
    """Communication service facade that works with different providers"""
    
    def __init__(self):
        self.email_provider = EmailProvider()
        self.voice_provider = None
        try:
            self.voice_provider = TwilioProvider()
        except Exception as e:
            print(f"Voice provider initialization failed: {e}")
            # Use mock provider as fallback
            self.voice_provider = MockCommunicationProvider()
    
    def send_email(self, to: str, subject: str, body: str) -> bool:
        """Send an email"""
        return self.email_provider.send_message(to, subject, body)
    
    def send_sms(self, to: str, message: str) -> bool:
        """Send an SMS"""
        if not self.voice_provider:
            raise ValueError("Voice/SMS provider not initialized")
        return self.voice_provider.send_message(to, "Schedulur", message)
    
    def make_call(self, to: str, message: str) -> Dict:
        """Make a voice call"""
        if not self.voice_provider:
            raise ValueError("Voice/SMS provider not initialized")
        return self.voice_provider.make_call(to, message)
    
    def call_doctor_for_appointment(self, 
                                  doctor_name: str,
                                  doctor_phone: str,
                                  patient_name: str,
                                  insurance: str,
                                  reason: str,
                                  preferred_dates: List[str]) -> Dict:
        """
        Call a doctor's office to schedule an appointment
        
        Args:
            doctor_name: Name of the doctor
            doctor_phone: Doctor's phone number
            patient_name: Patient's name
            insurance: Patient's insurance
            reason: Reason for the appointment
            preferred_dates: List of preferred dates in order
            
        Returns:
            Call details including transcript
        """
        # Prepare the call script
        message = f"""Hello, I'm calling to schedule an appointment with Dr. {doctor_name} for {patient_name}.
The patient has {insurance} insurance and needs to be seen for {reason}.
They would prefer an appointment on one of these dates: {', '.join(preferred_dates)}.
Please let me know what availability you have."""
        
        # Make the call
        call_result = self.make_call(doctor_phone, message)
        
        # In a real implementation with Twilio, we would set up a call flow that can interact
        # with the receptionist and collect information
        
        return call_result
    
    def notify_appointment(self, appointment: Dict, doctor: Dict, method: str = "email") -> bool:
        """Send an appointment notification or request"""
        doctor_name = doctor.get("name")
        doctor_email = doctor.get("email")
        doctor_phone = doctor.get("phone")
        
        start_time = appointment.get("start_time")
        formatted_date = start_time.strftime("%A, %B %d, %Y at %I:%M %p") if hasattr(start_time, "strftime") else start_time
        
        # Create message content
        subject = f"Appointment Request with Dr. {doctor_name}"
        body = f"I would like to schedule an appointment on {formatted_date}.\n\n"
        body += f"Please let me know if this time works for you, or suggest an alternative.\n\n"
        body += "Thank you."
        
        if method.lower() == "email" and doctor_email:
            return self.send_email(doctor_email, subject, body)
        elif method.lower() == "sms" and doctor_phone:
            return self.send_sms(doctor_phone, f"{subject}\n{body}")
        elif method.lower() == "call" and doctor_phone:
            message = f"Hello, this is an automated message requesting an appointment with Dr. {doctor_name} on {formatted_date}. Please press 1 to confirm, or 2 to suggest an alternative time."
            self.make_call(doctor_phone, message)
            return True
        else:
            raise ValueError(f"Invalid notification method or missing contact information: {method}")