from schedulur.models.user import User
from schedulur.models.provider import Provider
from schedulur.services.appointment_service import AppointmentService
from typing import List, Dict
from datetime import datetime, timedelta

class SchedulingOptimizer:
    @staticmethod
    def find_best_providers(user: User, specialization: str = None, max_results: int = 5) -> List[Dict]:
        """Find the best providers based on insurance coverage and availability matching user's schedule."""
        from schedulur.services.provider_service import ProviderService
        
        # Get all providers or filter by specialization
        if specialization:
            providers = ProviderService.filter_providers_by_specialization(specialization)
        else:
            providers = ProviderService.list_providers()
        
        # Filter by insurance if user has insurance
        if user.insurance_provider:
            providers = [p for p in providers if user.insurance_provider in p.accepted_insurance]
        
        # No matching providers
        if not providers:
            return []
        
        results = []
        
        for provider in providers:
            # Check for overlapping availability days
            common_days = set(user.available_days).intersection(set(provider.available_days))
            if not common_days:
                continue
            
            # Find all available appointment slots for the next 30 days
            available_slots = []
            current_date = datetime.now()
            end_date = current_date + timedelta(days=30)
            
            while current_date <= end_date:
                # Only check on days that both user and provider are available
                if current_date.weekday() in common_days:
                    # Get provider's available slots for this day
                    day_slots = AppointmentService.find_available_slots(
                        provider.id, 
                        current_date,
                        provider.appointment_duration
                    )
                    
                    # Filter slots based on user's available times
                    for slot in day_slots:
                        slot_start_time = slot['start_time'].time()
                        slot_end_time = slot['end_time'].time()
                        
                        # Check if slot is within user's available times
                        for user_time in user.available_times:
                            if slot_start_time >= user_time['start_time'] and slot_end_time <= user_time['end_time']:
                                available_slots.append(slot)
                                break
                
                current_date += timedelta(days=1)
            
            # Add provider to results if there are available slots
            if available_slots:
                results.append({
                    'provider': provider,
                    'available_slots': available_slots[:3],  # Just include first 3 slots as preview
                    'total_available_slots': len(available_slots)
                })
        
        # Sort by number of available slots (most flexible providers first)
        results.sort(key=lambda x: x['total_available_slots'], reverse=True)
        
        return results[:max_results]
    
    @staticmethod
    def recommend_appointment_sequence(user: User, required_specializations: List[str]) -> Dict:
        """Recommend a sequence of appointments across multiple specializations."""
        appointment_plan = []
        
        for specialization in required_specializations:
            # Find best providers for this specialization
            providers = SchedulingOptimizer.find_best_providers(user, specialization, max_results=3)
            
            if not providers:
                appointment_plan.append({
                    'specialization': specialization,
                    'status': 'no_providers_found',
                    'providers': []
                })
                continue
            
            appointment_plan.append({
                'specialization': specialization,
                'status': 'providers_found',
                'providers': providers
            })
        
        return {
            'user': user,
            'appointment_plan': appointment_plan
        }