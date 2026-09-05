import json
from datetime import datetime, date
from flask import Blueprint, render_template, redirect, url_for, abort, request, flash
from utils.auth_helpers import login_required, get_current_user
from utils.db import query_db, execute_db

patient_bp = Blueprint('patient', __name__, url_prefix='/patient', template_folder='../../templates/patient')


def format_patient_meta(patient):
    if not patient:
        return patient
    allergies = patient.get('allergies')
    if isinstance(allergies, str):
        try:
            parsed = json.loads(allergies)
            patient['allergies_list'] = parsed if isinstance(parsed, list) else [str(parsed)]
        except:
            patient['allergies_list'] = [allergies]
    elif isinstance(allergies, list):
        patient['allergies_list'] = allergies
    else:
        patient['allergies_list'] = ['Not Allergic']
        
    conditions = patient.get('chronic_conditions')
    if isinstance(conditions, str):
        try:
            parsed = json.loads(conditions)
            patient['conditions_list'] = parsed if isinstance(parsed, list) else [str(parsed)]
        except:
            patient['conditions_list'] = [conditions]
    elif isinstance(conditions, list):
        patient['conditions_list'] = conditions
    else:
        patient['conditions_list'] = []
    return patient


@patient_bp.route('/')
@patient_bp.route('/dashboard')
@patient_bp.route('/@<username>')
@login_required
def user_profile(username=None):
    user = get_current_user()
    
    if not username and user.get('role') != 'patient':
        patients_list = query_db('SELECT p.*, c.name as facility_id FROM patients p LEFT JOIN centers c ON p.center_id = c.id ORDER BY p.full_name ASC') or []
        return render_template('patient/list.html', current_user=user, patients=patients_list)

    if not username:
        username = user.get('username')
    username = username.strip().lstrip('@')
    
    if user['role'] == 'patient' and user['username'] != username:
        return redirect(f'/patient/@{user["username"]}')
        
    target_user = query_db('SELECT * FROM users WHERE username = %s', (username,), one=True)
    records = []
    patient = None
    appointments = []
    prescriptions = []
    latest_vitals = {}
    
    if target_user:
        patient = query_db('SELECT * FROM patients WHERE linked_user_id = %s', (target_user['id'],), one=True)
        if not patient and user['role'] == 'patient':
            patient = query_db('SELECT * FROM patients WHERE id = %s', ('PAT-001',), one=True)
            
        if patient:
            format_patient_meta(patient)
            raw_records = query_db("""
                SELECT m.*, u.full_name as doctor_name, c.name as center_name 
                FROM medical_records m 
                LEFT JOIN users u ON m.created_by = u.id 
                LEFT JOIN centers c ON m.center_id = c.id 
                WHERE m.patient_id = %s 
                ORDER BY m.created_at DESC
            """, (patient['id'],)) or []
            
            raw_prescriptions = query_db("""
                SELECT pr.*, u.full_name as doctor_name, c.name as center_name 
                FROM prescriptions pr 
                LEFT JOIN users u ON pr.prescribed_by = u.id 
                LEFT JOIN centers c ON pr.center_id = c.id 
                WHERE pr.patient_id = %s 
                ORDER BY pr.created_at DESC
            """, (patient['id'],)) or []
            
            for p in raw_prescriptions:
                if isinstance(p.get('medicines'), str):
                    try:
                        p['medicines_parsed'] = json.loads(p['medicines'])
                    except:
                        p['medicines_parsed'] = []
                else:
                    p['medicines_parsed'] = p.get('medicines', [])
                prescriptions.append(p)

            for r in raw_records:
                if isinstance(r.get('data'), str):
                    try:
                        r['data_parsed'] = json.loads(r['data'])
                    except:
                        r['data_parsed'] = {}
                else:
                    r['data_parsed'] = r.get('data', {})
                
                r['prescriptions'] = [p for p in prescriptions if p.get('record_id') == r['id']]
                records.append(r)
                
                if r.get('data_parsed') and isinstance(r['data_parsed'], dict):
                    v = r['data_parsed'].get('vitals')
                    if isinstance(v, dict):
                        for k, val in v.items():
                            if k not in latest_vitals:
                                latest_vitals[k] = val

            appointments = query_db('SELECT * FROM appointments WHERE patient_id = %s ORDER BY slot_time DESC', (patient['id'],)) or []
            referrals = query_db('''
                SELECT r.*, c_to.name as to_center_name, c_from.name as from_center_name, u.full_name as doctor_name
                FROM referrals r
                LEFT JOIN centers c_to ON r.to_center = c_to.id
                LEFT JOIN centers c_from ON r.from_center = c_from.id
                LEFT JOIN users u ON r.created_by = u.id
                WHERE r.patient_id = %s
                ORDER BY r.created_at DESC
            ''', (patient['id'],)) or []
            
    return render_template('dashboard/patient.html', current_user=user, profile_username=username, records=records, target_user=target_user, patient=patient, appointments=appointments, prescriptions=prescriptions, latest_vitals=latest_vitals)


@patient_bp.route('/records')
@patient_bp.route('/records/@<username>')
@patient_bp.route('/medical-records')
@patient_bp.route('/medical-records/@<username>')
@login_required
def patient_records(username=None):
    user = get_current_user()
    if not username:
        username = user.get('username')
    username = username.strip().lstrip('@')
    
    if user['role'] == 'patient' and user['username'] != username:
        return redirect(f'/patient/records/@{user["username"]}')
        
    target_user = query_db('SELECT * FROM users WHERE username = %s', (username,), one=True)
    records = []
    patient = None
    appointments = []
    prescriptions = []
    
    if target_user:
        patient = query_db('SELECT * FROM patients WHERE linked_user_id = %s', (target_user['id'],), one=True)
        if not patient:
            patient = query_db('SELECT * FROM patients WHERE id = %s', ('PAT-001',), one=True)
        if patient:
            format_patient_meta(patient)
            
            raw_prescriptions = query_db("""
                SELECT pr.*, u.full_name as doctor_name, c.name as center_name 
                FROM prescriptions pr 
                LEFT JOIN users u ON pr.prescribed_by = u.id 
                LEFT JOIN centers c ON pr.center_id = c.id 
                WHERE pr.patient_id = %s 
                ORDER BY pr.created_at DESC
            """, (patient['id'],)) or []
            
            for p in raw_prescriptions:
                if isinstance(p.get('medicines'), str):
                    try:
                        p['medicines_parsed'] = json.loads(p['medicines'])
                    except:
                        p['medicines_parsed'] = []
                else:
                    p['medicines_parsed'] = p.get('medicines', [])
                prescriptions.append(p)
                
            raw_records = query_db("""
                SELECT m.*, u.full_name as doctor_name, c.name as center_name 
                FROM medical_records m 
                LEFT JOIN users u ON m.created_by = u.id 
                LEFT JOIN centers c ON m.center_id = c.id 
                WHERE m.patient_id = %s 
                ORDER BY m.created_at DESC
            """, (patient['id'],)) or []
            
            for r in raw_records:
                if isinstance(r.get('data'), str):
                    try:
                        r['data_parsed'] = json.loads(r['data'])
                    except:
                        r['data_parsed'] = {}
                else:
                    r['data_parsed'] = r.get('data', {})
                    
                r['prescriptions'] = [p for p in prescriptions if p.get('record_id') == r['id']]
                records.append(r)
                
            appointments = query_db('SELECT * FROM appointments WHERE patient_id = %s ORDER BY slot_time DESC', (patient['id'],)) or []
            referrals = query_db("""
                SELECT r.*, c_to.name as to_center_name, c_from.name as from_center_name, u.full_name as doctor_name
                FROM referrals r
                LEFT JOIN centers c_to ON r.to_center = c_to.id
                LEFT JOIN centers c_from ON r.from_center = c_from.id
                LEFT JOIN users u ON r.created_by = u.id
                WHERE r.patient_id = %s
                ORDER BY r.created_at DESC
            """, (patient['id'],)) or []
            
    return render_template('patient/my_records.html', current_user=user, profile_username=username, records=records, target_user=target_user, patient=patient, appointments=appointments, prescriptions=prescriptions, referrals=referrals)


@patient_bp.route('/map')
@patient_bp.route('/map/@<username>')
@login_required
def patient_map(username=None):
    user = get_current_user()
    if not username:
        username = user.get('username')
    username = username.strip().lstrip('@')
    selected_facility_id = request.args.get('facility', '').strip()
    facilities = query_db('SELECT * FROM centers ORDER BY name ASC') or []
    for fac in facilities:
        if not fac.get('district'):
            fac['district'] = fac.get('region') or fac.get('state') or 'Main Region'
        if not fac.get('phone'):
            fac['phone'] = '+91 11 2345 6789'
    return render_template('map.html', profile_username=username, current_user=user, facilities=facilities, selected_facility_id=selected_facility_id)


def patient_facilities(username=None):
    user = get_current_user()
    if not username:
        username = user.get('username')
    username = username.strip().lstrip('@')
    facilities = query_db('SELECT * FROM centers ORDER BY name ASC') or []
    for fac in facilities:
        if not fac.get('district'):
            fac['district'] = fac.get('region') or fac.get('state') or 'Main Center'
    return render_template('facilities/list.html', profile_username=username, facilities=facilities, current_user=user)


@patient_bp.route('/notifications')
@patient_bp.route('/notifications/@<username>')
@login_required
def patient_notifications(username=None):
    user = get_current_user()
    if not username:
        username = user.get('username')
    username = username.strip().lstrip('@')
    notifs = []
    if user:
        notifs = query_db('SELECT * FROM notifications WHERE user_id = %s ORDER BY created_at DESC LIMIT 50', (user['id'],)) or []
    return render_template('notifications.html', profile_username=username, notifications=notifs, current_user=user)


@patient_bp.route('/emergency')
@patient_bp.route('/emergency/@<username>')
@patient_bp.route('/emergency-contact')
@patient_bp.route('/emergency-contact/@<username>')
@login_required
def patient_emergency(username=None):
    user = get_current_user()
    if not username:
        username = user.get('username')
    username = username.strip().lstrip('@')
    target_user = query_db('SELECT * FROM users WHERE username = %s', (username,), one=True)
    patient = None
    if target_user:
        patient = query_db('SELECT * FROM patients WHERE linked_user_id = %s', (target_user['id'],), one=True)
    return render_template('emergency.html', profile_username=username, patient=patient, current_user=user, target_user=target_user)


@patient_bp.route('/me')
@login_required
def my_records_redirect():
    user = get_current_user()
    return redirect(url_for('patient.user_profile', username=user['username']))


@patient_bp.route('/<patient_id>')
@patient_bp.route('/<patient_id>/@<username>')
@login_required
def patient_detail(patient_id, username=None):
    patient_id = patient_id.strip()
    if patient_id.startswith('@'):
        return redirect(url_for('patient.user_profile', username=patient_id.lstrip('@')))
        
    user = get_current_user()
    patient = query_db('SELECT * FROM patients WHERE id = %s', (patient_id,), one=True)
    if not patient:
        abort(404)
        
    if user['role'] == 'patient' and patient.get('linked_user_id') != user['id']:
        return redirect(url_for('patient.user_profile', username=user['username']))
        
    format_patient_meta(patient)
    center = query_db('SELECT * FROM centers WHERE id = %s', (patient.get('center_id'),), one=True) or {'name': patient.get('center_id') or 'Primary Health Centre'}
    
    raw_prescriptions = query_db("""
        SELECT pr.*, u.full_name as doctor_name, c.name as center_name 
        FROM prescriptions pr 
        LEFT JOIN users u ON pr.prescribed_by = u.id 
        LEFT JOIN centers c ON pr.center_id = c.id 
        WHERE pr.patient_id = %s 
        ORDER BY pr.created_at DESC
    """, (patient['id'],)) or []
    
    prescriptions = []
    for p in raw_prescriptions:
        if isinstance(p.get('medicines'), str):
            try:
                p['medicines_parsed'] = json.loads(p['medicines'])
            except:
                p['medicines_parsed'] = []
        else:
            p['medicines_parsed'] = p.get('medicines', [])
        prescriptions.append(p)

    raw_records = query_db("""
        SELECT m.*, u.full_name as doctor_name, c.name as center_name 
        FROM medical_records m 
        LEFT JOIN users u ON m.created_by = u.id 
        LEFT JOIN centers c ON m.center_id = c.id 
        WHERE m.patient_id = %s 
        ORDER BY m.created_at DESC
    """, (patient['id'],)) or []
    
    records = []
    latest_vitals = {}
    for r in raw_records:
        if isinstance(r.get('data'), str):
            try:
                r['data_parsed'] = json.loads(r['data'])
            except:
                r['data_parsed'] = {}
        else:
            r['data_parsed'] = r.get('data', {})
            
        r['prescriptions'] = [p for p in prescriptions if p.get('record_id') == r['id']]
        records.append(r)
        
        if r.get('data_parsed') and isinstance(r['data_parsed'], dict):
            v = r['data_parsed'].get('vitals')
            if isinstance(v, dict):
                for k, val in v.items():
                    if k not in latest_vitals:
                        latest_vitals[k] = val
            
    appointments = query_db('SELECT * FROM appointments WHERE patient_id = %s ORDER BY slot_time DESC', (patient['id'],)) or []
    
    return render_template('patient/detail.html', current_user=user, patient=patient, patient_id=patient_id, center=center, records=records, prescriptions=prescriptions, appointments=appointments, latest_vitals=latest_vitals)


@patient_bp.route('/teleconsult')
@patient_bp.route('/teleconsult/@<username>')
@login_required
def patient_teleconsult(username=None):
    user = get_current_user()
    if not username:
        username = user.get('username')
    username = username.strip().lstrip('@')
    target_user = query_db('SELECT * FROM users WHERE username = %s', (username,), one=True)
    patient = None
    sessions = []
    if target_user:
        patient = query_db('SELECT * FROM patients WHERE linked_user_id = %s', (target_user['id'],), one=True)
        if patient:
            sessions = query_db("""
                SELECT t.*, u.full_name as doctor_name, u.designation as doctor_designation, c.name as center_name
                FROM teleconsult_sessions t
                LEFT JOIN users u ON t.doctor_id = u.id
                LEFT JOIN centers c ON t.center_id = c.id
                WHERE t.patient_id = %s
                ORDER BY t.created_at DESC
            """, (patient['id'],)) or []
    return render_template('patient/teleconsult.html', current_user=user, profile_username=username, patient=patient, sessions=sessions)


@patient_bp.route('/appointments')
@patient_bp.route('/appointments/@<username>')
@login_required
def patient_appointments(username=None):
    from datetime import timedelta
    user = get_current_user()
    if not username:
        username = user.get('username')
    username = username.strip().lstrip('@')
    target_user = query_db('SELECT * FROM users WHERE username = %s', (username,), one=True)
    patient = None
    appointments = []
    active_token = None
    referrals = []
    now = datetime.now()

    if target_user:
        patient = query_db('SELECT * FROM patients WHERE linked_user_id = %s', (target_user['id'],), one=True)
        if not patient:
            patient = query_db('SELECT * FROM patients WHERE id = %s', ('PAT-2026-0001',), one=True)

        if patient:
            raw_appts = query_db("""
                SELECT a.*, c.name as center_name, c.phone as center_phone, u.full_name as doctor_name
                FROM appointments a
                LEFT JOIN centers c ON a.center_id = c.id
                LEFT JOIN users u ON a.doctor_id = u.id
                WHERE a.patient_id = %s
                ORDER BY a.slot_time DESC
            """, (patient['id'],)) or []

            appointments = raw_appts

            for a in raw_appts:
                is_active_status = a.get('status') in ('checked_in', 'in_progress')
                is_upcoming_today = (a.get('status') == 'scheduled' and a.get('slot_time') and a['slot_time'] >= now - timedelta(hours=4))
                if is_active_status or is_upcoming_today:
                    active_token = dict(a)
                    ahead_res = query_db("""
                        SELECT COUNT(*) as c FROM appointments
                        WHERE center_id = %s AND status IN ('checked_in', 'scheduled')
                          AND (urgency < %s OR (urgency = %s AND slot_time < %s))
                    """, (a['center_id'], a['urgency'], a['urgency'], a['slot_time']), one=True)
                    active_token['patients_ahead'] = ahead_res['c'] if ahead_res else 0
                    active_token['est_wait_min'] = max(5, (active_token['patients_ahead'] + (0 if a.get('status') == 'in_progress' else 1)) * 12)
                    break

            referrals = query_db("""
                SELECT r.*, c_to.name as to_center_name, c_to.type as to_center_type,
                       c_from.name as from_center_name, u.full_name as doctor_name
                FROM referrals r
                LEFT JOIN centers c_to ON r.to_center = c_to.id
                LEFT JOIN centers c_from ON r.from_center = c_from.id
                LEFT JOIN users u ON r.created_by = u.id
                WHERE r.patient_id = %s
                ORDER BY r.created_at DESC
            """, (patient['id'],)) or []

    facilities = query_db("SELECT * FROM centers ORDER BY name ASC") or []
    server_time_iso = now.strftime('%Y-%m-%dT%H:%M')

    return render_template('patient/appointments.html', current_user=user, profile_username=username,
                           patient=patient, appointments=appointments, active_token=active_token,
                           referrals=referrals, facilities=facilities, server_time_iso=server_time_iso)


@patient_bp.route('/appointments/book', methods=['POST'])
@login_required
def patient_book_appointment():
    from utils.audit import log_audit
    from datetime import timedelta
    user = get_current_user()
    patient = query_db('SELECT * FROM patients WHERE linked_user_id = %s', (user['id'],), one=True)
    if not patient:
        patient = query_db('SELECT * FROM patients WHERE id = %s', ('PAT-2026-0001',), one=True)

    if not patient:
        flash('Patient profile not found for booking.', 'error')
        return redirect(url_for('patient.user_profile', username=user['username']))

    center_id = (request.form.get('center_id') or 'FAC-BAKROL-01').strip()
    department = (request.form.get('department') or 'General OPD').strip()
    reason = (request.form.get('reason') or 'Online Scheduled Consultation').strip()
    slot_time_str = request.form.get('slot_time')

    now = datetime.now()
    if slot_time_str:
        try:
            slot_time = datetime.strptime(slot_time_str, '%Y-%m-%dT%H:%M')
        except:
            slot_time = now
    else:
        slot_time = now

    if slot_time < now - timedelta(minutes=5):
        flash('Appointment slot cannot be set in the past. Please select an upcoming date and time.', 'error')
        return redirect(url_for('patient.patient_appointments', username=user['username']))

    count_res = query_db("""
        SELECT COUNT(*) as c FROM appointments 
        WHERE center_id = %s AND DATE(created_at) = CURDATE()
    """, (center_id,), one=True)
    next_idx = (count_res['c'] if count_res else 0) + 1
    token_number = f"OPD-{next_idx:03d}"

    appt_id = execute_db("""
        INSERT INTO appointments (patient_id, center_id, token_number, department, slot_time, reason, urgency, status, notes)
        VALUES (%s, %s, %s, %s, %s, %s, 3, 'scheduled', 'Booked via Patient Portal Online Scheduler')
    """, (patient['id'], center_id, token_number, department, slot_time, reason))

    log_audit('patient_booked_appointment', 'appointment', appt_id)
    flash(f"Appointment successfully scheduled! Your OPD Token is #{token_number}.", 'success')
    return redirect(url_for('patient.patient_appointments', username=user['username']))
