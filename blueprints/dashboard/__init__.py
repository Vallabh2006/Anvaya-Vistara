
from flask import Blueprint, render_template
from utils.permissions import role_required

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/patient')
@role_required('patient')
def patient_dashboard():
    return render_template('dashboard/patient.html')

@dashboard_bp.route('/doctor')
@role_required('doctor')
def doctor_dashboard():
    return render_template('dashboard/doctor.html')

@dashboard_bp.route('/staff')
@role_required('nurse', 'helper', 'ambulance_op', 'care_taker', 'therapist', 'pharmacist', 'lab_technician', 'receptionist')
def staff_dashboard():
    return render_template('dashboard/staff.html')

@dashboard_bp.route('/phc')
def phc_dashboard():
    return render_template('dashboard/phc.html')
