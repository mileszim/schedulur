import json
import os
import uuid
from typing import List, Optional, Dict
from datetime import datetime, time

from schedulur.models.doctor import Doctor

class DoctorService:
    """Service for managing doctor information"""
    
    def __init__(self, data_file: str = None):
        self.data_file = data_file or os.path.join(os.path.dirname(__file__), "../data/doctors.json")
        self.doctors = {}
        self.load_doctors()
    
    def load_doctors(self) -> None:
        """Load doctors from data file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    doctor_data = json.load(f)
                    
                for doctor_id, doctor_dict in doctor_data.items():
                    # Convert time strings to time objects
                    if 'available_times' in doctor_dict:
                        for time_slot in doctor_dict['available_times']:
                            if 'start_time' in time_slot and isinstance(time_slot['start_time'], str):
                                time_parts = time_slot['start_time'].split(':')
                                time_slot['start_time'] = time(int(time_parts[0]), int(time_parts[1]))
                            
                            if 'end_time' in time_slot and isinstance(time_slot['end_time'], str):
                                time_parts = time_slot['end_time'].split(':')
                                time_slot['end_time'] = time(int(time_parts[0]), int(time_parts[1]))
                    
                    self.doctors[doctor_id] = Doctor(**doctor_dict)
        except Exception as e:
            print(f"Error loading doctors: {e}")
            self.doctors = {}
    
    def save_doctors(self) -> None:
        """Save doctors to data file"""
        try:
            # Ensure data directory exists
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            
            doctor_data = {}
            for doctor_id, doctor in self.doctors.items():
                doctor_dict = doctor.dict()
                
                # Convert time objects to strings for JSON serialization
                if 'available_times' in doctor_dict:
                    for time_slot in doctor_dict['available_times']:
                        if 'start_time' in time_slot and hasattr(time_slot['start_time'], 'strftime'):
                            time_slot['start_time'] = time_slot['start_time'].strftime('%H:%M')
                        
                        if 'end_time' in time_slot and hasattr(time_slot['end_time'], 'strftime'):
                            time_slot['end_time'] = time_slot['end_time'].strftime('%H:%M')
                
                doctor_data[doctor_id] = doctor_dict
            
            with open(self.data_file, 'w') as f:
                json.dump(doctor_data, f, indent=2)
        except Exception as e:
            print(f"Error saving doctors: {e}")
    
    def create_doctor(self, doctor: Doctor) -> Doctor:
        """Create a new doctor"""
        if not doctor.id:
            doctor.id = str(uuid.uuid4())
        
        self.doctors[doctor.id] = doctor
        self.save_doctors()
        return doctor
    
    def get_doctor(self, doctor_id: str) -> Optional[Doctor]:
        """Get a doctor by ID"""
        return self.doctors.get(doctor_id)
    
    def update_doctor(self, doctor_id: str, doctor: Doctor) -> Optional[Doctor]:
        """Update a doctor"""
        if doctor_id in self.doctors:
            doctor.id = doctor_id
            self.doctors[doctor_id] = doctor
            self.save_doctors()
            return doctor
        return None
    
    def delete_doctor(self, doctor_id: str) -> bool:
        """Delete a doctor"""
        if doctor_id in self.doctors:
            del self.doctors[doctor_id]
            self.save_doctors()
            return True
        return False
    
    def list_doctors(self) -> List[Doctor]:
        """List all doctors"""
        return list(self.doctors.values())
    
    def filter_doctors_by_insurance(self, insurance_provider: str) -> List[Doctor]:
        """Filter doctors by accepted insurance"""
        return [d for d in self.doctors.values() if insurance_provider in d.accepted_insurance]
    
    def filter_doctors_by_specialization(self, specialization: str) -> List[Doctor]:
        """Filter doctors by specialization"""
        return [d for d in self.doctors.values() if specialization.lower() in d.specialization.lower()]
    
    def get_approved_doctors(self) -> List[Doctor]:
        """Get doctors that have been approved by the user"""
        return [d for d in self.doctors.values() if d.user_approval is True]
    
    def get_rejected_doctors(self) -> List[Doctor]:
        """Get doctors that have been rejected by the user"""
        return [d for d in self.doctors.values() if d.user_approval is False]
    
    def get_pending_doctors(self) -> List[Doctor]:
        """Get doctors that haven't been approved or rejected yet"""
        return [d for d in self.doctors.values() if d.user_approval is None]