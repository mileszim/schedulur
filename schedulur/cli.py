#!/usr/bin/env python

import argparse
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json

from schedulur.models.doctor import Doctor
from schedulur.models.appointment import Appointment
from schedulur.services.doctor_service import DoctorService
from schedulur.services.appointment_service import AppointmentService
from schedulur.integrations.calendar import CalendarService
from schedulur.integrations.communication import CommunicationService

class CLI:
    """Command-line interface for Schedulur"""
    
    def __init__(self):
        self.doctor_service = DoctorService()
        self.appointment_service = AppointmentService()
        self.calendar_service = CalendarService()
        self.communication_service = CommunicationService()
        
        self.parser = argparse.ArgumentParser(description="Schedulur - Medical Appointment Scheduler")
        self.setup_parsers()
    
    def setup_parsers(self):
        """Set up command-line argument parsers"""
        subparsers = self.parser.add_subparsers(dest="command", help="Command")
        
        # Doctor commands
        doctor_parser = subparsers.add_parser("doctor", help="Doctor management")
        doctor_subparsers = doctor_parser.add_subparsers(dest="subcommand", help="Subcommand")
        
        # Add doctor
        add_doctor_parser = doctor_subparsers.add_parser("add", help="Add a new doctor")
        add_doctor_parser.add_argument("--name", required=True, help="Doctor's name")
        add_doctor_parser.add_argument("--specialization", required=True, help="Doctor's specialization")
        add_doctor_parser.add_argument("--location", required=True, help="Doctor's location")
        add_doctor_parser.add_argument("--email", help="Doctor's email")
        add_doctor_parser.add_argument("--phone", help="Doctor's phone number")
        add_doctor_parser.add_argument("--website", help="Doctor's website")
        add_doctor_parser.add_argument("--insurance", nargs="*", default=[], help="Insurance providers accepted")
        add_doctor_parser.add_argument("--duration", type=int, default=30, help="Appointment duration in minutes")
        
        # List doctors
        list_doctors_parser = doctor_subparsers.add_parser("list", help="List doctors")
        list_doctors_parser.add_argument("--specialization", help="Filter by specialization")
        list_doctors_parser.add_argument("--insurance", help="Filter by insurance")
        
        # Get doctor
        get_doctor_parser = doctor_subparsers.add_parser("get", help="Get doctor details")
        get_doctor_parser.add_argument("doctor_id", help="Doctor ID")
        
        # Delete doctor
        delete_doctor_parser = doctor_subparsers.add_parser("delete", help="Delete a doctor")
        delete_doctor_parser.add_argument("doctor_id", help="Doctor ID")
        
        # Appointment commands
        appointment_parser = subparsers.add_parser("appointment", help="Appointment management")
        appointment_subparsers = appointment_parser.add_subparsers(dest="subcommand", help="Subcommand")
        
        # Schedule appointment
        schedule_parser = appointment_subparsers.add_parser("schedule", help="Schedule an appointment")
        schedule_parser.add_argument("doctor_id", help="Doctor ID")
        schedule_parser.add_argument("--date", required=True, help="Date (YYYY-MM-DD)")
        schedule_parser.add_argument("--time", required=True, help="Time (HH:MM)")
        schedule_parser.add_argument("--duration", type=int, help="Duration in minutes")
        schedule_parser.add_argument("--notes", help="Appointment notes")
        
        # List appointments
        list_appointments_parser = appointment_subparsers.add_parser("list", help="List appointments")
        list_appointments_parser.add_argument("--upcoming", action="store_true", help="Show only upcoming appointments")
        
        # Cancel appointment
        cancel_parser = appointment_subparsers.add_parser("cancel", help="Cancel an appointment")
        cancel_parser.add_argument("appointment_id", help="Appointment ID")
        
        # Send appointment request
        request_parser = appointment_subparsers.add_parser("request", help="Send an appointment request")
        request_parser.add_argument("appointment_id", help="Appointment ID")
        request_parser.add_argument("--method", choices=["email", "sms", "call"], default="email", 
                                 help="Contact method")
        
        # Calendar commands
        calendar_parser = subparsers.add_parser("calendar", help="Calendar operations")
        calendar_subparsers = calendar_parser.add_subparsers(dest="subcommand", help="Subcommand")
        
        # Find available slots
        slots_parser = calendar_subparsers.add_parser("slots", help="Find available time slots")
        slots_parser.add_argument("--days", type=int, default=7, help="Number of days to look ahead")
        slots_parser.add_argument("--start-hour", type=int, default=9, help="Start hour of the day (24h format)")
        slots_parser.add_argument("--end-hour", type=int, default=17, help="End hour of the day (24h format)")
        slots_parser.add_argument("--duration", type=int, default=30, help="Appointment duration in minutes")
    
    def run(self, args=None):
        """Run the CLI with the given arguments"""
        args = self.parser.parse_args(args)
        
        if not args.command:
            self.parser.print_help()
            return
        
        # Handle doctor commands
        if args.command == "doctor":
            self.handle_doctor_command(args)
        
        # Handle appointment commands
        elif args.command == "appointment":
            self.handle_appointment_command(args)
        
        # Handle calendar commands
        elif args.command == "calendar":
            self.handle_calendar_command(args)
    
    def handle_doctor_command(self, args):
        """Handle doctor-related commands"""
        if not args.subcommand:
            print("Error: Please specify a subcommand for doctor")
            return
        
        if args.subcommand == "add":
            doctor = Doctor(
                name=args.name,
                specialization=args.specialization,
                location=args.location,
                email=args.email,
                phone=args.phone,
                website=args.website,
                accepted_insurance=args.insurance,
                appointment_duration=args.duration
            )
            created_doctor = self.doctor_service.create_doctor(doctor)
            print(f"Doctor added with ID: {created_doctor.id}")
        
        elif args.subcommand == "list":
            if args.specialization:
                doctors = self.doctor_service.filter_doctors_by_specialization(args.specialization)
            elif args.insurance:
                doctors = self.doctor_service.filter_doctors_by_insurance(args.insurance)
            else:
                doctors = self.doctor_service.list_doctors()
            
            if not doctors:
                print("No doctors found")
                return
            
            print(f"Found {len(doctors)} doctors:")
            for doctor in doctors:
                insurances = ", ".join(doctor.accepted_insurance) if doctor.accepted_insurance else "None"
                print(f"ID: {doctor.id}")
                print(f"Name: {doctor.name}")
                print(f"Specialization: {doctor.specialization}")
                print(f"Location: {doctor.location}")
                print(f"Insurance: {insurances}")
                print("----------")
        
        elif args.subcommand == "get":
            doctor = self.doctor_service.get_doctor(args.doctor_id)
            if not doctor:
                print(f"Doctor not found with ID: {args.doctor_id}")
                return
            
            print(f"Doctor ID: {doctor.id}")
            print(f"Name: {doctor.name}")
            print(f"Specialization: {doctor.specialization}")
            print(f"Location: {doctor.location}")
            print(f"Email: {doctor.email or 'Not provided'}")
            print(f"Phone: {doctor.phone or 'Not provided'}")
            print(f"Website: {doctor.website or 'Not provided'}")
            print(f"Appointment Duration: {doctor.appointment_duration} minutes")
            print(f"Insurance Accepted: {', '.join(doctor.accepted_insurance) if doctor.accepted_insurance else 'None'}")
        
        elif args.subcommand == "delete":
            success = self.doctor_service.delete_doctor(args.doctor_id)
            if success:
                print(f"Doctor deleted with ID: {args.doctor_id}")
            else:
                print(f"Doctor not found with ID: {args.doctor_id}")
    
    def handle_appointment_command(self, args):
        """Handle appointment-related commands"""
        if not args.subcommand:
            print("Error: Please specify a subcommand for appointment")
            return
        
        if args.subcommand == "schedule":
            doctor = self.doctor_service.get_doctor(args.doctor_id)
            if not doctor:
                print(f"Doctor not found with ID: {args.doctor_id}")
                return
            
            try:
                date_parts = args.date.split("-")
                time_parts = args.time.split(":")
                start_time = datetime(
                    int(date_parts[0]), int(date_parts[1]), int(date_parts[2]),
                    int(time_parts[0]), int(time_parts[1])
                )
                
                duration = args.duration or doctor.appointment_duration
                end_time = start_time + timedelta(minutes=duration)
                
                appointment = Appointment(
                    doctor_id=args.doctor_id,
                    start_time=start_time,
                    end_time=end_time,
                    notes=args.notes
                )
                
                created_appointment = self.appointment_service.create_appointment(appointment)
                
                if created_appointment:
                    print(f"Appointment scheduled with ID: {created_appointment.id}")
                    print(f"Date: {created_appointment.start_time.strftime('%Y-%m-%d')}")
                    print(f"Time: {created_appointment.start_time.strftime('%H:%M')} - {created_appointment.end_time.strftime('%H:%M')}")
                    print(f"Doctor: {doctor.name} ({doctor.specialization})")
                else:
                    print("Failed to schedule appointment. The time slot might not be available.")
            
            except ValueError as e:
                print(f"Error: {e}")
                print("Please use the format YYYY-MM-DD for date and HH:MM for time.")
        
        elif args.subcommand == "list":
            if args.upcoming:
                appointments = self.appointment_service.get_upcoming_appointments()
            else:
                appointments = self.appointment_service.list_appointments()
            
            if not appointments:
                print("No appointments found")
                return
            
            print(f"Found {len(appointments)} appointments:")
            for appointment in appointments:
                doctor = self.doctor_service.get_doctor(appointment.doctor_id)
                doctor_name = doctor.name if doctor else "Unknown Doctor"
                
                print(f"ID: {appointment.id}")
                print(f"Doctor: {doctor_name}")
                print(f"Date: {appointment.start_time.strftime('%Y-%m-%d')}")
                print(f"Time: {appointment.start_time.strftime('%H:%M')} - {appointment.end_time.strftime('%H:%M')}")
                print(f"Status: {appointment.status}")
                print(f"Confirmed: {'Yes' if appointment.is_confirmed else 'No'}")
                if appointment.notes:
                    print(f"Notes: {appointment.notes}")
                print("----------")
        
        elif args.subcommand == "cancel":
            success = self.appointment_service.cancel_appointment(args.appointment_id)
            if success:
                print(f"Appointment cancelled with ID: {args.appointment_id}")
            else:
                print(f"Appointment not found with ID: {args.appointment_id}")
        
        elif args.subcommand == "request":
            success = self.appointment_service.send_appointment_request(args.appointment_id, args.method)
            if success:
                print(f"Appointment request sent for ID: {args.appointment_id} via {args.method}")
            else:
                print(f"Failed to send appointment request. Please check the appointment ID.")
    
    def handle_calendar_command(self, args):
        """Handle calendar-related commands"""
        if not args.subcommand:
            print("Error: Please specify a subcommand for calendar")
            return
        
        if args.subcommand == "slots":
            start_date = datetime.now()
            slots = self.calendar_service.find_available_slots(
                start_date,
                days=args.days,
                start_hour=args.start_hour,
                end_hour=args.end_hour,
                duration_minutes=args.duration
            )
            
            if not slots:
                print("No available slots found in the specified time range")
                return
            
            print(f"Found {len(slots)} available slots:")
            for i, slot in enumerate(slots, 1):
                start = slot['start']
                end = slot['end']
                print(f"{i}. {start.strftime('%A, %B %d, %Y %H:%M')} - {end.strftime('%H:%M')}")

def main():
    cli = CLI()
    cli.run()

if __name__ == "__main__":
    main()