#!/usr/bin/env python

"""
Schedulur Demo Script

This script demonstrates the appointment scheduling workflow with CLI commands.
"""

import os
import sys
import subprocess
import time
from datetime import datetime, timedelta

def print_header(text):
    """Print section header"""
    width = len(text) + 4
    print("\n" + "=" * width)
    print(f"  {text}")
    print("=" * width)

def run_command(command):
    """Run a CLI command and print the output"""
    print(f"\n$ {command}")
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    print(result.stdout)
    if result.stderr:
        print(f"Error: {result.stderr}")
    return result

def demo():
    # Ensure data directory exists
    os.makedirs("schedulur/data", exist_ok=True)
    
    # 1. Create user
    print_header("1. Creating a user profile")
    run_command("python -m schedulur.cli user create --name 'John Doe' --email 'john@example.com' --phone '555-123-4567' --zip '94102' --insurance 'Blue Cross' --calendar 'mock'")
    
    # 2. Set availability
    print_header("2. Setting user availability")
    run_command("python -m schedulur.cli user availability --day 1 --start '09:00' --end '12:00'")
    run_command("python -m schedulur.cli user availability --day 3 --start '14:00' --end '17:00'")
    
    # 3. Connect to calendar
    print_header("3. Connecting to calendar")
    run_command("python -m schedulur.cli calendar connect --provider mock")
    
    # 4. Check available slots
    print_header("4. Checking available slots")
    run_command("python -m schedulur.cli calendar slots --days 7")
    
    # 5. Search for doctors
    print_header("5. Searching for doctors")
    run_command("python -m schedulur.cli search doctor --specialization 'Cardiology' --urgency 3")
    
    # 6. Approve doctors
    print_header("6. Approving doctors for scheduling")
    # Extract doctor ID from previous output and approve (this is a mock for demo)
    run_command("python -m schedulur.cli search doctor --specialization 'Cardiology' --urgency 3 | grep ID | head -n1 | awk '{print $2}' > doctor_id.txt")
    with open("doctor_id.txt", "r") as f:
        doctor_id = f.read().strip()
    run_command(f"python -m schedulur.cli appointment approve {doctor_id}")
    
    # 7. Schedule appointment
    print_header("7. Scheduling appointment")
    run_command("python -m schedulur.cli appointment schedule --reason 'Heart checkup'")
    
    # 8. View the appointment
    print_header("8. Viewing appointment details")
    run_command("python -m schedulur.cli appointment list")
    
    # Extract appointment ID from previous output and view details
    run_command("python -m schedulur.cli appointment list | grep ID | head -n1 | awk '{print $2}' > appointment_id.txt")
    with open("appointment_id.txt", "r") as f:
        appointment_id = f.read().strip()
    
    run_command(f"python -m schedulur.cli appointment show {appointment_id}")
    
    # Clean up temp files
    os.remove("doctor_id.txt")
    os.remove("appointment_id.txt")
    
    print_header("Demo completed!")
    print("\nYou can now try the following commands:")
    print("- python -m schedulur.cli user show")
    print("- python -m schedulur.cli search query 'I need a heart doctor who takes Blue Cross'")
    print("- python -m schedulur.cli appointment list")
    print("- python -m schedulur.cli calendar slots")

if __name__ == "__main__":
    demo()