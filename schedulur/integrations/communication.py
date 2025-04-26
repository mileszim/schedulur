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

class EmailProvider(CommunicationProvider):
    """Email communication provider"""
    
    def __init__(self, smtp_server: str = None, smtp_port: int = None, 
                 username: str = None, password: str = None):
        self.smtp_server = smtp_server or os.environ.get('SMTP_SERVER')
        self.smtp_port = smtp_port or int(os.environ.get('SMTP_PORT', 587))
        self.username = username or os.environ.get('SMTP_USERNAME')
        self.password = password or os.environ.get('SMTP_PASSWORD')
        # TODO: Initialize email client
    
    def send_message(self, to: str, subject: str, body: str) -> bool:
        # TODO: Implement email sending logic
        print(f"Sending email to {to} with subject '{subject}'")
        return True
    
    def make_call(self, to: str, message: str) -> Dict:
        # Email provider cannot make calls
        raise NotImplementedError("Email provider cannot make voice calls")

class TwilioProvider(CommunicationProvider):
    """Twilio communication provider for voice and SMS"""
    
    def __init__(self, account_sid: str = None, auth_token: str = None, phone_number: str = None):
        self.account_sid = account_sid or os.environ.get('TWILIO_ACCOUNT_SID')
        self.auth_token = auth_token or os.environ.get('TWILIO_AUTH_TOKEN')
        self.phone_number = phone_number or os.environ.get('TWILIO_PHONE_NUMBER')
        # TODO: Initialize Twilio client
    
    def send_message(self, to: str, subject: str, body: str) -> bool:
        # Send SMS via Twilio
        message_body = f"{subject}\n\n{body}"
        print(f"Sending SMS to {to}: {message_body[:50]}...")
        # TODO: Implement Twilio SMS sending
        return True
    
    def make_call(self, to: str, message: str) -> Dict:
        # Make voice call via Twilio
        print(f"Making call to {to} with message: {message[:50]}...")
        # TODO: Implement Twilio call
        return {"status": "initiated", "call_id": f"sample-call-{int(time.time())}"}

class CommunicationService:
    """Communication service facade that works with different providers"""
    
    def __init__(self):
        self.email_provider = EmailProvider()
        self.voice_provider = None
        try:
            self.voice_provider = TwilioProvider()
        except Exception as e:
            print(f"Voice provider initialization failed: {e}")
    
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
    
    def notify_appointment(self, appointment: Dict, doctor: Dict, method: str = "email") -> bool:
        """Send an appointment notification or request"""
        doctor_name = doctor.get("name")
        doctor_email = doctor.get("email")
        doctor_phone = doctor.get("phone")
        
        start_time = appointment.get("start_time")
        formatted_date = start_time.strftime("%A, %B %d, %Y at %I:%M %p")
        
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
