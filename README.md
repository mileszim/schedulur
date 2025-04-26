# Schedulur

A personal medical appointment scheduling system that helps you find and book appointments with doctors based on your insurance, availability, and their specialization.

## Features

- Store and manage doctor information, including specialization and accepted insurance
- Integration with your personal calendar to find available time slots
- Automated appointment requests via email, SMS, or phone calls
- Command-line interface for easy interaction
- Save all data locally for privacy

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/schedulur.git
cd schedulur

# Install dependencies and the package in development mode
pip install -e .
```

## Usage

### Adding a doctor

```bash
schedulur doctor add --name "Dr. Alice Smith" --specialization "Cardiologist" \
    --location "123 Medical Center, New York" --phone "555-123-4567" \
    --email "alice@hospital.com" --insurance "BlueCross" "Medicare"
```

### Viewing your doctors

```bash
# List all doctors
schedulur doctor list

# Filter by specialization
schedulur doctor list --specialization "Dermatologist"

# Filter by insurance
schedulur doctor list --insurance "Medicare"
```

### Scheduling an appointment

```bash
# Check your available time slots first
schedulur calendar slots --days 14

# Schedule an appointment with a doctor
schedulur appointment schedule <doctor_id> --date 2025-05-01 --time 10:30 --notes "Annual checkup"
```

### Sending an appointment request

```bash
# Send an email request to the doctor
schedulur appointment request <appointment_id> --method email

# Or make a phone call
schedulur appointment request <appointment_id> --method call
```

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

To send emails, SMS, or make calls:

### Email

Set these environment variables:
```bash
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT=587
export SMTP_USERNAME="your_email@gmail.com"
export SMTP_PASSWORD="your_app_password"
```

### Twilio (for SMS and Calls)

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
