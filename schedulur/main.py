from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
from datetime import datetime, time
import uvicorn

# Import models
from schedulur.models.user import User
from schedulur.models.provider import Provider
from schedulur.models.appointment import Appointment

# Import services
from schedulur.services.user_service import UserService
from schedulur.services.provider_service import ProviderService
from schedulur.services.appointment_service import AppointmentService

# Import utilities
from schedulur.utils.scheduling import SchedulingOptimizer

# Create FastAPI app
app = FastAPI(title="Schedulur API", description="API for scheduling appointments with healthcare providers")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/")
async def read_root():
    return {"status": "healthy", "app": "Schedulur API"}

# User endpoints
@app.post("/users/", response_model=User)
async def create_user(user: User):
    return UserService.create_user(user)

@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    user = UserService.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/users/{user_id}", response_model=User)
async def update_user(user_id: str, user: User):
    updated_user = UserService.update_user(user_id, user)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@app.delete("/users/{user_id}")
async def delete_user(user_id: str):
    success = UserService.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}

@app.get("/users/", response_model=List[User])
async def list_users():
    return UserService.list_users()

# Provider endpoints
@app.post("/providers/", response_model=Provider)
async def create_provider(provider: Provider):
    return ProviderService.create_provider(provider)

@app.get("/providers/{provider_id}", response_model=Provider)
async def get_provider(provider_id: str):
    provider = ProviderService.get_provider(provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider

@app.put("/providers/{provider_id}", response_model=Provider)
async def update_provider(provider_id: str, provider: Provider):
    updated_provider = ProviderService.update_provider(provider_id, provider)
    if not updated_provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return updated_provider

@app.delete("/providers/{provider_id}")
async def delete_provider(provider_id: str):
    success = ProviderService.delete_provider(provider_id)
    if not success:
        raise HTTPException(status_code=404, detail="Provider not found")
    return {"message": "Provider deleted successfully"}

@app.get("/providers/", response_model=List[Provider])
async def list_providers(
    specialization: Optional[str] = None,
    insurance: Optional[str] = None
):
    if specialization and insurance:
        # Filter by both
        providers_by_specialization = ProviderService.filter_providers_by_specialization(specialization)
        return [p for p in providers_by_specialization if insurance in p.accepted_insurance]
    elif specialization:
        return ProviderService.filter_providers_by_specialization(specialization)
    elif insurance:
        return ProviderService.filter_providers_by_insurance(insurance)
    else:
        return ProviderService.list_providers()

# Appointment endpoints
@app.post("/appointments/", response_model=Appointment)
async def create_appointment(appointment: Appointment):
    created_appointment = AppointmentService.create_appointment(appointment)
    if not created_appointment:
        raise HTTPException(status_code=400, detail="Could not create appointment. Check user/provider IDs, insurance compatibility, and slot availability.")
    return created_appointment

@app.get("/appointments/{appointment_id}", response_model=Appointment)
async def get_appointment(appointment_id: str):
    appointment = AppointmentService.get_appointment(appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment

@app.put("/appointments/{appointment_id}", response_model=Appointment)
async def update_appointment(appointment_id: str, appointment: Appointment):
    updated_appointment = AppointmentService.update_appointment(appointment_id, appointment)
    if not updated_appointment:
        raise HTTPException(status_code=400, detail="Could not update appointment. Check slot availability.")
    return updated_appointment

@app.delete("/appointments/{appointment_id}")
async def delete_appointment(appointment_id: str):
    success = AppointmentService.delete_appointment(appointment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return {"message": "Appointment deleted successfully"}

@app.get("/appointments/", response_model=List[Appointment])
async def list_appointments(
    user_id: Optional[str] = None,
    provider_id: Optional[str] = None
):
    if user_id:
        return AppointmentService.get_user_appointments(user_id)
    elif provider_id:
        return AppointmentService.get_provider_appointments(provider_id)
    else:
        return AppointmentService.list_appointments()

@app.post("/appointments/{appointment_id}/cancel")
async def cancel_appointment(appointment_id: str):
    success = AppointmentService.cancel_appointment(appointment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return {"message": "Appointment cancelled successfully"}

# Available slots endpoint
@app.get("/providers/{provider_id}/available-slots")
async def get_available_slots(
    provider_id: str,
    date: str,
    duration_minutes: Optional[int] = None
):
    try:
        # Parse the date string into a datetime object
        parsed_date = datetime.strptime(date, "%Y-%m-%d")
        
        # If duration is not specified, get it from the provider
        if not duration_minutes:
            provider = ProviderService.get_provider(provider_id)
            if not provider:
                raise HTTPException(status_code=404, detail="Provider not found")
            duration_minutes = provider.appointment_duration
        
        slots = AppointmentService.find_available_slots(provider_id, parsed_date, duration_minutes)
        
        # Convert datetime objects to strings for JSON response
        formatted_slots = [
            {
                'start_time': slot['start_time'].isoformat(),
                'end_time': slot['end_time'].isoformat()
            } for slot in slots
        ]
        
        return formatted_slots
    
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

# Scheduling optimization endpoints
@app.get("/users/{user_id}/best-providers")
async def find_best_providers(
    user_id: str,
    specialization: Optional[str] = None,
    max_results: Optional[int] = 5
):
    user = UserService.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    results = SchedulingOptimizer.find_best_providers(user, specialization, max_results)
    
    # Format the results for JSON response
    formatted_results = []
    for result in results:
        formatted_slots = [
            {
                'start_time': slot['start_time'].isoformat(),
                'end_time': slot['end_time'].isoformat()
            } for slot in result['available_slots']
        ]
        
        formatted_results.append({
            'provider': result['provider'],
            'available_slots': formatted_slots,
            'total_available_slots': result['total_available_slots']
        }
    
    return formatted_results

@app.post("/users/{user_id}/appointment-sequence")
async def recommend_appointment_sequence(
    user_id: str,
    required_specializations: List[str]
):
    user = UserService.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    result = SchedulingOptimizer.recommend_appointment_sequence(user, required_specializations)
    
    # Format the results for JSON response
    formatted_plan = []
    for plan_item in result['appointment_plan']:
        formatted_providers = []
        
        for provider_item in plan_item['providers']:
            formatted_slots = [
                {
                    'start_time': slot['start_time'].isoformat(),
                    'end_time': slot['end_time'].isoformat()
                } for slot in provider_item['available_slots']
            ]
            
            formatted_providers.append({
                'provider': provider_item['provider'],
                'available_slots': formatted_slots,
                'total_available_slots': provider_item['total_available_slots']
            }
        
        formatted_plan.append({
            'specialization': plan_item['specialization'],
            'status': plan_item['status'],
            'providers': formatted_providers
        })
    
    return {
        'user': result['user'],
        'appointment_plan': formatted_plan
    }

# Run the application
if __name__ == "__main__":
    uvicorn.run("schedulur.main:app", host="0.0.0.0", port=8000, reload=True)