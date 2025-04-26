import requests
import os
import time
from typing import List, Dict, Optional
from math import cos, radians
from geopy.geocoders import Nominatim

# API Integration for Provider Directory

class ProviderDirectoryAPI:
    """Integration with the Provider Directory API"""
    
    def __init__(self, api_key: Optional[str] = None):
        # The API key is needed for some APIs
        self.api_key = api_key or os.environ.get('PROVIDER_API_KEY')
        
        # Headers for API requests
        self.headers = {
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Origin': 'https://home.trillianthealth.com',
            'Referer': 'https://home.trillianthealth.com/',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)',
            'accept': 'application/json',
            'content-type': 'application/json',
        }
        
        # Authorization token, would typically come from an OAuth flow or similar
        # For demo purposes, this would be refreshed as needed
        self._add_authorization()
    
    def _add_authorization(self):
        """Add authorization token to headers"""
        # In a real app, this would get a fresh token from OAuth or similar
        # This is a placeholder token for demo purposes
        token = os.environ.get('PROVIDER_API_TOKEN')
        if token:
            self.headers['authorization'] = f'Bearer {token}'
    
    def get_provider_details(self, npi: str) -> Dict:
        """
        Get detailed information about a provider by NPI number
        
        Args:
            npi: National Provider Identifier
            
        Returns:
            Provider details as a dictionary
        """
        url = f"https://api.stable.uaap.trillianthealth.com/api/provider-directory/providers/{npi}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching provider details: {e}")
            return {}
    
    def get_location_bounds(self, zip_code: str, radius_miles: int = 10) -> Dict:
        """
        Get geographical bounds for a given zip code and radius
        
        Args:
            zip_code: ZIP code to search around
            radius_miles: Radius to search in miles
            
        Returns:
            Dictionary with northEast and southWest bounds
        """
        try:
            geolocator = Nominatim(user_agent="schedulur-app")
            location = geolocator.geocode(f'{zip_code}, United States')
            
            if location is None:
                return None
                
            lat = location.latitude
            lon = location.longitude
            
            # Convert miles to kilometers for calculation
            radius_km = radius_miles * 1.60934
            
            # Approximate degrees lat/lon for the given radius
            lat_offset = radius_km / 110.574
            lon_offset = radius_km / (111.320 * cos(radians(lat)))
            
            return {
                'northEast': {
                    'lat': lat + lat_offset,
                    'lng': lon + lon_offset
                },
                'southWest': {
                    'lat': lat - lat_offset,
                    'lng': lon - lon_offset
                }
            }
        except Exception as e:
            print(f"Error getting location bounds: {e}")
            return None
    
    def search_doctors(self, 
                     specialization: str,
                     location_text: Optional[str] = None,
                     zip_code: Optional[str] = None,
                     radius_miles: int = 10) -> List[Dict]:
        """
        Search for doctors by specialty and location
        
        Args:
            specialization: Medical specialty (e.g., "Cardiology")
            location_text: Location description (e.g., "San Francisco, CA")
            zip_code: ZIP code to search around
            radius_miles: Radius to search in miles
            
        Returns:
            List of doctors matching the criteria
        """
        url = 'https://api.stable.uaap.trillianthealth.com/api/provider-directory/providers:search?pageSize=100&pageNumber=0'
        
        # Get location bounds from zip code
        location_bounds = None
        if zip_code:
            location_bounds = self.get_location_bounds(zip_code, radius_miles)
            # If we couldn't get location bounds, default to the location_text
            if not location_bounds and not location_text:
                location_text = f"{zip_code}, United States"
        
        # Adjust specialization for API search
        # Map common specialties to their corresponding values in the API
        specialty_mapping = {
            "cardiology": ["Cardiology Physician", "Cardiovascular Disease Physician", "Interventional Cardiology Physician"],
            "dermatology": ["Dermatology Physician"],
            "pediatrics": ["Pediatrics Physician"],
            "neurology": ["Neurology Physician"],
            "orthopedics": ["Orthopedic Surgery Physician"],
            "primary care": ["Family Medicine Physician", "Internal Medicine Physician", "General Practice Physician"],
            "allergy": ["Allergy & Immunology Physician", "Allergy Physician"],
            "psychiatry": ["Psychiatry Physician", "Psychiatrist & Neurology Physician"],
        }
        
        # Default to exact specialization if no mapping found
        specialties = specialty_mapping.get(specialization.lower(), [specialization])
        
        # Prepare payload for API request
        payload = {
            'specialties': specialties,
            'locationCulling': False
        }
        
        # Add location parameters
        if location_text:
            payload['locationText'] = location_text
        
        if location_bounds:
            payload['locationBounds'] = location_bounds
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            result = response.json()
            
            # Return the list of doctors
            return result.get('items', [])
        except Exception as e:
            print(f"Error searching for doctors: {e}")
            return []
            
    def doctor_to_model_format(self, doctor_data: Dict) -> Dict:
        """
        Convert API doctor data to the format expected by our Doctor model
        
        Args:
            doctor_data: Doctor data from the API
            
        Returns:
            Dictionary formatted for our Doctor model
        """
        entity = doctor_data.get('entityShort', {})
        location = doctor_data.get('displayLocation', {})
        
        # Build a properly formatted doctor dictionary
        return {
            "id": entity.get('provider_id'),
            "name": f"Dr. {entity.get('provider_first_name', '')} {entity.get('provider_last_name', '')}".strip(),
            "specialization": entity.get('provider_primary_specialty_description', '').replace(' Physician', ''),
            "npi": str(entity.get('provider_npi', '')),
            "practice_name": entity.get('primary_organization_name', ''),
            "address": entity.get('provider_affiliated_practice_1_street_address', ''),
            "city": location.get('city', entity.get('provider_affiliated_practice_1_city', '')),
            "state": location.get('state', entity.get('provider_affiliated_practice_1_state', '')),
            "zip_code": location.get('zipCode', entity.get('provider_affiliated_practice_1_zip_code', '')),
            "latitude": location.get('latitude', entity.get('provider_affiliated_practice_1_latitude')),
            "longitude": location.get('longitude', entity.get('provider_affiliated_practice_1_longitude')),
            # Format phone if available
            "phone": self._format_phone(entity.get('provider_affiliated_practice_1_phone_number', '')),
            # Default values
            "accepted_insurance": [],  # Would need additional API call to get this
            "appointment_duration": 30  # Default
        }
    
    def _format_phone(self, phone: str) -> str:
        """Format phone number as XXX-XXX-XXXX"""
        if not phone or len(phone) < 10:
            return ""
        
        # Strip non-numeric characters
        digits = ''.join(c for c in phone if c.isdigit())
        
        # Format as XXX-XXX-XXXX
        if len(digits) == 10:
            return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits[0] == '1':
            return f"{digits[1:4]}-{digits[4:7]}-{digits[7:]}"
        else:
            return phone
            
    def get_provider_details_formatted(self, npi: str) -> Dict:
        """
        Get detailed provider information and format it for our model
        
        Args:
            npi: National Provider Identifier
            
        Returns:
            Dictionary formatted for our Doctor model
        """
        # Get provider details from API
        provider_data = self.get_provider_details(npi)
        
        if not provider_data or 'entity' not in provider_data:
            return {}
            
        entity = provider_data.get('entity', {})
        
        # Format the data for our model
        return {
            "id": entity.get('provider_id'),
            "name": f"Dr. {entity.get('provider_first_name', '')} {entity.get('provider_last_name', '')}".strip(),
            "specialization": entity.get('provider_primary_specialty_description', '').replace(' Physician', ''),
            "npi": str(entity.get('provider_npi', '')),
            "practice_name": entity.get('primary_organization_name', ''),
            "address": entity.get('provider_affiliated_practice_1_street_address', ''),
            "city": entity.get('provider_affiliated_practice_1_city', ''),
            "state": entity.get('provider_affiliated_practice_1_state', ''),
            "zip_code": entity.get('provider_affiliated_practice_1_zip_code', ''),
            "latitude": entity.get('provider_affiliated_practice_1_latitude'),
            "longitude": entity.get('provider_affiliated_practice_1_longitude'),
            # Format phone if available
            "phone": self._format_phone(entity.get('provider_affiliated_practice_1_phone_number', '')),
            # Default values
            "accepted_insurance": [],  # Would need additional API call to get this
            "appointment_duration": 30  # Default
        }