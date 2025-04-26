# Schedulur

A personal medical appointment scheduling system that helps you find and book appointments with doctors based on your insurance, availability, and their specialization.

## Features

- Connect to your personal calendar (Google Calendar, Outlook, or mock for testing)
- Set your availability for medical appointments
- Search for doctors based on specialty, insurance, location, and urgency
- Get a list of matching doctors with their availability
- Approve doctors you want to schedule with
- Automated appointment booking via simulated phone calls
- Store call transcripts for reference
- Add confirmed appointments to your calendar
- Command-line interface for easy interaction
- All data stored locally for privacy

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/schedulur.git
cd schedulur

# Install dependencies and the package in development mode
pip install -e .
```

## User Flow

Schedulur follows this appointment booking workflow:

1. **Connect to calendar** - Link to your Google Calendar or Outlook
2. **Specify availability** - Set your preferred appointment days and times
3. **Search for doctors** - Find doctors based on specialty, insurance, etc.
4. **Approve doctors** - Select which doctors to contact
5. **Schedule appointment** - Make automated calls to book appointments
6. **View confirmed appointment** - See appointment details with call transcript
7. **Add to calendar** - Appointment is added to your calendar

## Usage

### Setting up your profile

```bash
# Create a user profile
schedulur user create --name "Your Name" --email "your.email@example.com" --phone "555-123-4567" --zip "94102" --insurance "Blue Cross"

# Show your profile
schedulur user show

# Set your availability (0=Monday, 6=Sunday)
schedulur user availability --day 1 --start "09:00" --end "12:00"
schedulur user availability --day 3 --start "14:00" --end "17:00"
```

### Connecting to calendar

```bash
# Connect to your calendar
schedulur calendar connect --provider google

# View your available slots
schedulur calendar slots --days 14
```

### Searching for doctors

```bash
# Search by criteria
schedulur search doctor --specialization "Cardiology" --insurance "Blue Cross" --zip "94102" --distance 25 --urgency 3

# Or use natural language search
schedulur search query "I need a heart doctor who accepts Blue Cross within 10 miles of 94102, it's somewhat urgent"
```

### Managing appointments

```bash
# Approve a doctor to call
schedulur appointment approve <doctor_id>

# Schedule appointments with approved doctors
schedulur appointment schedule --reason "Annual heart checkup"

# List your appointments
schedulur appointment list

# View appointment details with call transcript
schedulur appointment show <appointment_id>

# Cancel an appointment
schedulur appointment cancel <appointment_id>
```

## Demo

A demo script is included to showcase the workflow:

```bash
python -m schedulur.cli_demo
```

This script will:
1. Create a sample user profile
2. Set availability
3. Connect to a mock calendar
4. Search for doctors
5. Approve a doctor
6. Schedule an appointment
7. Show the appointment details with call transcript

## Calendar Integration

To integrate with Google Calendar or Outlook, you need to set up credentials:

### Google Calendar

1. Visit the Google Cloud Console and create a project
2. Enable the Google Calendar API
3. Create OAuth credentials and download the JSON file
4. Set the environment variable:
   ```bash
   export GOOGLE_CREDENTIALS_PATH="/path/to/credentials.json"
   ```

### Outlook Calendar

1. Register an application in the Microsoft Azure portal
2. Create OAuth credentials and save them
3. Set the environment variable:
   ```bash
   export OUTLOOK_CREDENTIALS_PATH="/path/to/outlook_credentials.json"
   ```

## Communication Integration

For making calls to doctors' offices:

### Twilio (for Voice Calls)

Sign up for Twilio and set these environment variables:
```bash
export TWILIO_ACCOUNT_SID="your_account_sid"
export TWILIO_AUTH_TOKEN="your_auth_token"
export TWILIO_PHONE_NUMBER="your_twilio_phone_number"
```

## Contributing

To contribute to this project:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

### Development Setup

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
python -m unittest discover tests
```

## License

MIT