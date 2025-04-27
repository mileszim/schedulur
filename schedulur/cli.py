#!/usr/bin/env python

import argparse
import sys
import uuid
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json

from schedulur.models.doctor import Doctor
from schedulur.models.appointment import Appointment, AppointmentStatus
from schedulur.models.user import User, UserAvailability
from schedulur.services.doctor_service import DoctorService
from schedulur.services.doctor_search_service import DoctorSearchService
from schedulur.services.appointment_service import AppointmentService
from schedulur.services.user_service import UserService
from schedulur.integrations.calendar import CalendarService
from schedulur.integrations.communication import CommunicationService


class CLI:
    """Command-line interface for Schedulur"""

    def __init__(self):
        self.user_service = UserService()
        self.doctor_service = DoctorService()
        self.doctor_search_service = DoctorSearchService()
        self.appointment_service = AppointmentService()
        self.calendar_service = CalendarService()
        self.communication_service = CommunicationService()

        self.current_user = None
        self._load_current_user()

        self.parser = argparse.ArgumentParser(
            description="Schedulur - Medical Appointment Scheduler")
        self.setup_parsers()

    def _load_current_user(self):
        """Load the current user from config file"""
        config_file = os.path.join(
            os.path.dirname(__file__), "data/config.json")
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    if 'current_user_id' in config:
                        self.current_user = self.user_service.get_user(
                            config['current_user_id'])
        except Exception as e:
            print(f"Error loading user config: {e}")

    def _save_current_user(self, user_id: str):
        """Save the current user to config file"""
        config_file = os.path.join(
            os.path.dirname(__file__), "data/config.json")
        try:
            os.makedirs(os.path.dirname(config_file), exist_ok=True)

            config = {'current_user_id': user_id}
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving user config: {e}")

    def setup_parsers(self):
        """Set up command-line argument parsers"""
        subparsers = self.parser.add_subparsers(dest="command", help="Command")

        # User commands
        user_parser = subparsers.add_parser("user", help="User management")
        user_subparsers = user_parser.add_subparsers(
            dest="subcommand", help="Subcommand")

        # Add/create user
        add_user_parser = user_subparsers.add_parser(
            "create", help="Create a new user profile")
        add_user_parser.add_argument(
            "--name", required=True, help="User's full name")
        add_user_parser.add_argument(
            "--email", required=True, help="User's email address")
        add_user_parser.add_argument("--phone", help="User's phone number")
        add_user_parser.add_argument("--zip", help="User's ZIP code")
        add_user_parser.add_argument(
            "--insurance", help="User's insurance provider")
        add_user_parser.add_argument(
            "--insurance-id", help="User's insurance ID")
        add_user_parser.add_argument("--calendar", choices=["google", "outlook", "mock"], default="mock",
                                     help="Calendar provider to use")

        # Show current user
        user_subparsers.add_parser("show", help="Show current user profile")

        # Set current user
        set_user_parser = user_subparsers.add_parser(
            "select", help="Select a user profile")
        set_user_parser.add_argument("user_id", help="User ID to select")

        # Set availability
        availability_parser = user_subparsers.add_parser(
            "availability", help="Set user availability")
        availability_parser.add_argument("--day", type=int, choices=range(7), required=True,
                                         help="Day of week (0=Monday, 6=Sunday)")
        availability_parser.add_argument(
            "--start", required=True, help="Start time (HH:MM)")
        availability_parser.add_argument(
            "--end", required=True, help="End time (HH:MM)")

        # Calendar commands
        calendar_parser = subparsers.add_parser(
            "calendar", help="Calendar operations")
        calendar_subparsers = calendar_parser.add_subparsers(
            dest="subcommand", help="Subcommand")

        # Connect calendar
        connect_parser = calendar_subparsers.add_parser(
            "connect", help="Connect to calendar")
        connect_parser.add_argument("--provider", choices=["google", "outlook", "mock"], required=True,
                                    help="Calendar provider")

        # Show calendar slots
        slots_parser = calendar_subparsers.add_parser(
            "slots", help="Show available calendar slots")
        slots_parser.add_argument(
            "--days", type=int, default=7, help="Number of days to look ahead")

        # Search commands
        search_parser = subparsers.add_parser(
            "search", help="Search for doctors")
        search_subparsers = search_parser.add_subparsers(
            dest="subcommand", help="Subcommand")

        # Search by criteria
        criteria_parser = search_subparsers.add_parser(
            "doctor", help="Search for doctors by criteria")
        criteria_parser.add_argument(
            "--specialization", required=True, help="Doctor specialization")
        criteria_parser.add_argument("--insurance", help="Insurance provider")
        criteria_parser.add_argument("--zip", help="ZIP code")
        criteria_parser.add_argument(
            "--distance", type=int, default=5, help="Max distance in miles")
        criteria_parser.add_argument("--urgency", type=int, choices=range(1, 6), default=1,
                                     help="Urgency level (1-5)")

        # Search by query
        query_parser = search_subparsers.add_parser(
            "query", help="Search for doctors using natural language")
        query_parser.add_argument(
            "query", help="Natural language search query")

        # Appointment commands
        appointment_parser = subparsers.add_parser(
            "appointment", help="Appointment management")
        appointment_subparsers = appointment_parser.add_subparsers(
            dest="subcommand", help="Subcommand")

        # Schedule appointment
        schedule_parser = appointment_subparsers.add_parser(
            "schedule", help="Schedule an appointment with approved doctors")
        schedule_parser.add_argument(
            "--reason", required=True, help="Reason for appointment")
        schedule_parser.add_argument(
            "--date", help="Preferred date (YYYY-MM-DD)")

        # Approve doctor
        approve_parser = appointment_subparsers.add_parser(
            "approve", help="Approve a doctor for scheduling")
        approve_parser.add_argument("doctor_id", help="Doctor ID to approve")

        # Reject doctor
        reject_parser = appointment_subparsers.add_parser(
            "reject", help="Reject a doctor for scheduling")
        reject_parser.add_argument("doctor_id", help="Doctor ID to reject")

        # List appointments
        list_appointments_parser = appointment_subparsers.add_parser(
            "list", help="List appointments")
        list_appointments_parser.add_argument(
            "--upcoming", action="store_true", help="Show only upcoming appointments")

        # Show appointment details
        show_parser = appointment_subparsers.add_parser(
            "show", help="Show appointment details")
        show_parser.add_argument("appointment_id", help="Appointment ID")

        # Cancel appointment
        cancel_parser = appointment_subparsers.add_parser(
            "cancel", help="Cancel an appointment")
        cancel_parser.add_argument("appointment_id", help="Appointment ID")

    def run(self, args=None):
        """Run the CLI with the given arguments"""
        args = self.parser.parse_args(args)

        if not args.command:
            self.parser.print_help()
            return

        # Handle user commands
        if args.command == "user":
            self.handle_user_command(args)

        # Handle calendar commands
        elif args.command == "calendar":
            self.handle_calendar_command(args)

        # Handle search commands
        elif args.command == "search":
            self.handle_search_command(args)

        # Handle appointment commands
        elif args.command == "appointment":
            self.handle_appointment_command(args)

    def check_current_user(self):
        """Check if there's a current user, and prompt to create one if not"""
        if not self.current_user:
            print(
                "No user profile selected. Please create or select a user profile first.")
            print(
                "Run 'schedulur user create --name \"Your Name\" --email \"your.email@example.com\"'")
            return False
        return True

    def handle_user_command(self, args):
        """Handle user-related commands"""
        if not args.subcommand:
            print("Error: Please specify a subcommand for user")
            return

        if args.subcommand == "create":
            # Create new user profile
            user = User(
                id=str(uuid.uuid4()),
                name=args.name,
                email=args.email,
                phone=args.phone,
                zip_code=args.zip,
                insurance_provider=args.insurance,
                insurance_id=args.insurance_id,
                calendar_provider=args.calendar
            )

            created_user = self.user_service.create_user(user)
            if created_user:
                print(f"User profile created with ID: {created_user.id}")

                # Set as current user
                self.current_user = created_user
                self._save_current_user(created_user.id)
                print(f"Selected {created_user.name} as the current user")

        elif args.subcommand == "show":
            # Show current user profile
            if not self.check_current_user():
                return

            print(f"Current user profile:")
            print(f"ID: {self.current_user.id}")
            print(f"Name: {self.current_user.name}")
            print(f"Email: {self.current_user.email}")
            print(f"Phone: {self.current_user.phone or 'Not provided'}")
            print(f"ZIP: {self.current_user.zip_code or 'Not provided'}")
            print(
                f"Insurance: {self.current_user.insurance_provider or 'Not provided'}")
            print(f"Calendar: {self.current_user.calendar_provider}")

            # Show availability if set
            if self.current_user.availability and self.current_user.availability.time_slots:
                print("\nAvailability:")
                day_names = ['Monday', 'Tuesday', 'Wednesday',
                             'Thursday', 'Friday', 'Saturday', 'Sunday']
                for slot in self.current_user.availability.time_slots:
                    day = slot.get('day', 0)
                    start = slot.get('start', '00:00')
                    end = slot.get('end', '00:00')
                    print(f"  {day_names[day]}: {start} - {end}")

        elif args.subcommand == "select":
            # Select a user profile
            user = self.user_service.get_user(args.user_id)
            if user:
                self.current_user = user
                self._save_current_user(user.id)
                print(f"Selected {user.name} as the current user")
            else:
                print(f"User not found with ID: {args.user_id}")

        elif args.subcommand == "availability":
            # Set user availability
            if not self.check_current_user():
                return

            # Initialize availability if not set
            if not self.current_user.availability:
                self.current_user.availability = UserAvailability()

            # Add or update time slot
            day = args.day
            start_time = args.start
            end_time = args.end

            # Remove any existing slot for this day
            if self.current_user.availability.time_slots:
                self.current_user.availability.time_slots = [
                    slot for slot in self.current_user.availability.time_slots
                    if slot.get('day') != day
                ]

            # Add the new slot
            self.current_user.availability.time_slots.append({
                'day': day,
                'start': start_time,
                'end': end_time
            })

            # Update the user
            self.user_service.update_user(
                self.current_user.id, self.current_user)

            day_name = ['Monday', 'Tuesday', 'Wednesday',
                        'Thursday', 'Friday', 'Saturday', 'Sunday'][day]
            print(
                f"Updated availability for {day_name}: {start_time} - {end_time}")

    def handle_calendar_command(self, args):
        """Handle calendar-related commands"""
        if not self.check_current_user():
            return

        if not args.subcommand:
            print("Error: Please specify a subcommand for calendar")
            return

        if args.subcommand == "connect":
            # Connect to calendar provider
            provider = args.provider

            # Update user's calendar provider
            self.current_user.calendar_provider = provider
            self.user_service.update_user(
                self.current_user.id, self.current_user)

            print(f"Connected to {provider.title()} Calendar")

            # In a real implementation, this would handle OAuth flow
            if provider == "google":
                print("In a real implementation, this would open the Google OAuth flow")
                print("For now, we're using a mock implementation")
            elif provider == "outlook":
                print(
                    "In a real implementation, this would open the Microsoft OAuth flow")
                print("For now, we're using a mock implementation")

        elif args.subcommand == "slots":
            # Show available calendar slots
            calendar_service = CalendarService(provider_type=self.current_user.calendar_provider,
                                               user_id=self.current_user.id)

            # Get availability from user profile
            time_preferences = None
            if self.current_user.availability and self.current_user.availability.time_slots:
                time_preferences = self.current_user.availability.time_slots

            # Find available slots
            slots = calendar_service.find_available_slots(
                start_date=datetime.now(),
                days=args.days,
                time_preferences=time_preferences
            )

            if not slots:
                print("No available slots found in the specified time range")
                return

            print(f"Found {len(slots)} available slots:")
            # Group by date
            dates = {}
            for slot in slots:
                date_str = slot['start'].strftime('%Y-%m-%d')
                if date_str not in dates:
                    dates[date_str] = []

                time_str = f"{slot['start'].strftime('%H:%M')} - {slot['end'].strftime('%H:%M')}"
                dates[date_str].append(time_str)

            # Print by date
            for date_str, times in sorted(dates.items()):
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                print(f"\n{date_obj.strftime('%A, %B %d, %Y')}:")
                for i, time_slot in enumerate(sorted(times), 1):
                    print(f"  {i}. {time_slot}")

    def handle_search_command(self, args):
        """Handle search-related commands"""
        if not self.check_current_user():
            return

        if not args.subcommand:
            print("Error: Please specify a subcommand for search")
            return

        if args.subcommand == "doctor":
            # Search for doctors by criteria
            zip_code = args.zip or self.current_user.zip_code
            insurance = args.insurance or self.current_user.insurance_provider

            if not zip_code:
                print(
                    "Warning: No ZIP code provided. Distance-based results may not be accurate.")

            doctors = self.doctor_search_service.search_doctors(
                specialization=args.specialization,
                insurance=insurance,
                zip_code=zip_code,
                max_distance=args.distance,
                urgency_level=args.urgency
            )

            if not doctors:
                print(f"No doctors found matching the criteria")
                return

            self.print_doctor_search_results(doctors)

        elif args.subcommand == "query":
            # Search using natural language query
            doctors = self.doctor_search_service.search_with_claude(args.query)

            if not doctors:
                print(f"No doctors found matching the query")
                return

            self.print_doctor_search_results(doctors)

    def print_doctor_search_results(self, doctors: List[Doctor]):
        """Print doctor search results in a user-friendly format"""
        print(f"\nFound {len(doctors)} doctors:")

        for i, doctor in enumerate(doctors, 1):
            approval_status = ""
            if doctor.user_approval is True:
                approval_status = " (Approved)"
            elif doctor.user_approval is False:
                approval_status = " (Rejected)"

            print(f"\n{i}. {doctor.name}{approval_status}")
            print(f"   ID: {doctor.id}")
            print(f"   Specialization: {doctor.specialization}")
            if doctor.practice_name:
                print(f"   Practice: {doctor.practice_name}")

            location = []
            if doctor.address:
                location.append(doctor.address)
            if doctor.city and doctor.state:
                location.append(f"{doctor.city}, {doctor.state}")
            if doctor.zip_code:
                location.append(doctor.zip_code)

            if location:
                print(f"   Location: {', '.join(location)}")

            if doctor.distance_miles is not None:
                print(f"   Distance: {doctor.distance_miles:.1f} miles")

            if doctor.earliest_available_slot:
                print(
                    f"   Earliest available: {doctor.earliest_available_slot}")

            if doctor.accepted_insurance:
                print(f"   Insurance: {', '.join(doctor.accepted_insurance)}")

            if doctor.phone:
                print(f"   Phone: {doctor.phone}")

            print(f"   To approve: schedulur appointment approve {doctor.id}")
            print(f"   To reject: schedulur appointment reject {doctor.id}")

    def handle_appointment_command(self, args):
        """Handle appointment-related commands"""
        if not self.check_current_user():
            return

        if not args.subcommand:
            print("Error: Please specify a subcommand for appointment")
            return

        if args.subcommand == "schedule":
            # Schedule appointments with approved doctors
            approved_doctors = self.doctor_service.get_approved_doctors()

            if not approved_doctors:
                print(
                    "No approved doctors found. Please search for doctors and approve them first.")
                return

            # Parse preferred date if provided
            preferred_date = None
            if args.date:
                try:
                    date_parts = args.date.split("-")
                    preferred_date = datetime(int(date_parts[0]), int(
                        date_parts[1]), int(date_parts[2]), 9, 0)
                except (ValueError, IndexError):
                    print("Invalid date format. Please use YYYY-MM-DD.")
                    return

            print(
                f"Scheduling appointments with {len(approved_doctors)} approved doctors...")

            # Schedule with each approved doctor
            for doctor in approved_doctors:
                print(f"\nCalling {doctor.name} ({doctor.specialization})...")

                appointment, call_details = self.appointment_service.schedule_with_doctor(
                    doctor=doctor,
                    user=self.current_user,
                    reason=args.reason,
                    preferred_date=preferred_date
                )

                if appointment:
                    print(
                        f"Success! Appointment scheduled for {appointment.start_time.strftime('%A, %B %d at %I:%M %p')}")
                    print(
                        f"Location: {doctor.address}, {doctor.city}, {doctor.state} {doctor.zip_code}")
                    print(f"Appointment ID: {appointment.id}")
                    print(
                        f"Added to your {self.current_user.calendar_provider} calendar")
                    print("\nCall transcript excerpt:")

                    # Show abbreviated transcript
                    if call_details.get('transcript'):
                        lines = call_details['transcript'].strip().split('\n')
                        filtered_lines = [
                            line for line in lines if line.strip()]
                        important_lines = filtered_lines[:3] + \
                            ["..."] + filtered_lines[-3:]
                        for line in important_lines:
                            print(f"  {line}")

                    print(
                        f"\nTo view full details: schedulur appointment show {appointment.id}")

                    # Once we've scheduled one appointment, we're done
                    doctor.has_been_called = True
                    self.doctor_service.update_doctor(doctor.id, doctor)
                    break
                else:
                    print(f"Failed to schedule appointment with {doctor.name}")
                    if 'error' in call_details:
                        print(f"Error: {call_details['error']}")

            # If we reached here without breaking, no appointments were scheduled
            if not appointment:
                print("\nCouldn't schedule appointments with any approved doctors.")
                print("Please try approving more doctors or try again later.")

        elif args.subcommand == "approve":
            # Approve a doctor for scheduling
            success = self.appointment_service.approve_doctor_for_scheduling(
                args.doctor_id, True)
            if success:
                doctor = self.doctor_service.get_doctor(args.doctor_id)
                print(f"Approved {doctor.name} for scheduling")
            else:
                print(f"Doctor not found with ID: {args.doctor_id}")

        elif args.subcommand == "reject":
            # Reject a doctor for scheduling
            success = self.appointment_service.approve_doctor_for_scheduling(
                args.doctor_id, False)
            if success:
                doctor = self.doctor_service.get_doctor(args.doctor_id)
                print(f"Rejected {doctor.name} for scheduling")
            else:
                print(f"Doctor not found with ID: {args.doctor_id}")

        elif args.subcommand == "list":
            # List appointments
            if args.upcoming:
                appointments = self.appointment_service.get_upcoming_appointments()
            else:
                appointments = self.appointment_service.get_user_appointments(
                    self.current_user.id)

            if not appointments:
                print("No appointments found")
                return

            print(f"Found {len(appointments)} appointments:")
            for appointment in appointments:
                doctor = self.doctor_service.get_doctor(appointment.doctor_id)
                doctor_name = doctor.name if doctor else "Unknown Doctor"

                status_emoji = "✓" if appointment.status == AppointmentStatus.SCHEDULED else "🕒"

                print(f"\n{status_emoji} Appointment with {doctor_name}")
                print(f"   ID: {appointment.id}")
                print(
                    f"   When: {appointment.start_time.strftime('%A, %B %d at %I:%M %p')}")
                print(f"   Status: {appointment.status}")
                if appointment.reason:
                    print(f"   Reason: {appointment.reason}")

        elif args.subcommand == "show":
            # Show appointment details
            appointment = self.appointment_service.get_appointment(
                args.appointment_id)
            if not appointment:
                print(f"Appointment not found with ID: {args.appointment_id}")
                return

            doctor = self.doctor_service.get_doctor(appointment.doctor_id)
            doctor_name = doctor.name if doctor else "Unknown Doctor"

            print(f"\nAppointment Details:")
            print(f"ID: {appointment.id}")
            print(f"Doctor: {doctor_name}")
            if doctor:
                print(f"Specialization: {doctor.specialization}")
                if doctor.practice_name:
                    print(f"Practice: {doctor.practice_name}")
                if doctor.address:
                    print(f"Address: {doctor.address}")
                    if doctor.city and doctor.state and doctor.zip_code:
                        print(
                            f"         {doctor.city}, {doctor.state} {doctor.zip_code}")
                if doctor.phone:
                    print(f"Phone: {doctor.phone}")

            print(
                f"\nDate: {appointment.start_time.strftime('%A, %B %d, %Y')}")
            print(
                f"Time: {appointment.start_time.strftime('%I:%M %p')} - {appointment.end_time.strftime('%I:%M %p')}")
            print(f"Status: {appointment.status}")

            if appointment.reason:
                print(f"\nReason: {appointment.reason}")
            if appointment.notes:
                print(f"Notes: {appointment.notes}")

            if appointment.call_transcript:
                print(f"\nCall Transcript:")
                print("=" * 50)
                print(appointment.call_transcript)
                print("=" * 50)

            print(
                f"\nTo cancel this appointment: schedulur appointment cancel {appointment.id}")

        elif args.subcommand == "cancel":
            # Cancel an appointment
            success = self.appointment_service.cancel_appointment(
                args.appointment_id)
            if success:
                print(f"Appointment cancelled with ID: {args.appointment_id}")
                print("The appointment has been removed from your calendar")
            else:
                print(f"Appointment not found with ID: {args.appointment_id}")


def main():
    cli = CLI()
    cli.run()


if __name__ == "__main__":
    main()
