#!/usr/bin/env python

"""
Command-line demo for Schedulur appointment scheduling system.
Use this to demonstrate the core functionality without a web interface.
"""

import sys
import uuid
from datetime import datetime, time, timedelta
from typing import List, Dict, Optional

# Import models and services
from schedulur.models.user import User
from schedulur.models.provider import Provider
from schedulur.models.appointment import Appointment
from schedulur.services.user_service import UserService
from schedulur.services.provider_service import ProviderService
from schedulur.services.appointment_service import AppointmentService
from schedulur.utils.scheduling import SchedulingOptimizer
from schedulur.utils.date_helpers import parse_time_string, format_time, day_name, format_availability

# Sample data for demo
def create_sample_data():
    # Create users
    user1 = User(
        name="John Doe",
        email="john@example.com",
        phone="555-123-4567",
        available_days=[0, 1, 2, 3, 4],  # Monday-Friday
        available_times=[
            {"start_time": parse_time_string("09:00"), "end_time": parse_time_string("17:00")}
        ],
        insurance_provider="BlueShield",
        insurance_id="BS12345678"
    )
    
    user2 = User(
        name="Jane Smith",
        email="jane@example.com",
        phone="555-987-6543",
        available_days=[1, 3, 5],  # Tuesday, Thursday, Saturday
        available_times=[
            {"start_time": parse_time_string("10:00"), "end_time": parse_time_string("18:00")}
        ],
        insurance_provider="HealthFirst",
        insurance_id="HF87654321"
    )
    
    # Create providers
    provider1 = Provider(
        name="Dr. Alice Johnson",
        specialization="Cardiologist",
        location="123 Medical Center, New York, NY",
        email="alice@hospital.com",
        phone="555-111-2222",
        available_days=[0, 1, 2, 3, 4],  # Monday-Friday
        available_times=[
            {"day": 0, "start_time": parse_time_string("08:00"), "end_time": parse_time_string("16:00")},
            {"day": 1, "start_time": parse_time_string("08:00"), "end_time": parse_time_string("16:00")},
            {"day": 2, "start_time": parse_time_string("08:00"), "end_time": parse_time_string("16:00")},
            {"day": 3, "start_time": parse_time_string("08:00"), "end_time": parse_time_string("16:00")},
            {"day": 4, "start_time": parse_time_string("08:00"), "end_time": parse_time_string("16:00")}
        ],
        accepted_insurance=["BlueShield", "Medicare", "HealthFirst"],
        appointment_duration=30
    )
    
    provider2 = Provider(
        name="Dr. Bob Williams",
        specialization="Dermatologist",
        location="456 Skin Clinic, New York, NY",
        email="bob@skinclinic.com",
        phone="555-333-4444",
        available_days=[1, 3, 5],  # Tuesday, Thursday, Saturday
        available_times=[
            {"day": 1, "start_time": parse_time_string("09:00"), "end_time": parse_time_string("17:00")},
            {"day": 3, "start_time": parse_time_string("09:00"), "end_time": parse_time_string("17:00")},
            {"day": 5, "start_time": parse_time_string("10:00"), "end_time": parse_time_string("15:00")}
        ],
        accepted_insurance=["BlueShield", "UnitedHealth"],
        appointment_duration=45
    )
    
    provider3 = Provider(
        name="Dr. Carol Martinez",
        specialization="Neurologist",
        location="789 Brain Center, New York, NY",
        email="carol@braincenter.com",
        phone="555-555-6666",
        available_days=[0, 2, 4],  # Monday, Wednesday, Friday
        available_times=[
            {"day": 0, "start_time": parse_time_string("10:00"), "end_time": parse_time_string("18:00")},
            {"day": 2, "start_time": parse_time_string("10:00"), "end_time": parse_time_string("18:00")},
            {"day": 4, "start_time": parse_time_string("10:00"), "end_time": parse_time_string("18:00")}
        ],
        accepted_insurance=["Medicare", "HealthFirst"],
        appointment_duration=60
    )
    
    # Save users and providers
    users = [user1, user2]
    providers = [provider1, provider2, provider3]
    
    saved_users = []
    saved_providers = []
    
    for user in users:
        saved_users.append(UserService.create_user(user))
    
    for provider in providers:
        saved_providers.append(ProviderService.create_provider(provider))
    
    return saved_users, saved_providers

def print_separator():
    print("\n" + "-" * 80 + "\n")

def display_user_info(user: User):
    print(f"User: {user.name} (ID: {user.id})")
    print(f"Email: {user.email}")
    print(f"Phone: {user.phone}")
    print(f"Insurance: {user.insurance_provider or 'None'} (ID: {user.insurance_id or 'None'})")
    print("\nAvailability:")
    print(format_availability(user.available_days, user.available_times))

def display_provider_info(provider: Provider):
    print(f"Provider: {provider.name} (ID: {provider.id})")
    print(f"Specialization: {provider.specialization}")
    print(f"Location: {provider.location}")
    print(f"Contact: {provider.email}, {provider.phone}")
    print(f"Appointment Duration: {provider.appointment_duration} minutes")
    print(f"\nAccepted Insurance:")
    if provider.accepted_insurance:
        for ins in provider.accepted_insurance:
            print(f"- {ins}")
    else:
        print("- None specified")
    
    print("\nAvailability:")
    print(format_availability(provider.available_days, provider.available_times))

def display_appointment_info(appointment: Appointment):
    user = UserService.get_user(appointment.user_id)
    provider = ProviderService.get_provider(appointment.provider_id)
    
    user_name = user.name if user else "Unknown User"
    provider_name = provider.name if provider else "Unknown Provider"
    
    print(f"Appointment ID: {appointment.id}")
    print(f"Status: {appointment.status.upper()}")
    print(f"User: {user_name} (ID: {appointment.user_id})")
    print(f"Provider: {provider_name} (ID: {appointment.provider_id})")
    print(f"Start: {appointment.start_time.strftime('%A, %B %d, %Y at %I:%M %p')}")
    print(f"End: {appointment.end_time.strftime('%A, %B %d, %Y at %I:%M %p')}")
    
    if appointment.notes:
        print(f"Notes: {appointment.notes}")

def display_available_slots(slots: List[Dict]):
    if not slots:
        print("No available slots found.")
        return
    
    for i, slot in enumerate(slots, 1):
        start = slot['start_time']
        end = slot['end_time']
        print(f"{i}. {start.strftime('%A, %B %d, %Y at %I:%M %p')} - {end.strftime('%I:%M %p')}")

def display_best_providers(results: List[Dict]):
    if not results:
        print("No suitable providers found.")
        return
    
    for i, result in enumerate(results, 1):
        provider = result['provider']
        slots = result['available_slots']
        total_slots = result['total_available_slots']
        
        print(f"{i}. {provider.name} - {provider.specialization}")
        print(f"   Location: {provider.location}")
        print(f"   Insurance: {', '.join(provider.accepted_insurance)}")
        print(f"   Total available slots: {total_slots}")
        
        if slots:
            print("   Example slots:")
            for slot in slots:
                start = slot['start_time']
                end = slot['end_time']
                print(f"   - {start.strftime('%A, %B %d at %I:%M %p')} - {end.strftime('%I:%M %p')}")
        
        print()

def display_appointment_sequence(plan: Dict):
    user = plan['user']
    print(f"Appointment sequence plan for {user.name}:")
    print()
    
    for item in plan['appointment_plan']:
        print(f"Specialization: {item['specialization']}")
        print(f"Status: {item['status']}")
        
        if item['status'] == 'providers_found':
            print(f"Top providers:")
            for provider_item in item['providers']:
                provider = provider_item['provider']
                total_slots = provider_item['total_available_slots']
                print(f"- {provider.name}: {total_slots} available slots")
        
        print()

def schedule_appointment(user_id: str, provider_id: str):
    user = UserService.get_user(user_id)
    provider = ProviderService.get_provider(provider_id)
    
    if not user or not provider:
        print("Invalid user or provider ID.")
        return
    
    print(f"Scheduling appointment with {provider.name} for {user.name}")
    
    # Find available days in the next 30 days
    today = datetime.now()
    available_days = []
    
    for i in range(30):
        check_date = today + timedelta(days=i)
        weekday = check_date.weekday()
        
        if weekday in provider.available_days and weekday in user.available_days:
            available_days.append(check_date.date())
    
    if not available_days:
        print("No common available days found in the next 30 days.")
        return
    
    # Display available days
    print("\nAvailable days:")
    for i, day in enumerate(available_days[:10], 1):  # Show only first 10
        print(f"{i}. {day.strftime('%A, %B %d, %Y')}")
    
    # Ask user to select a day
    day_choice = int(input("\nSelect a day (number): "))
    if day_choice < 1 or day_choice > len(available_days[:10]):
        print("Invalid selection.")
        return
    
    selected_date = available_days[day_choice-1]
    
    # Find available slots for that day
    date_time = datetime.combine(selected_date, datetime.min.time())
    slots = AppointmentService.find_available_slots(provider_id, date_time, provider.appointment_duration)
    
    if not slots:
        print(f"No available slots on {selected_date.strftime('%A, %B %d, %Y')}.")
        return
    
    # Display available slots
    print(f"\nAvailable slots on {selected_date.strftime('%A, %B %d, %Y')}:")
    display_available_slots(slots)
    
    # Ask user to select a slot
    slot_choice = int(input("\nSelect a slot (number): "))
    if slot_choice < 1 or slot_choice > len(slots):
        print("Invalid selection.")
        return
    
    selected_slot = slots[slot_choice-1]
    
    # Create the appointment
    appointment = Appointment(
        user_id=user_id,
        provider_id=provider_id,
        start_time=selected_slot['start_time'],
        end_time=selected_slot['end_time'],
        status="scheduled",
        notes=f"Scheduled via CLI demo on {datetime.now().strftime('%Y-%m-%d')}."
    )
    
    created_appointment = AppointmentService.create_appointment(appointment)
    
    if created_appointment:
        print("\nAppointment successfully scheduled!")
        print_separator()
        display_appointment_info(created_appointment)
    else:
        print("\nFailed to schedule appointment. Please try again.")

def main_menu():
    while True:
        print_separator()
        print("SCHEDULUR - Appointment Scheduling System")
        print_separator()
        print("1. Create sample data")
        print("2. View all users")
        print("3. View all providers")
        print("4. View all appointments")
        print("5. Schedule an appointment")
        print("6. Find best providers for a user")
        print("7. Create appointment sequence plan")
        print("8. Exit")
        
        choice = input("\nEnter your choice (1-8): ")
        
        if choice == "1":
            users, providers = create_sample_data()
            print(f"Created {len(users)} users and {len(providers)} providers.")
        
        elif choice == "2":
            users = UserService.list_users()
            if not users:
                print("No users found. Create sample data first.")
                continue
                
            print_separator()
            print(f"USERS ({len(users)})")
            print_separator()
            
            for user in users:
                display_user_info(user)
                print()
        
        elif choice == "3":
            providers = ProviderService.list_providers()
            if not providers:
                print("No providers found. Create sample data first.")
                continue
                
            print_separator()
            print(f"PROVIDERS ({len(providers)})")
            print_separator()
            
            for provider in providers:
                display_provider_info(provider)
                print_separator()
        
        elif choice == "4":
            appointments = AppointmentService.list_appointments()
            if not appointments:
                print("No appointments found. Schedule some appointments first.")
                continue
                
            print_separator()
            print(f"APPOINTMENTS ({len(appointments)})")
            print_separator()
            
            for appointment in appointments:
                display_appointment_info(appointment)
                print_separator()
        
        elif choice == "5":
            users = UserService.list_users()
            providers = ProviderService.list_providers()
            
            if not users or not providers:
                print("No users or providers found. Create sample data first.")
                continue
            
            print_separator()
            print("USERS:")
            for i, user in enumerate(users, 1):
                print(f"{i}. {user.name} (Insurance: {user.insurance_provider or 'None'})")
            
            user_choice = int(input("\nSelect a user (number): "))
            if user_choice < 1 or user_choice > len(users):
                print("Invalid selection.")
                continue
            
            selected_user = users[user_choice-1]
            
            print_separator()
            print("PROVIDERS:")
            for i, provider in enumerate(providers, 1):
                print(f"{i}. {provider.name} - {provider.specialization}")
                print(f"   Insurance: {', '.join(provider.accepted_insurance)}")
            
            provider_choice = int(input("\nSelect a provider (number): "))
            if provider_choice < 1 or provider_choice > len(providers):
                print("Invalid selection.")
                continue
            
            selected_provider = providers[provider_choice-1]
            
            # Check insurance compatibility
            if (selected_user.insurance_provider and 
                selected_user.insurance_provider not in selected_provider.accepted_insurance):
                print(f"\nWARNING: {selected_provider.name} does not accept {selected_user.insurance_provider} insurance.")
                continue_anyway = input("Continue anyway? (y/n): ").lower()
                if continue_anyway != 'y':
                    continue
            
            schedule_appointment(selected_user.id, selected_provider.id)
        
        elif choice == "6":
            users = UserService.list_users()
            
            if not users:
                print("No users found. Create sample data first.")
                continue
            
            print_separator()
            print("USERS:")
            for i, user in enumerate(users, 1):
                print(f"{i}. {user.name} (Insurance: {user.insurance_provider or 'None'})")
            
            user_choice = int(input("\nSelect a user (number): "))
            if user_choice < 1 or user_choice > len(users):
                print("Invalid selection.")
                continue
            
            selected_user = users[user_choice-1]
            
            specialization = input("\nEnter specialization (leave blank for any): ").strip()
            
            print_separator()
            print(f"Finding best providers for {selected_user.name}")
            print(f"Specialization: {specialization or 'Any'}")
            print(f"Insurance: {selected_user.insurance_provider or 'None'}")
            print_separator()
            
            results = SchedulingOptimizer.find_best_providers(
                selected_user, 
                specialization if specialization else None
            )
            
            display_best_providers(results)
        
        elif choice == "7":
            users = UserService.list_users()
            
            if not users:
                print("No users found. Create sample data first.")
                continue
            
            print_separator()
            print("USERS:")
            for i, user in enumerate(users, 1):
                print(f"{i}. {user.name} (Insurance: {user.insurance_provider or 'None'})")
            
            user_choice = int(input("\nSelect a user (number): "))
            if user_choice < 1 or user_choice > len(users):
                print("Invalid selection.")
                continue
            
            selected_user = users[user_choice-1]
            
            print("\nEnter required specializations (comma-separated):")
            print("Example: Cardiologist, Neurologist, Dermatologist")
            specializations = [s.strip() for s in input("> ").split(',')]
            
            if not specializations or specializations[0] == '':
                print("No specializations entered.")
                continue
            
            print_separator()
            print(f"Creating appointment sequence plan for {selected_user.name}")
            print(f"Required specializations: {', '.join(specializations)}")
            print_separator()
            
            plan = SchedulingOptimizer.recommend_appointment_sequence(selected_user, specializations)
            display_appointment_sequence(plan)
        
        elif choice == "8":
            print("Thank you for using Schedulur. Goodbye!")
            sys.exit(0)
        
        else:
            print("Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
