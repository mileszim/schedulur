import requests
import os
import json
from typing import List, Dict, Optional
import uuid
from datetime import datetime

from schedulur.models.doctor import Doctor
from schedulur.models.user import User
from schedulur.services.api_integration import ProviderDirectoryAPI

class DoctorSearchService:
    """Service for searching for doctors"""
    
    def __init__(self, api_key: str = None):
        # In future, use a real healthcare provider API
        self.api_key = api_key or os.environ.get('HEALTHCARE_API_KEY')
        self.mock_data_file = os.path.join(os.path.dirname(__file__), "../data/mock_doctors.json")
        self._ensure_mock_data()
        
        # Initialize the API integration
        self.api = ProviderDirectoryAPI()
        
        # Flag to use real API or mock data
        self.use_real_api = os.environ.get('USE_REAL_API', 'false').lower() == 'true'
        print(f"API Integration enabled: {self.use_real_api} (set USE_REAL_API=true to enable)")
        
    def _ensure_mock_data(self):
        """Create mock doctor data if it doesn't exist"""
        if not os.path.exists(self.mock_data_file):
            doctors = self._generate_mock_doctors()
            os.makedirs(os.path.dirname(self.mock_data_file), exist_ok=True)
            with open(self.mock_data_file, 'w') as f:
                json.dump([doc.dict() for doc in doctors], f, indent=2)
    
    def _generate_mock_doctors(self, count: int = 20) -> List[Doctor]:
        """Generate mock doctor data for testing"""
        specializations = [
            "Cardiology", "Dermatology", "Endocrinology", "Family Medicine", 
            "Gastroenterology", "Neurology", "Obstetrics", "Oncology", 
            "Ophthalmology", "Orthopedics", "Pediatrics", "Psychiatry"
        ]
        
        insurance_providers = [
            "Aetna", "Blue Cross", "Cigna", "Humana", "Medicare", "Medicaid", 
            "UnitedHealthcare", "Kaiser Permanente"
        ]
        
        states = {
            "CA": ["San Francisco", "Los Angeles", "San Diego"],
            "NY": ["New York", "Brooklyn", "Queens"],
            "TX": ["Austin", "Houston", "Dallas"],
            "FL": ["Miami", "Orlando", "Tampa"]
        }
        
        doctors = []
        for i in range(count):
            doctor_id = str(uuid.uuid4())
            specialization = specializations[i % len(specializations)]
            
            # Generate a somewhat geographically consistent location
            state = list(states.keys())[i % len(states)]
            city = states[state][i % len(states[state])]
            
            # Create zip code (fake)
            zip_code = f"{9 if state == 'CA' else (1 if state == 'NY' else (7 if state == 'TX' else 3))}{i % 10}{''.join([str(i % 10) for _ in range(3)])}"
            
            # Select 2-3 insurance providers
            accepted_insurance = [
                insurance_providers[i % len(insurance_providers)],
                insurance_providers[(i + 3) % len(insurance_providers)]
            ]
            if i % 3 == 0:
                accepted_insurance.append(insurance_providers[(i + 5) % len(insurance_providers)])
            
            doctors.append(Doctor(
                id=doctor_id,
                name=f"Dr. {'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[i % 26]} {'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[(i + 5) % 26]}. {'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[(i + 10) % 26]}{'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[(i + 15) % 26]}",
                specialization=specialization,
                practice_name=f"{city} {specialization} Group",
                email=f"doctor{i}@example.com",
                phone=f"555-{i:03d}-{(i+100):04d}"[-8:],
                website=f"https://doctor{i}.example.com",
                address=f"{(i + 100) % 999} Main St, Suite {i % 100 + 100}",
                city=city,
                state=state,
                zip_code=zip_code,
                accepted_insurance=accepted_insurance,
                appointment_duration=30 if i % 3 == 0 else (45 if i % 3 == 1 else 60)
            ))
        
        return doctors
    
    def search_doctors(self, 
                       specialization: str, 
                       insurance: Optional[str] = None,
                       zip_code: Optional[str] = None,
                       max_distance: Optional[int] = 25) -> List[Doctor]:
        """
        Search for doctors based on criteria
        
        Args:
            specialization: Type of doctor (e.g., "Cardiology", "Dermatology")
            insurance: User's insurance provider
            zip_code: User's zip code for distance calculations
            max_distance: Maximum distance in miles
            
        Returns:
            List of matching doctors
        """
        try:
            # Check if we should use the real API
            if self.use_real_api:
                return self._search_doctors_api(specialization, insurance, zip_code, max_distance)
            else:
                return self._search_doctors_mock(specialization, insurance, zip_code, max_distance)
        except Exception as e:
            print(f"Error searching for doctors: {e}")
            return []
            
    def _search_doctors_api(self, 
                           specialization: str, 
                           insurance: Optional[str] = None,
                           zip_code: Optional[str] = None,
                           max_distance: Optional[int] = 25) -> List[Doctor]:
        """Search for doctors using the real API"""
        try:
            print(f"Using real API to search for {specialization} doctors near {zip_code} within {max_distance} miles")
            
            # Search doctors via API
            results = self.api.search_doctors(
                specialization=specialization,
                zip_code=zip_code,
                radius_miles=max_distance
            )
            
            print(f"API search results: {len(results) if results else 0} doctors found")
            
            if not results:
                print("No results from API search")
                return []
                
            # Convert API results to Doctor objects
            doctors = []
            for doctor_data in results:
                # Format the data for our model
                formatted_data = self.api.doctor_to_model_format(doctor_data)
                
                # Add insurance info if we have it
                if insurance:
                    formatted_data["accepted_insurance"] = [insurance]
                
                # Add mock earliest available slot for now
                # In a real implementation, this would come from a scheduling API
                from datetime import timedelta
                i = len(doctors)
                days_offset = i % 5  # Days ahead for the appointment
                time_minutes = (i % 4) * 60  # Hours offset for the appointment time (0, 1, 2, or 3 hours)
                
                start_time = datetime.now().replace(hour=9, minute=0) + timedelta(days=days_offset, minutes=time_minutes)
                formatted_data["earliest_available_slot"] = start_time.strftime("%Y-%m-%d %H:%M")
                
                # Calculate approximate distance if we have coordinates
                if "latitude" in formatted_data and "longitude" in formatted_data and formatted_data["latitude"] and formatted_data["longitude"]:
                    # In a real implementation, we would use a proper distance calculation
                    formatted_data["distance_miles"] = (i * 2) % max_distance
                
                # Create a Doctor object
                doctor = Doctor(**formatted_data)
                doctors.append(doctor)
            
            # Sort by earliest available slot (most favorable) and distance (closest)
            doctors.sort(key=lambda d: (d.earliest_available_slot or "", d.distance_miles or float('inf')))
            
            return doctors
        except Exception as e:
            print(f"Error in API doctor search: {e}")
            return []
            
    def _search_doctors_mock(self, 
                            specialization: str, 
                            insurance: Optional[str] = None,
                            zip_code: Optional[str] = None,
                            max_distance: Optional[int] = 25) -> List[Doctor]:
        """Search for doctors using mock data"""
        try:
            with open(self.mock_data_file, 'r') as f:
                doctor_data = json.load(f)
            
            doctors = [Doctor(**doc) for doc in doctor_data]
            
            # Filter by specialization
            if specialization:
                doctors = [d for d in doctors if d.specialization.lower() == specialization.lower()]
            
            # Filter by insurance
            if insurance:
                doctors = [d for d in doctors if any(ins.lower() == insurance.lower() for ins in d.accepted_insurance)]
            
            # Add mock distance and sort by "distance"
            # In a real implementation, we would use geolocation APIs
            for i, doctor in enumerate(doctors):
                doctor.distance_miles = (i * 2) % max_distance
            
            # Limit results by distance
            doctors = [d for d in doctors if d.distance_miles <= max_distance]
            
            # Add mock earliest available slot
            from datetime import timedelta
            for i, doctor in enumerate(doctors):
                days_offset = i % 5  # Days ahead for the appointment
                time_minutes = (i % 4) * 60  # Hours offset for the appointment time (0, 1, 2, or 3 hours)
                
                start_time = datetime.now().replace(hour=9, minute=0) + timedelta(days=days_offset, minutes=time_minutes)
                doctor.earliest_available_slot = start_time.strftime("%Y-%m-%d %H:%M")
            
            # Sort by earliest available slot (most favorable) and distance (closest)
            doctors.sort(key=lambda d: (d.earliest_available_slot, d.distance_miles))
            
            return doctors
        
        except Exception as e:
            print(f"Error in mock doctor search: {e}")
            return []
    
    def search_with_claude(self, query: str) -> List[Doctor]:
        """
        Use Claude to search for doctors based on unstructured query
        
        Args:
            query: Natural language query
            
        Returns:
            List of matching doctors
        """
        # This would use Claude to parse the query and extract search parameters
        # Then call the regular search method
        # For now, just use a simple implementation
        
        # Extract specialty from query using basic keyword matching
        specialization = None
        specializations = {
            "cardiology": ["heart", "cardio", "chest pain", "cardiac"],
            "dermatology": ["skin", "dermatitis", "rash", "acne"],
            "neurology": ["brain", "neuro", "headache", "nerve"],
            "orthopedics": ["bone", "joint", "knee", "shoulder", "fracture"],
            "primary care": ["general", "family", "primary", "physical", "routine"],
            "pediatrics": ["child", "kid", "children", "pediatric"],
        }
        
        for specialty, keywords in specializations.items():
            if any(keyword in query.lower() for keyword in keywords):
                specialization = specialty
                break
        
        # Extract insurance from query
        insurance = None
        insurance_keywords = {
            "Aetna": ["aetna"],
            "Blue Cross": ["blue cross", "blue shield", "bcbs"],
            "Cigna": ["cigna"],
            "Humana": ["humana"],
            "Medicare": ["medicare"],
            "Medicaid": ["medicaid"],
            "UnitedHealthcare": ["united", "unitedhealthcare", "uhc"],
        }
        
        for ins, keywords in insurance_keywords.items():
            if any(keyword in query.lower() for keyword in keywords):
                insurance = ins
                break
        
        # Extract zip code from query using a simple regex
        import re
        zip_match = re.search(r'\b\d{5}\b', query)
        zip_code = zip_match.group(0) if zip_match else None
        
        # Estimate urgency based on urgency words
        urgency_level = 1
        urgency_keywords = {
            5: ["emergency", "urgent", "right away", "immediately", "severe"],
            4: ["very soon", "quickly", "asap", "pain", "concerning"],
            3: ["soon", "moderate", "uncomfortable"],
            2: ["regular", "routine", "checkup", "standard"],
            1: ["eventually", "when available", "no rush"]
        }
        
        for level, keywords in urgency_keywords.items():
            if any(keyword in query.lower() for keyword in keywords):
                urgency_level = level
                break
        
        # Get location if we have a zip code
        location_text = None
        if not zip_code:
            # Look for location mentions
            locations = ["san francisco", "los angeles", "new york", "chicago", "boston", "seattle", "miami"]
            for loc in locations:
                if loc in query.lower():
                    location_text = loc
                    break
        
        # Use the structured search with the extracted parameters
        return self.search_doctors(
            specialization=specialization or "Primary Care",
            insurance=insurance,
            zip_code=zip_code
        )