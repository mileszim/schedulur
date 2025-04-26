import os
import uuid
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from schedulur.models.user import User, UserAvailability
from schedulur.models.doctor import Doctor
from schedulur.services.user_service import UserService
from schedulur.services.doctor_service import DoctorService
from schedulur.services.doctor_search_service import DoctorSearchService
from schedulur.services.appointment_service import AppointmentService
from schedulur.integrations.calendar import CalendarService

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-for-schedulur')
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Initialize services
user_service = UserService()
doctor_service = DoctorService()
doctor_search_service = DoctorSearchService()
appointment_service = AppointmentService()

# Ensure data directory exists
os.makedirs(os.path.join(os.path.dirname(__file__), "data"), exist_ok=True)

# Routes
@app.route('/')
def index():
    """Home page"""
    # Check if user is logged in
    user_id = session.get('user_id')
    user = None
    if user_id:
        user = user_service.get_user(user_id)
    
    return render_template('index.html', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login/registration page"""
    if request.method == 'POST':
        form_type = request.form.get('form_type', '')
        email = request.form['email']
        
        # Look for existing user by email
        users = user_service.list_users()
        existing_user = next((u for u in users if u.email == email), None)
        
        if form_type == 'login':
            # Login flow
            if existing_user:
                # Use existing user
                user = existing_user
                flash(f"Welcome back, {user.name}!", "success")
                session['user_id'] = user.id
                return redirect(url_for('profile'))
            else:
                # User not found
                flash("Email not found. Please register first.", "warning")
                return render_template('login.html')
                
        elif form_type == 'register':
            # Registration flow
            if existing_user:
                # User already exists
                flash("An account with this email already exists. Please login instead.", "warning")
                return render_template('login.html')
            else:
                # Create new user
                name = request.form['name']
                user = User(
                    id=str(uuid.uuid4()),
                    name=name,
                    email=email,
                    phone=request.form.get('phone', ''),
                    zip_code=request.form.get('zip_code', ''),
                    insurance_provider=request.form.get('insurance', ''),
                    calendar_provider='mock'  # Default to mock calendar
                )
                user = user_service.create_user(user)
                flash(f"Account created successfully for {user.name}!", "success")
                session['user_id'] = user.id
                return redirect(url_for('profile'))
        else:
            # Invalid form type
            flash("Invalid form submission.", "danger")
            return render_template('login.html')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Log out user"""
    session.pop('user_id', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    """User profile page"""
    # Check if user is logged in
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in first.", "warning")
        return redirect(url_for('login'))
    
    user = user_service.get_user(user_id)
    
    if request.method == 'POST':
        # Update user profile
        user.name = request.form['name']
        user.email = request.form['email']
        user.phone = request.form['phone']
        user.zip_code = request.form['zip_code']
        user.insurance_provider = request.form['insurance']
        
        # Update user
        user = user_service.update_user(user_id, user)
        flash("Profile updated successfully!", "success")
    
    return render_template('profile.html', user=user)

@app.route('/calendar-connect', methods=['GET', 'POST'])
def calendar_connect():
    """Connect to calendar"""
    # Check if user is logged in
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in first.", "warning")
        return redirect(url_for('login'))
    
    user = user_service.get_user(user_id)
    
    if request.method == 'POST':
        # Update calendar provider
        provider = request.form['provider']
        user.calendar_provider = provider
        user = user_service.update_user(user_id, user)
        
        flash(f"Connected to {provider.title()} Calendar successfully!", "success")
        return redirect(url_for('availability'))
    
    return render_template('calendar_connect.html', user=user)

@app.route('/availability', methods=['GET', 'POST'])
def availability():
    """Set user availability"""
    # Check if user is logged in
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in first.", "warning")
        return redirect(url_for('login'))
    
    user = user_service.get_user(user_id)
    
    if request.method == 'POST':
        # Initialize availability if not set
        if not user.availability:
            user.availability = UserAvailability()
        
        # Clear existing availability
        user.availability.time_slots = []
        
        # Process form data
        for day in range(7):  # 0-6 for Monday to Sunday
            if f'day_{day}' in request.form:
                start = request.form.get(f'start_{day}', '09:00')
                end = request.form.get(f'end_{day}', '17:00')
                
                # Add time slot
                user.availability.time_slots.append({
                    'day': day,
                    'start': start,
                    'end': end
                })
        
        # Update user
        user = user_service.update_user(user_id, user)
        flash("Availability updated successfully!", "success")
        
        return redirect(url_for('calendar_slots'))
    
    # Initialize form values for template
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_values = {}
    
    if user.availability and user.availability.time_slots:
        for slot in user.availability.time_slots:
            day = slot.get('day', 0)
            day_values[day] = {
                'enabled': True,
                'start': slot.get('start', '09:00'),
                'end': slot.get('end', '17:00')
            }
    
    return render_template('availability.html', user=user, day_names=day_names, day_values=day_values)

@app.route('/calendar-slots')
def calendar_slots():
    """View available calendar slots"""
    # Check if user is logged in
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in first.", "warning")
        return redirect(url_for('login'))
    
    user = user_service.get_user(user_id)
    
    # Get calendar service
    calendar_service = CalendarService(provider_type=user.calendar_provider, user_id=user_id)
    
    # Get availability from user profile
    time_preferences = None
    if user.availability and user.availability.time_slots:
        time_preferences = user.availability.time_slots
    
    # Find available slots
    days = request.args.get('days', 7, type=int)
    slots = calendar_service.find_available_slots(
        start_date=datetime.now(),
        days=days,
        time_preferences=time_preferences
    )
    
    # Group slots by date
    dates = {}
    for slot in slots:
        date_str = slot['start'].strftime('%Y-%m-%d')
        if date_str not in dates:
            dates[date_str] = []
        
        time_str = f"{slot['start'].strftime('%H:%M')} - {slot['end'].strftime('%H:%M')}"
        dates[date_str].append({
            'start': slot['start'],
            'end': slot['end'],
            'time_str': time_str
        })
    
    return render_template('calendar_slots.html', user=user, dates=dates, days=days)

@app.route('/search', methods=['GET', 'POST'])
def search():
    """Search for doctors"""
    # Check if user is logged in
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in first.", "warning")
        return redirect(url_for('login'))
    
    user = user_service.get_user(user_id)
    doctors = []
    
    if request.method == 'POST':
        search_type = request.form['search_type']
        
        if search_type == 'criteria':
            # Search by criteria
            specialization = request.form['specialization']
            insurance = request.form.get('insurance') or user.insurance_provider
            zip_code = request.form.get('zip_code') or user.zip_code
            distance = int(request.form.get('distance', 25))
            urgency = int(request.form.get('urgency', 1))
            
            doctors = doctor_search_service.search_doctors(
                specialization=specialization,
                insurance=insurance,
                zip_code=zip_code,
                max_distance=distance,
                urgency_level=urgency
            )
        
        elif search_type == 'query':
            # Search by natural language query
            query = request.form['query']
            doctors = doctor_search_service.search_with_claude(query)
    
    return render_template('search.html', user=user, doctors=doctors)

@app.route('/doctor/approve/<doctor_id>')
def approve_doctor(doctor_id):
    """Approve a doctor for scheduling"""
    # Check if user is logged in
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in first.", "warning")
        return redirect(url_for('login'))
    
    success = appointment_service.approve_doctor_for_scheduling(doctor_id, True)
    
    if success:
        doctor = doctor_service.get_doctor(doctor_id)
        flash(f"You approved {doctor.name} for scheduling.", "success")
    else:
        flash("Doctor not found.", "danger")
    
    return redirect(url_for('search'))

@app.route('/doctor/reject/<doctor_id>')
def reject_doctor(doctor_id):
    """Reject a doctor for scheduling"""
    # Check if user is logged in
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in first.", "warning")
        return redirect(url_for('login'))
    
    success = appointment_service.approve_doctor_for_scheduling(doctor_id, False)
    
    if success:
        doctor = doctor_service.get_doctor(doctor_id)
        flash(f"You rejected {doctor.name} for scheduling.", "warning")
    else:
        flash("Doctor not found.", "danger")
    
    return redirect(url_for('search'))

@app.route('/approved-doctors')
def approved_doctors():
    """View approved doctors"""
    # Check if user is logged in
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in first.", "warning")
        return redirect(url_for('login'))
    
    user = user_service.get_user(user_id)
    doctors = doctor_service.get_approved_doctors()
    
    return render_template('approved_doctors.html', user=user, doctors=doctors)

@app.route('/schedule', methods=['GET', 'POST'])
def schedule():
    """Schedule appointments with approved doctors"""
    # Check if user is logged in
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in first.", "warning")
        return redirect(url_for('login'))
    
    user = user_service.get_user(user_id)
    appointment = None
    call_details = None
    
    if request.method == 'POST':
        # Get reason for appointment
        reason = request.form['reason']
        
        # Get approved doctors
        approved_doctors = doctor_service.get_approved_doctors()
        
        if not approved_doctors:
            flash("No approved doctors found. Please approve some doctors first.", "warning")
            return redirect(url_for('search'))
        
        # Try to schedule with first approved doctor
        doctor = approved_doctors[0]
        
        flash(f"Calling {doctor.name} to schedule your appointment...", "info")
        
        # Schedule appointment
        appointment, call_details = appointment_service.schedule_with_doctor(
            doctor=doctor,
            user=user,
            reason=reason
        )
        
        if appointment:
            flash(f"Success! Your appointment with {doctor.name} has been scheduled.", "success")
        else:
            flash(f"Failed to schedule appointment with {doctor.name}", "danger")
    
    return render_template('schedule.html', user=user, appointment=appointment, call_details=call_details)

@app.route('/appointments')
def appointments():
    """View appointments"""
    # Check if user is logged in
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in first.", "warning")
        return redirect(url_for('login'))
    
    user = user_service.get_user(user_id)
    
    # Get user appointments
    user_appointments = appointment_service.get_user_appointments(user_id)
    
    # Get doctor information for each appointment
    appointments_with_doctors = []
    for appointment in user_appointments:
        doctor = doctor_service.get_doctor(appointment.doctor_id)
        appointments_with_doctors.append({
            'appointment': appointment,
            'doctor': doctor
        })
    
    return render_template('appointments.html', user=user, appointments=appointments_with_doctors)

@app.route('/appointment/<appointment_id>')
def view_appointment(appointment_id):
    """View appointment details"""
    # Check if user is logged in
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in first.", "warning")
        return redirect(url_for('login'))
    
    user = user_service.get_user(user_id)
    
    # Get appointment
    appointment = appointment_service.get_appointment(appointment_id)
    if not appointment:
        flash("Appointment not found.", "danger")
        return redirect(url_for('appointments'))
    
    # Get doctor
    doctor = doctor_service.get_doctor(appointment.doctor_id)
    
    return render_template('appointment_detail.html', user=user, appointment=appointment, doctor=doctor)

@app.route('/appointment/cancel/<appointment_id>')
def cancel_appointment(appointment_id):
    """Cancel an appointment"""
    # Check if user is logged in
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in first.", "warning")
        return redirect(url_for('login'))
    
    # Cancel appointment
    success = appointment_service.cancel_appointment(appointment_id)
    
    if success:
        flash("Appointment cancelled successfully.", "success")
    else:
        flash("Failed to cancel appointment.", "danger")
    
    return redirect(url_for('appointments'))

if __name__ == '__main__':
    app.run(debug=True)