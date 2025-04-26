import unittest
import tempfile
import os
from schedulur.models.doctor import Doctor
from schedulur.services.doctor_service import DoctorService

class TestDoctorService(unittest.TestCase):
    
    def setUp(self):
        # Create a temporary data file for testing
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.temp_file.close()
        
        # Initialize the service with the temp file
        self.doctor_service = DoctorService(self.temp_file.name)
    
    def tearDown(self):
        # Clean up the temp file
        os.unlink(self.temp_file.name)
    
    def test_create_doctor(self):
        doctor = Doctor(
            name="Dr. Test",
            specialization="Testing",
            location="Test Hospital",
            email="test@example.com",
            phone="123-456-7890",
            accepted_insurance=["TestInsurance"]
        )
        
        created_doctor = self.doctor_service.create_doctor(doctor)
        
        self.assertIsNotNone(created_doctor.id)
        self.assertEqual(created_doctor.name, "Dr. Test")
        self.assertEqual(created_doctor.specialization, "Testing")
        
        # Should be retrievable
        retrieved_doctor = self.doctor_service.get_doctor(created_doctor.id)
        self.assertEqual(retrieved_doctor.name, created_doctor.name)
    
    def test_update_doctor(self):
        # First create a doctor
        doctor = Doctor(
            name="Dr. Original",
            specialization="Original",
            location="Original Hospital"
        )
        
        created_doctor = self.doctor_service.create_doctor(doctor)
        
        # Now update the doctor
        updated_doctor = Doctor(
            name="Dr. Updated",
            specialization="Updated",
            location="Updated Hospital"
        )
        
        result = self.doctor_service.update_doctor(created_doctor.id, updated_doctor)
        
        self.assertEqual(result.name, "Dr. Updated")
        
        # Check the update was persisted
        retrieved_doctor = self.doctor_service.get_doctor(created_doctor.id)
        self.assertEqual(retrieved_doctor.name, "Dr. Updated")
    
    def test_delete_doctor(self):
        # First create a doctor
        doctor = Doctor(
            name="Dr. ToDelete",
            specialization="Temporary",
            location="Temp Hospital"
        )
        
        created_doctor = self.doctor_service.create_doctor(doctor)
        
        # Verify it exists
        self.assertIsNotNone(self.doctor_service.get_doctor(created_doctor.id))
        
        # Now delete it
        result = self.doctor_service.delete_doctor(created_doctor.id)
        
        self.assertTrue(result)
        self.assertIsNone(self.doctor_service.get_doctor(created_doctor.id))
    
    def test_filter_by_specialization(self):
        # Create doctors with different specializations
        doctor1 = Doctor(name="Dr. One", specialization="Cardiology", location="Hospital")
        doctor2 = Doctor(name="Dr. Two", specialization="Neurology", location="Hospital")
        doctor3 = Doctor(name="Dr. Three", specialization="Cardiology", location="Hospital")
        
        self.doctor_service.create_doctor(doctor1)
        self.doctor_service.create_doctor(doctor2)
        self.doctor_service.create_doctor(doctor3)
        
        # Filter by specialization
        cardiologists = self.doctor_service.filter_doctors_by_specialization("Cardiology")
        
        self.assertEqual(len(cardiologists), 2)
        self.assertTrue(all(d.specialization == "Cardiology" for d in cardiologists))
        
        neurologists = self.doctor_service.filter_doctors_by_specialization("Neurology")
        self.assertEqual(len(neurologists), 1)
        self.assertEqual(neurologists[0].specialization, "Neurology")

if __name__ == "__main__":
    unittest.main()