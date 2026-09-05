import csv
import io
from flask import Response
import json
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, jsonify
from utils.auth_helpers import role_required, get_current_user
from utils.db import query_db, execute_db

phc_bp = Blueprint('phc', __name__, url_prefix='/phc', template_folder='../../templates/phc')

ALLOWED_ROLES = ('doctor', 'nurse', 'helper', 'ambulance_op', 'care_taker', 'therapist', 'pharmacist', 'lab_technician', 'receptionist', 'system_admin', 'region_admin')


@phc_bp.route('/')
@phc_bp.route('/dashboard')
@phc_bp.route('/@<username>')
@role_required(*ALLOWED_ROLES)
def dashboard(username=None):
    user = get_current_user()
    if username and username.strip().lstrip('@') != user.get('username') and user.get('role') not in ('system_admin', 'region_admin'):
        return redirect(f'/phc/@{user.get("username")}')
        
    center_id = user.get('center_id') or 'FAC-BAKROL-01'
    center = query_db('SELECT * FROM centers WHERE id = %s', (center_id,), one=True) or {'id': 'FAC-BAKROL-01', 'name': 'Primary Health Centre 1', 'type': 'PHC', 'region': 'North Region'}

    queue = query_db("""
        SELECT a.*, p.full_name as patient_name, p.gender, p.dob, p.blood_group, p.is_high_risk 
        FROM appointments a 
        LEFT JOIN patients p ON a.patient_id = p.id 
        WHERE a.center_id = %s 
        ORDER BY a.urgency ASC, a.slot_time ASC
    """, (center_id,)) or []

    inventory = query_db('SELECT * FROM inventory_items WHERE center_id = %s ORDER BY quantity ASC', (center_id,)) or []
    low_stock_items = [item for item in inventory if item['quantity'] <= item['reorder_level']]

    prescriptions = query_db("""
        SELECT pr.*, p.full_name as patient_name, u.full_name as doctor_name
        FROM prescriptions pr
        LEFT JOIN patients p ON pr.patient_id = p.id
        LEFT JOIN users u ON pr.prescribed_by = u.id
        WHERE pr.center_id = %s
        ORDER BY pr.created_at DESC LIMIT 6
    """, (center_id,)) or []
    for pr in prescriptions:
        if isinstance(pr.get('medicines'), str):
            try:
                pr['medicines_parsed'] = json.loads(pr['medicines'])
            except:
                pr['medicines_parsed'] = []
        else:
            pr['medicines_parsed'] = pr.get('medicines', [])

    referrals = query_db("""
        SELECT r.*, p.full_name as patient_name, c_to.name as to_center_name, c_from.name as from_center_name
        FROM referrals r
        LEFT JOIN patients p ON r.patient_id = p.id
        LEFT JOIN centers c_to ON r.to_center = c_to.id
        LEFT JOIN centers c_from ON r.from_center = c_from.id
        WHERE r.from_center = %s OR r.to_center = %s
        ORDER BY r.created_at DESC LIMIT 5
    """, (center_id, center_id)) or []

    teleconsults = query_db("""
        SELECT t.*, p.full_name as patient_name, u.full_name as doctor_name
        FROM teleconsult_sessions t
        LEFT JOIN patients p ON t.patient_id = p.id
        LEFT JOIN users u ON t.doctor_id = u.id
        WHERE t.center_id = %s
        ORDER BY t.created_at DESC LIMIT 5
    """, (center_id,)) or []

    pat_count_row = query_db('SELECT COUNT(*) as cnt FROM patients WHERE center_id = %s', (center_id,), one=True)
    patient_count = pat_count_row['cnt'] if pat_count_row else len(queue)

    stats = {
        'today_queue': len(queue),
        'low_stock': len(low_stock_items),
        'active_referrals': len([r for r in referrals if r['status'] in ('initiated', 'in_transit')]),
        'total_patients': patient_count,
        'teleconsults_count': len(teleconsults)
    }

    return render_template('phc/dashboard.html', 
                           current_user=user, 
                           profile_username=user.get('username'),
                           center=center, 
                           queue=queue, 
                           inventory=inventory,
                           low_stock_items=low_stock_items,
                           prescriptions=prescriptions,
                           referrals=referrals,
                           teleconsults=teleconsults,
                           stats=stats)


@phc_bp.route('/queue')
@phc_bp.route('/appointments')
@role_required(*ALLOWED_ROLES)
def queue():
    user = get_current_user()
    center_id = user.get('center_id') or 'FAC-BAKROL-01'
    center = query_db('SELECT * FROM centers WHERE id = %s', (center_id,), one=True) or {'name': center_id}

    all_appointments = query_db("""
        SELECT a.*, p.full_name as patient_name, p.gender, p.dob, p.blood_group, p.is_high_risk, p.phone,
               u.full_name as doctor_name, u.designation as doctor_designation
        FROM appointments a 
        LEFT JOIN patients p ON a.patient_id = p.id 
        LEFT JOIN users u ON a.doctor_id = u.id
        WHERE a.center_id = %s 
        ORDER BY a.urgency ASC, a.slot_time ASC
    """, (center_id,)) or []

    for idx, item in enumerate(all_appointments, 1):
        if not item.get('token_number'):
            prefix = 'EMG' if item.get('urgency') == 1 else 'OPD'
            item['token_number'] = f"{prefix}-{idx:03d}"

    waiting_list = [a for a in all_appointments if a.get('status') in ('checked_in', 'scheduled')]
    in_consultation = [a for a in all_appointments if a.get('status') == 'in_progress']
    completed_list = [a for a in all_appointments if a.get('status') == 'completed']

    stats = {
        'total': len(all_appointments),
        'waiting': len(waiting_list),
        'in_progress': len(in_consultation),
        'completed': len(completed_list),
        'critical': sum(1 for a in waiting_list if a.get('urgency') == 1),
        'avg_wait_min': max(5, len(waiting_list) * 12)
    }

    doctors = query_db("""
        SELECT id, full_name, designation, role 
        FROM users 
        WHERE (center_id = %s OR center_id IS NULL) AND is_active = 1 
        ORDER BY full_name ASC
    """, (center_id,)) or []

    patients = query_db("""
        SELECT id, full_name, phone, gender, dob, blood_group 
        FROM patients 
        ORDER BY full_name ASC LIMIT 100
    """) or []

    departments = [
        'General OPD', 'Emergency / Triage', 'Pediatrics', 
        'Obstetrics & Gynecology', 'Cardiology', 'Orthopedics', 
        'General Surgery', 'Dental', 'Dermatology', 'Ayush / Wellness'
    ]

    return render_template('phc/queue.html', current_user=user, center=center,
                           queue=waiting_list, in_consultation=in_consultation, 
                           completed=completed_list, all_appointments=all_appointments,
                           stats=stats, doctors=doctors, patients=patients, departments=departments)


@phc_bp.route('/appointments/book', methods=['POST'])
@phc_bp.route('/queue/generate-token', methods=['POST'])
@role_required(*ALLOWED_ROLES)
def book_appointment():
    from utils.audit import log_audit
    user = get_current_user()
    center_id = user.get('center_id') or 'FAC-BAKROL-01'
    data = request.get_json(silent=True) or request.form.to_dict()

    patient_id = (data.get('patient_id') or '').strip()
    doctor_id = data.get('doctor_id') or None
    department = (data.get('department') or 'General OPD').strip()
    reason = (data.get('reason') or 'Walk-in OPD Consultation').strip()
    urgency_raw = data.get('urgency', 3)
    try:
        urgency = int(urgency_raw)
    except:
        urgency = 3

    status = (data.get('status') or 'checked_in').strip()
    slot_time_str = data.get('slot_time')
    if slot_time_str:
        try:
            slot_time = datetime.strptime(slot_time_str, '%Y-%m-%dT%H:%M')
        except:
            slot_time = datetime.now()
    else:
        slot_time = datetime.now()

    if not patient_id:
        if request.is_json:
            return jsonify({'ok': False, 'error': 'Patient ID is required.'}), 400
        flash('Patient selection is required to issue token or book appointment.', 'error')
        return redirect(url_for('phc.queue'))

    count_res = query_db("""
        SELECT COUNT(*) as c FROM appointments 
        WHERE center_id = %s AND DATE(created_at) = CURDATE()
    """, (center_id,), one=True)
    next_idx = (count_res['c'] if count_res else 0) + 1
    prefix = 'EMG' if urgency == 1 else ('OPD' if department == 'General OPD' else department[:3].upper())
    token_number = f"{prefix}-{next_idx:03d}"

    appt_id = execute_db("""
        INSERT INTO appointments (patient_id, center_id, doctor_id, token_number, department, slot_time, reason, urgency, status, notes)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (patient_id, center_id, doctor_id, token_number, department, slot_time, reason, urgency, status, data.get('notes')))

    log_audit('appointment_booked', 'appointment', appt_id)

    if request.is_json:
        return jsonify({
            'ok': True,
            'appointment_id': appt_id,
            'token_number': token_number,
            'status': status,
            'message': f"Token {token_number} generated successfully."
        })

    flash(f"Token #{token_number} generated successfully for Patient {patient_id}. Added to waiting queue.", 'success')
    return redirect(url_for('phc.queue'))


@phc_bp.route('/queue/<int:appointment_id>/update-status', methods=['POST'])
@role_required(*ALLOWED_ROLES)
def update_queue_status(appointment_id):
    from utils.audit import log_audit
    user = get_current_user()
    data = request.get_json(silent=True) or request.form.to_dict()
    new_status = (data.get('status') or '').strip()
    doctor_id = data.get('doctor_id') or (user['id'] if user['role'] in ('doctor', 'medical_officer') else None)

    appt = query_db('SELECT * FROM appointments WHERE id = %s', (appointment_id,), one=True)
    if not appt:
        if request.is_json:
            return jsonify({'ok': False, 'error': 'Appointment not found.'}), 404
        flash('Appointment not found.', 'error')
        return redirect(url_for('phc.queue'))

    if new_status == 'in_progress':
        execute_db("""
            UPDATE appointments 
            SET status = 'in_progress', doctor_id = COALESCE(%s, doctor_id)
            WHERE id = %s
        """, (doctor_id, appointment_id))
    elif new_status == 'completed':
        execute_db("""
            UPDATE appointments 
            SET status = 'completed', end_time = NOW()
            WHERE id = %s
        """, (appointment_id,))
    elif new_status in ('checked_in', 'scheduled', 'no_show', 'cancelled'):
        execute_db("""
            UPDATE appointments 
            SET status = %s
            WHERE id = %s
        """, (new_status, appointment_id))

    log_audit('queue_status_updated', 'appointment', appointment_id)

    if request.is_json:
        return jsonify({'ok': True, 'appointment_id': appointment_id, 'new_status': new_status})

    flash(f"Queue token #{appt.get('token_number') or appointment_id} marked as {new_status.replace('_', ' ').title()}.", "success")
    return redirect(url_for('phc.queue'))


@phc_bp.route('/queue/display')
@role_required(*ALLOWED_ROLES)
def queue_display():
    user = get_current_user()
    center_id = user.get('center_id') or 'FAC-BAKROL-01'
    center = query_db('SELECT * FROM centers WHERE id = %s', (center_id,), one=True) or {'name': 'Primary Health Centre'}
    return render_template('phc/queue_display.html', current_user=user, center=center)


@phc_bp.route('/queue/display/data')
@role_required(*ALLOWED_ROLES)
def queue_display_data():
    user = get_current_user()
    center_id = user.get('center_id') or 'FAC-BAKROL-01'
    center = query_db('SELECT * FROM centers WHERE id = %s', (center_id,), one=True) or {'name': center_id}

    items = query_db("""
        SELECT a.*, p.full_name as patient_name, u.full_name as doctor_name, u.designation as doctor_designation
        FROM appointments a
        LEFT JOIN patients p ON a.patient_id = p.id
        LEFT JOIN users u ON a.doctor_id = u.id
        WHERE a.center_id = %s AND a.status IN ('checked_in', 'in_progress', 'scheduled')
        ORDER BY a.urgency ASC, a.slot_time ASC
    """, (center_id,)) or []

    for idx, item in enumerate(items, 1):
        if not item.get('token_number'):
            prefix = 'EMG' if item.get('urgency') == 1 else 'OPD'
            item['token_number'] = f"{prefix}-{idx:03d}"

    in_consultation = [
        {
            'token': a.get('token_number'),
            'patient': a.get('patient_name') or a.get('patient_id'),
            'doctor': a.get('doctor_name') or 'Medical Officer',
            'department': a.get('department') or 'General OPD',
            'urgency': a.get('urgency')
        }
        for a in items if a.get('status') == 'in_progress'
    ]

    waiting_items = [a for a in items if a.get('status') in ('checked_in', 'scheduled')]
    next_in_line = [
        {
            'token': a.get('token_number'),
            'patient': (a.get('patient_name') or a.get('patient_id'))[:15],
            'department': a.get('department') or 'General OPD',
            'urgency': a.get('urgency'),
            'est_time': f"~{idx * 10} mins"
        }
        for idx, a in enumerate(waiting_items[:5], 1)
    ]

    return jsonify({
        'center_name': center.get('name'),
        'current_time': datetime.now().strftime('%I:%M:%S %p'),
        'in_consultation': in_consultation,
        'next_in_line': next_in_line,
        'total_waiting': len(waiting_items),
        'avg_wait_min': max(5, len(waiting_items) * 12)
    })


@phc_bp.route('/referrals/<int:referral_id>/enqueue', methods=['POST'])
@role_required(*ALLOWED_ROLES)
def enqueue_referral(referral_id):
    from utils.audit import log_audit
    user = get_current_user()
    referral = query_db('SELECT * FROM referrals WHERE id = %s', (referral_id,), one=True)
    if not referral:
        flash('Referral record not found.', 'error')
        return redirect(url_for('phc.referrals'))

    dest_center = referral['to_center']
    patient_id = referral['patient_id']

    count_res = query_db("""
        SELECT COUNT(*) as c FROM appointments 
        WHERE center_id = %s AND DATE(created_at) = CURDATE()
    """, (dest_center,), one=True)
    next_idx = (count_res['c'] if count_res else 0) + 1
    token_number = f"REF-{next_idx:03d}"

    urgency_map = {'critical': 1, 'high': 2, 'medium': 3, 'low': 3}
    num_urgency = urgency_map.get(referral.get('urgency'), 2)

    appt_id = execute_db("""
        INSERT INTO appointments (patient_id, center_id, token_number, department, referral_id, slot_time, reason, urgency, status, notes)
        VALUES (%s, %s, %s, %s, %s, NOW(), %s, %s, 'checked_in', %s)
    """, (patient_id, dest_center, token_number, 'Referred Specialist OPD', referral_id,
           f"Inter-Hospital Referral Transfer: {referral.get('reason') or 'Specialist Care'}",
           num_urgency, f"Referred from {referral.get('from_center')}. Priority Queue Admission."))

    if referral['status'] == 'initiated':
        execute_db("UPDATE referrals SET status = 'accepted', accepted_by = %s WHERE id = %s", (user['id'], referral_id))

    log_audit('referral_enqueued', 'referral', referral_id)
    flash(f"Patient successfully enrolled into destination facility OPD Queue with Priority Token #{token_number}!", 'success')
    return redirect(url_for('phc.queue'))


@phc_bp.route('/consultation', methods=['GET', 'POST'])
@phc_bp.route('/consultation/<patient_id>', methods=['GET', 'POST'])
@role_required('doctor', 'nurse', 'system_admin')
def consultation(patient_id=None):
    user = get_current_user()
    center_id = user.get('center_id') or 'FAC-BAKROL-01'
    
    if request.method == 'POST':
        data = request.get_json(silent=True) or request.form.to_dict()
        target_patient_id = patient_id or data.get('patient_id')
        
        if not target_patient_id:
            if request.is_json:
                return jsonify({'ok': False, 'error': 'Patient ID is required.'}), 400
            flash('Patient ID is required.', 'error')
            return redirect(url_for('phc.consultation'))
            
        patient = query_db('SELECT * FROM patients WHERE id = %s', (target_patient_id,), one=True)
        if not patient:
            if request.is_json:
                return jsonify({'ok': False, 'error': 'Patient not found.'}), 404
            flash('Patient not found.', 'error')
            return redirect(url_for('phc.consultation'))

        symptoms = data.get('symptoms', '').strip()
        diagnosis = data.get('diagnosis', '').strip()
        bp = data.get('bp', '').strip()
        pulse = data.get('pulse', '').strip()
        spo2 = data.get('spo2', '').strip()
        temp = data.get('temperature', '').strip()
        meds_text = data.get('medications', '').strip()
        
        vitals = {}
        if bp: vitals['BP'] = bp
        if pulse: vitals['Pulse'] = pulse
        if spo2: vitals['SpO2'] = spo2
        if temp: vitals['Temp'] = temp
        
        record_data = {
            'symptoms': symptoms,
            'notes': diagnosis,
            'vitals': vitals
        }
        
        title = f"OPD Consultation - {diagnosis[:40]}" if diagnosis else f"Clinical Consultation ({datetime.now().strftime('%b %d, %Y')})"
        
        record_id = execute_db("""
            INSERT INTO medical_records (patient_id, record_type, title, data, center_id, created_by)
            VALUES (%s, 'consultation', %s, %s, %s, %s)
        """, (target_patient_id, title, json.dumps(record_data), center_id, user['id']))
        
        med_items = []
        rx_id = None
        if meds_text:
            for line in meds_text.replace(';', '\n').replace(',', '\n').split('\n'):
                line = line.strip()
                if line:
                    med_items.append({'name': line, 'dosage': 'Standard / As advised', 'frequency': 'As directed'})
            
            rx_id = execute_db("""
                INSERT INTO prescriptions (record_id, patient_id, medicines, notes, prescribed_by, center_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (record_id, target_patient_id, json.dumps(med_items), f"Prescription for {diagnosis}" if diagnosis else "Clinical Prescription", user['id'], center_id))
            
        execute_db("""
            UPDATE appointments SET status = 'completed'
            WHERE patient_id = %s AND center_id = %s AND status IN ('scheduled', 'checked_in', 'in_progress')
        """, (target_patient_id, center_id))
        
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'ok': True,
                'message': 'Consultation and e-Prescription saved successfully!',
                'record_id': record_id,
                'rx_id': rx_id,
                'record': {
                    'title': title,
                    'created_at': datetime.now().strftime('%Y-%m-%d'),
                    'notes': diagnosis,
                    'symptoms': symptoms,
                    'vitals': vitals,
                    'medicines': med_items
                }
            })
            
        flash('Consultation & e-Prescription saved successfully.', 'success')
        return redirect(url_for('phc.consultation', patient_id=target_patient_id))

    patient = None
    records = []
    prescriptions = []
    
    if patient_id:
        patient = query_db('SELECT * FROM patients WHERE id = %s', (patient_id,), one=True)
        if patient:
            raw_records = query_db('SELECT * FROM medical_records WHERE patient_id = %s ORDER BY created_at DESC', (patient['id'],)) or []
            for r in raw_records:
                if isinstance(r.get('data'), str):
                    try:
                        r['data_parsed'] = json.loads(r['data'])
                    except:
                        r['data_parsed'] = {}
                else:
                    r['data_parsed'] = r.get('data', {})
                records.append(r)
                
            raw_prescriptions = query_db("""
                SELECT pr.*, u.full_name as doctor_name 
                FROM prescriptions pr 
                LEFT JOIN users u ON pr.prescribed_by = u.id 
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
                
    patients_list = query_db('SELECT id, full_name, dob, gender, blood_group FROM patients ORDER BY full_name ASC') or []
    return render_template('phc/consultation.html', current_user=user, patient=patient, patient_id=patient_id, records=records, prescriptions=prescriptions, patients_list=patients_list)


@phc_bp.route('/teleconsult')
@phc_bp.route('/contact')
@role_required(*ALLOWED_ROLES)
def teleconsult():
    user = get_current_user()
    center_id = user.get('center_id') or 'FAC-BAKROL-01'
    is_admin = user.get('role') in ('system_admin', 'region_admin')

    teleconsults = query_db("""
        SELECT t.*, p.full_name as patient_name, p.gender, p.dob, p.blood_group,
               u.full_name as doctor_name, u.role as doctor_role, u.designation as doctor_designation,
               c.name as center_name, c.type as center_type
        FROM teleconsult_sessions t
        LEFT JOIN patients p ON t.patient_id = p.id
        LEFT JOIN users u ON t.doctor_id = u.id
        LEFT JOIN centers c ON t.center_id = c.id
        WHERE (t.center_id = %s OR t.doctor_id = %s OR %s)
        ORDER BY CASE t.status WHEN 'active' THEN 1 WHEN 'requested' THEN 2 ELSE 3 END, t.created_at DESC
    """, (center_id, user['id'], 1 if is_admin else 0)) or []

    stats = {
        'total': len(teleconsults),
        'active': len([t for t in teleconsults if t['status'] == 'active']),
        'requested': len([t for t in teleconsults if t['status'] == 'requested']),
        'completed': len([t for t in teleconsults if t['status'] == 'completed'])
    }

    specialists = query_db("""
        SELECT u.id, u.full_name, u.role, u.designation, c.name as facility_name, c.id as center_id, c.type as facility_type
        FROM users u
        LEFT JOIN centers c ON u.center_id = c.id
        WHERE u.role IN ('doctor', 'therapist', 'nurse', 'system_admin') AND u.is_active = 1
        ORDER BY u.full_name ASC
    """) or []

    patients_list = query_db('SELECT id, full_name, dob, gender, blood_group FROM patients ORDER BY full_name ASC') or []

    return render_template('phc/teleconsult.html', current_user=user, teleconsults=teleconsults,
                           specialists=specialists, patients_list=patients_list, stats=stats)


@phc_bp.route('/teleconsult/create', methods=['POST'])
@role_required(*ALLOWED_ROLES)
def create_teleconsult():
    from utils.audit import log_audit
    user = get_current_user()
    center_id = user.get('center_id') or 'FAC-BAKROL-01'

    patient_id = request.form.get('patient_id', '').strip()
    doctor_id = request.form.get('doctor_id', '').strip()
    clinical_summary = request.form.get('summary', '').strip()
    department = request.form.get('department', '').strip()
    priority = request.form.get('priority', 'routine').strip()
    pre_vitals = request.form.get('pre_vitals', '').strip()

    if not patient_id or not doctor_id:
        flash('Please select a patient and a medical specialist.', 'error')
        return redirect(url_for('phc.teleconsult'))

    full_summary = f"[Department: {department or 'General Medicine'}] [Priority: {priority.upper()}]\n" + clinical_summary
    if pre_vitals:
        full_summary += f"\nInitial Vitals: {pre_vitals}"

    session_id = execute_db("""
        INSERT INTO teleconsult_sessions (patient_id, doctor_id, center_id, status, summary)
        VALUES (%s, %s, %s, 'requested', %s)
    """, (patient_id, doctor_id, center_id, full_summary))

    execute_db("""
        INSERT INTO teleconsult_messages (session_id, sender_id, body)
        VALUES (%s, %s, %s)
    """, (session_id, user['id'], f'Teleconsultation requested for Patient {patient_id}. Clinical Reason: {clinical_summary}'))

    execute_db("""
        INSERT INTO notifications (user_id, title, body, link)
        VALUES (%s, %s, %s, %s)
    """, (doctor_id, 'New Teleconsultation Request',
          f'Remote consultation requested for Patient {patient_id}. Priority: {priority.title()}',
          url_for('phc.teleconsult_room', session_id=session_id)))

    log_audit('teleconsult_requested', 'teleconsult_session', session_id)
    flash(f'Teleconsultation session requested successfully! Connected to specialist room #{session_id}.', 'success')
    return redirect(url_for('phc.teleconsult_room', session_id=session_id))


@phc_bp.route('/teleconsult/room/<int:session_id>')
@role_required(*ALLOWED_ROLES)
def teleconsult_room(session_id):
    user = get_current_user()
    session_data = query_db("""
        SELECT t.*, p.full_name as patient_name, p.gender, p.dob, p.blood_group, p.allergies, p.chronic_conditions, p.phone as patient_phone,
               u.full_name as doctor_name, u.role as doctor_role, u.designation as doctor_designation,
               c.name as center_name, c.type as center_type
        FROM teleconsult_sessions t
        LEFT JOIN patients p ON t.patient_id = p.id
        LEFT JOIN users u ON t.doctor_id = u.id
        LEFT JOIN centers c ON t.center_id = c.id
        WHERE t.id = %s
    """, (session_id,), one=True)

    if not session_data:
        flash('Teleconsultation session not found.', 'error')
        return redirect(url_for('phc.teleconsult'))

    if session_data['status'] == 'requested':
        execute_db("UPDATE teleconsult_sessions SET status = 'active', started_at = COALESCE(started_at, NOW()) WHERE id = %s", (session_id,))
        session_data['status'] = 'active'

    allergies = session_data.get('allergies')
    if isinstance(allergies, str):
        try:
            parsed = json.loads(allergies)
            session_data['allergies_list'] = parsed if isinstance(parsed, list) else [str(parsed)]
        except:
            session_data['allergies_list'] = [allergies]
    else:
        session_data['allergies_list'] = ['Not Allergic']

    conditions = session_data.get('chronic_conditions')
    if isinstance(conditions, str):
        try:
            parsed = json.loads(conditions)
            session_data['conditions_list'] = parsed if isinstance(parsed, list) else [str(parsed)]
        except:
            session_data['conditions_list'] = [conditions]
    else:
        session_data['conditions_list'] = []

    patient_records = query_db("""
        SELECT m.*, u.full_name as doctor_name 
        FROM medical_records m 
        LEFT JOIN users u ON m.created_by = u.id 
        WHERE m.patient_id = %s 
        ORDER BY m.created_at DESC LIMIT 5
    """, (session_data['patient_id'],)) or []

    for r in patient_records:
        if isinstance(r.get('data'), str):
            try:
                r['data_parsed'] = json.loads(r['data'])
            except:
                r['data_parsed'] = {}
        else:
            r['data_parsed'] = r.get('data', {})

    prescriptions = query_db("""
        SELECT pr.*, u.full_name as doctor_name 
        FROM prescriptions pr 
        LEFT JOIN users u ON pr.prescribed_by = u.id 
        WHERE pr.patient_id = %s 
        ORDER BY pr.created_at DESC LIMIT 5
    """, (session_data['patient_id'],)) or []

    for p in prescriptions:
        if isinstance(p.get('medicines'), str):
            try:
                p['medicines_parsed'] = json.loads(p['medicines'])
            except:
                p['medicines_parsed'] = []
        else:
            p['medicines_parsed'] = p.get('medicines', [])

    messages = query_db("""
        SELECT tm.*, u.full_name as sender_name, u.role as sender_role
        FROM teleconsult_messages tm
        LEFT JOIN users u ON tm.sender_id = u.id
        WHERE tm.session_id = %s
        ORDER BY tm.sent_at ASC
    """, (session_id,)) or []

    return render_template('phc/teleconsult_room.html', current_user=user, session=session_data,
                           patient_records=patient_records, prescriptions=prescriptions, messages=messages)


@phc_bp.route('/teleconsult/room/<int:session_id>/message', methods=['POST'])
@role_required(*ALLOWED_ROLES)
def send_teleconsult_message(session_id):
    user = get_current_user()
    data = request.get_json(silent=True) or request.form
    body = (data.get('body') or data.get('message') or '').strip()

    if not body:
        return jsonify({'ok': False, 'success': False, 'error': 'Message body cannot be empty'}), 400

    msg_id = execute_db("""
        INSERT INTO teleconsult_messages (session_id, sender_id, body)
        VALUES (%s, %s, %s)
    """, (session_id, user['id'], body))

    return jsonify({
        'ok': True,
        'success': True,
        'message': {
            'id': msg_id,
            'sender_id': user['id'],
            'sender_name': user.get('full_name') or user.get('username'),
            'sender_role': user.get('role'),
            'body': body,
            'sent_at': datetime.now().strftime('%H:%M')
        }
    })


@phc_bp.route('/teleconsult/room/<int:session_id>/messages')
@role_required(*ALLOWED_ROLES)
def get_teleconsult_messages(session_id):
    messages = query_db("""
        SELECT tm.*, u.full_name as sender_name, u.role as sender_role,
               DATE_FORMAT(tm.sent_at, '%%H:%%i') as time_formatted
        FROM teleconsult_messages tm
        LEFT JOIN users u ON tm.sender_id = u.id
        WHERE tm.session_id = %s
        ORDER BY tm.sent_at ASC
    """, (session_id,)) or []

    return jsonify({'ok': True, 'messages': messages})


@phc_bp.route('/teleconsult/room/<int:session_id>/complete', methods=['POST'])
@role_required(*ALLOWED_ROLES)
def complete_teleconsult(session_id):
    from utils.audit import log_audit
    user = get_current_user()
    session_data = query_db('SELECT * FROM teleconsult_sessions WHERE id = %s', (session_id,), one=True)
    if not session_data:
        flash('Session not found.', 'error')
        return redirect(url_for('phc.teleconsult'))

    clinical_summary = (request.form.get("final_summary") or request.form.get("summary") or "").strip()
    specialist_advice = (request.form.get("specialist_advice") or request.form.get("diagnosis") or "").strip()
    rx_notes = request.form.get("rx_notes", "").strip()
    meds_names = request.form.getlist("med_name[]")
    meds_dosages = request.form.getlist("med_dosage[]")
    meds_durations = request.form.getlist("med_duration[]")
    raw_meds = request.form.get("prescribe_medicines", "").strip()

    combined_summary = session_data.get("summary") or ""
    user_label = user.get('full_name') or user.get('username')
    advice_header = f"\n\n[COMPLETED CONSULTATION ADVICE by {user_label}]:\n{clinical_summary}\n{specialist_advice}"
    combined_summary += advice_header
    execute_db("""
        UPDATE teleconsult_sessions
        SET status = 'completed', ended_at = NOW(), summary = %s
        WHERE id = %s
    """, (combined_summary.strip(), session_id))

    meds_list = []
    for i in range(len(meds_names)):
        name = (meds_names[i] or "").strip()
        if name:
            meds_list.append({
                "name": name,
                "dosage": (meds_dosages[i] if i < len(meds_dosages) else "") or "1-0-1 after meals",
                "duration": (meds_durations[i] if i < len(meds_durations) else "") or "5 days"
            })

    if not meds_list and raw_meds:
        for line in raw_meds.splitlines():
            line = line.strip()
            if line:
                meds_list.append({
                    "name": line,
                    "dosage": "As directed",
                    "duration": "Course duration"
                })

    if meds_list:
        execute_db("""
            INSERT INTO prescriptions (patient_id, medicines, notes, prescribed_by, center_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (session_data["patient_id"], json.dumps(meds_list), rx_notes or f"Teleconsultation Specialist Prescription (Session #{session_id})", user["id"], session_data["center_id"]))
    record_data = {
        'teleconsult_session_id': session_id,
        'summary': clinical_summary,
        'specialist_advice': specialist_advice,
        'medicines_prescribed': meds_list
    }
    execute_db("""
        INSERT INTO medical_records (patient_id, record_type, title, data, center_id, created_by)
        VALUES (%s, 'consultation', %s, %s, %s, %s)
    """, (session_data['patient_id'], f'Specialist Teleconsultation (#{session_id})', json.dumps(record_data), session_data['center_id'], user['id']))

    log_audit('teleconsult_completed', 'teleconsult_session', session_id)
    flash(f'Teleconsultation session #{session_id} successfully concluded and clinical record saved.', 'success')
    return redirect(url_for('phc.teleconsult'))


@phc_bp.route('/prescriptions')
@phc_bp.route('/prescriptions/<patient_id>')
@role_required('doctor', 'nurse', 'system_admin')
def prescriptions(patient_id=None):
    if patient_id:
        return redirect(url_for('phc.consultation', patient_id=patient_id))
    return redirect(url_for('phc.consultation'))


@phc_bp.route('/inventory')
@role_required(*ALLOWED_ROLES)
def inventory():
    user = get_current_user()
    selected_center_id = request.args.get('center_id') or request.args.get('facility') or user.get('center_id') or 'FAC-BAKROL-01'
    search_q = request.args.get('q', '').strip()
    status_filter = request.args.get('status', '').strip()
    category_filter = request.args.get('category', '').strip()

    centers = query_db('SELECT id, name, type FROM centers ORDER BY name ASC') or []

    query = """
        SELECT i.*, c.name as center_name, c.type as center_type 
        FROM inventory_items i 
        LEFT JOIN centers c ON i.center_id = c.id 
        WHERE 1=1
    """
    params = []

    if selected_center_id and selected_center_id != 'all':
        query += " AND i.center_id = %s"
        params.append(selected_center_id)

    if search_q:
        query += " AND (i.item_name LIKE %s OR i.category LIKE %s)"
        params.extend([f"%{search_q}%", f"%{search_q}%"])

    if category_filter and category_filter != 'all':
        query += " AND i.category = %s"
        params.append(category_filter)

    query += " ORDER BY i.item_name ASC"
    items = query_db(query, tuple(params)) or []

    if status_filter == 'low':
        items = [item for item in items if item['quantity'] <= item['reorder_level']]
    elif status_filter == 'adequate':
        items = [item for item in items if item['quantity'] > item['reorder_level']]

    total_count = len(items)
    low_stock_count = sum(1 for item in items if item['quantity'] <= item['reorder_level'])
    
    categories = query_db('SELECT DISTINCT category FROM inventory_items WHERE category IS NOT NULL ORDER BY category ASC') or []
    categories = [c['category'] for c in categories if c.get('category')]

    current_center = next((c for c in centers if c['id'] == selected_center_id), None)

    return render_template('phc/inventory.html', 
                           current_user=user, 
                           inventory=items, 
                           centers=centers, 
                           selected_center_id=selected_center_id, 
                           current_center=current_center,
                           search_q=search_q,
                           status_filter=status_filter,
                           category_filter=category_filter,
                           categories=categories,
                           low_stock_count=low_stock_count,
                           total_count=total_count)



@phc_bp.route('/inventory/export')
@role_required(*ALLOWED_ROLES)
def export_inventory_csv():
    user = get_current_user()
    selected_center_id = request.args.get('center_id') or request.args.get('facility') or user.get('center_id') or 'FAC-BAKROL-01'
    search_q = request.args.get('q', '').strip()
    status_filter = request.args.get('status', '').strip()
    category_filter = request.args.get('category', '').strip()

    query = """
        SELECT i.*, c.name as center_name 
        FROM inventory_items i 
        LEFT JOIN centers c ON i.center_id = c.id 
        WHERE 1=1
    """
    params = []
    if selected_center_id and selected_center_id != 'all':
        query += " AND i.center_id = %s"
        params.append(selected_center_id)
    if search_q:
        query += " AND (i.item_name LIKE %s OR i.category LIKE %s)"
        params.extend([f"%{search_q}%", f"%{search_q}%"])
    if category_filter and category_filter != 'all':
        query += " AND i.category = %s"
        params.append(category_filter)
    query += " ORDER BY i.item_name ASC"
    
    items = query_db(query, tuple(params)) or []
    if status_filter == 'low':
        items = [it for it in items if it['quantity'] <= it['reorder_level']]
    elif status_filter == 'adequate':
        items = [it for it in items if it['quantity'] > it['reorder_level']]

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Center ID', 'Center Name', 'Item Name', 'Category', 'Quantity', 'Unit', 'Reorder Level', 'Expiry Date', 'Stock Status'])
    
    for it in items:
        status = 'Low Stock' if it['quantity'] <= it['reorder_level'] else 'Adequate'
        exp = it['expiry_date'].strftime('%Y-%m-%d') if it.get('expiry_date') and hasattr(it['expiry_date'], 'strftime') else (it.get('expiry_date') or '')
        writer.writerow([
            it['center_id'],
            it.get('center_name') or it['center_id'],
            it['item_name'],
            it.get('category') or 'General',
            it['quantity'],
            it.get('unit') or 'units',
            it.get('reorder_level') or 10,
            exp,
            status
        ])
        
    csv_data = output.getvalue()
    filename = f"inventory_export_{selected_center_id}.csv"
    return Response(csv_data, mimetype='text/csv', headers={'Content-Disposition': f'attachment; filename={filename}'})


@phc_bp.route('/inventory/import', methods=['POST'])
@role_required(*ALLOWED_ROLES)
def import_inventory_csv():
    user = get_current_user()
    if 'file' not in request.files:
        flash('No file part selected in upload.', 'danger')
        return redirect(url_for('phc.inventory'))
        
    file = request.files['file']
    if file.filename == '':
        flash('No file selected for upload.', 'danger')
        return redirect(url_for('phc.inventory'))
        
    if not file.filename.lower().endswith(('.csv', '.txt')):
        flash('Please upload a valid CSV file (.csv).', 'danger')
        return redirect(url_for('phc.inventory'))

    default_center_id = request.form.get('center_id') or user.get('center_id') or 'FAC-BAKROL-01'
    if default_center_id == 'all':
        default_center_id = user.get('center_id') or 'FAC-BAKROL-01'

    try:
        content_str = file.stream.read().decode('utf-8-sig', errors='replace')
        stream = io.StringIO(content_str, newline=None)
        reader = csv.reader(stream)
        
        headers = None
        imported_count = 0
        updated_count = 0
        
        for row in reader:
            if not row or not any(row):
                continue
            if headers is None:
                header_check = [c.lower().strip() for c in row]
                if any('item' in c or 'name' in c for c in header_check):
                    headers = header_check
                    continue
                else:
                    headers = ['center_id', 'item_name', 'category', 'quantity', 'unit', 'reorder_level', 'expiry_date']
            
            row_dict = {}
            for idx, val in enumerate(row):
                if idx < len(headers):
                    row_dict[headers[idx]] = val.strip()

            item_name = row_dict.get('item name') or row_dict.get('item_name') or row_dict.get('name') or (row[1] if len(row) > 1 else (row[0] if len(row) > 0 else ''))
            if not item_name or item_name.lower() in ('item name', 'item_name', 'name'):
                continue
                
            center_id = row_dict.get('center id') or row_dict.get('center_id') or row_dict.get('center') or (row[0] if len(row) > 0 and str(row[0]).startswith('FAC-') else default_center_id)
            if not center_id or not str(center_id).startswith('FAC-'):
                center_id = default_center_id
                
            category = row_dict.get('category') or (row[2] if len(row) > 2 else 'General')
            
            raw_qty = row_dict.get('quantity') or row_dict.get('qty') or (row[3] if len(row) > 3 else '0')
            try:
                quantity = int(float(raw_qty))
            except:
                quantity = 0
                
            unit = row_dict.get('unit') or (row[4] if len(row) > 4 else 'units')
            if not unit:
                unit = 'units'
                
            raw_reorder = row_dict.get('reorder level') or row_dict.get('reorder_level') or row_dict.get('reorder') or (row[5] if len(row) > 5 else '10')
            try:
                reorder_level = int(float(raw_reorder))
            except:
                reorder_level = 10
                
            expiry_date = row_dict.get('expiry date') or row_dict.get('expiry_date') or row_dict.get('expiry') or (row[6] if len(row) > 6 else None)
            if expiry_date and len(expiry_date) < 8:
                expiry_date = None

            existing = query_db('SELECT id, quantity FROM inventory_items WHERE center_id = %s AND item_name = %s', (center_id, item_name), one=True)
            if existing:
                execute_db('UPDATE inventory_items SET quantity = %s, category = %s, unit = %s, reorder_level = %s WHERE id = %s', 
                           (existing['quantity'] + quantity, category, unit, reorder_level, existing['id']))
                updated_count += 1
            else:
                execute_db('INSERT INTO inventory_items (center_id, item_name, category, quantity, unit, expiry_date, reorder_level) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                           (center_id, item_name, category, quantity, unit, expiry_date or None, reorder_level))
                imported_count += 1

        flash(f'CSV Import complete: {imported_count} new items added, {updated_count} existing items restocked.', 'success')
    except Exception as e:
        flash(f'Error importing CSV: {str(e)}', 'danger')

    return redirect(url_for('phc.inventory', center_id=default_center_id))


@phc_bp.route('/inventory/template')
@role_required(*ALLOWED_ROLES)
def download_inventory_template():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['center_id', 'item_name', 'category', 'quantity', 'unit', 'reorder_level', 'expiry_date'])
    writer.writerow(['FAC-BAKROL-01', 'Paracetamol 500mg Tablets', 'Analgesic', '500', 'tablets', '100', '2027-12-31'])
    writer.writerow(['FAC-BAKROL-01', 'Amoxicillin 250mg Capsules', 'Antibiotic', '250', 'capsules', '50', '2027-06-30'])
    writer.writerow(['FAC-002', 'Normal Saline 0.9% IV 500ml', 'IV Fluids', '100', 'bottles', '30', '2027-10-31'])
    
    return Response(output.getvalue(), mimetype='text/csv', headers={'Content-Disposition': 'attachment; filename=inventory_import_template.csv'})


@phc_bp.route('/referrals')
@role_required(*ALLOWED_ROLES)
def referrals():
    user = get_current_user()
    center_id = user.get('center_id') or 'FAC-BAKROL-01'
    is_admin = user.get('role') in ('system_admin', 'region_admin')

    status_filter = request.args.get('status', '').strip()
    type_filter = request.args.get('type', 'all').strip()
    urgency_filter = request.args.get('urgency', '').strip()

    query = """
        SELECT r.*, p.full_name as patient_name, p.gender, p.dob, p.blood_group,
               c_to.name as to_center_name, c_to.type as to_center_type,
               c_from.name as from_center_name, c_from.type as from_center_type,
               u.full_name as created_by_name, acc.full_name as accepted_by_name
        FROM referrals r
        LEFT JOIN patients p ON r.patient_id = p.id
        LEFT JOIN centers c_to ON r.to_center = c_to.id
        LEFT JOIN centers c_from ON r.from_center = c_from.id
        LEFT JOIN users u ON r.created_by = u.id
        LEFT JOIN users acc ON r.accepted_by = acc.id
        WHERE 1=1
    """
    params = []

    if not is_admin:
        if type_filter == 'outgoing':
            query += " AND r.from_center = %s"
            params.append(center_id)
        elif type_filter == 'incoming':
            query += " AND r.to_center = %s"
            params.append(center_id)
        else:
            query += " AND (r.from_center = %s OR r.to_center = %s)"
            params.extend([center_id, center_id])
    else:
        if type_filter == 'outgoing' and center_id:
            query += " AND r.from_center = %s"
            params.append(center_id)
        elif type_filter == 'incoming' and center_id:
            query += " AND r.to_center = %s"
            params.append(center_id)

    if status_filter:
        query += " AND r.status = %s"
        params.append(status_filter)

    if urgency_filter:
        query += " AND r.urgency = %s"
        params.append(urgency_filter)

    query += " ORDER BY CASE r.urgency WHEN 'critical' THEN 1 WHEN 'high' THEN 2 WHEN 'medium' THEN 3 ELSE 4 END, r.created_at DESC"

    referrals_list = query_db(query, tuple(params)) or []

    all_refs = query_db("""
        SELECT status, urgency, from_center, to_center
        FROM referrals
        WHERE from_center = %s OR to_center = %s
    """, (center_id, center_id)) if not is_admin else query_db("SELECT status, urgency, from_center, to_center FROM referrals") or []

    stats = {
        'total': len(all_refs),
        'active_transfers': len([r for r in all_refs if r['status'] in ('initiated', 'accepted', 'in_transit')]),
        'critical': len([r for r in all_refs if r['urgency'] == 'critical' and r['status'] in ('initiated', 'accepted', 'in_transit')]),
        'incoming': len([r for r in all_refs if r['to_center'] == center_id and r['status'] in ('initiated', 'accepted', 'in_transit')]),
        'outgoing': len([r for r in all_refs if r['from_center'] == center_id and r['status'] in ('initiated', 'accepted', 'in_transit')]),
        'completed': len([r for r in all_refs if r['status'] in ('completed', 'counter_referred')])
    }

    centers_list = query_db('SELECT id, name, type, region, address, phone FROM centers ORDER BY name ASC') or []
    patients_list = query_db('SELECT id, full_name, dob, gender, blood_group FROM patients ORDER BY full_name ASC') or []
    ambulances = query_db("SELECT id, driver_name, driver_phone, status, center_id FROM vehicles WHERE type = 'ambulance' ORDER BY status ASC") or []

    return render_template('phc/referrals.html', current_user=user, center_id=center_id, referrals=referrals_list,
                           centers_list=centers_list, patients_list=patients_list, ambulances=ambulances,
                           stats=stats, active_tab=type_filter, active_status=status_filter)


@phc_bp.route('/referrals/create', methods=['POST'])
@role_required(*ALLOWED_ROLES)
def create_referral():
    from utils.audit import log_audit
    user = get_current_user()
    from_center = user.get('center_id') or request.form.get('from_center') or 'FAC-BAKROL-01'

    patient_id = request.form.get('patient_id', '').strip()
    to_center = request.form.get('to_center', '').strip()
    urgency = request.form.get('urgency', 'medium').strip()
    reason = request.form.get('reason', '').strip()
    notes = request.form.get('notes', '').strip()
    specialist_dept = request.form.get('specialist_dept', '').strip()

    if not patient_id or not to_center or not reason:
        flash('Please select a patient, destination healthcare facility, and provide a clinical referral reason.', 'error')
        return redirect(url_for('phc.referrals'))

    if from_center == to_center:
        flash('Destination facility must be different from the originating facility.', 'error')
        return redirect(url_for('phc.referrals'))

    if specialist_dept:
        notes = f"[Required Specialty: {specialist_dept}]\n" + (notes or '')

    ref_id = execute_db("""
        INSERT INTO referrals (patient_id, from_center, to_center, urgency, status, reason, notes, created_by)
        VALUES (%s, %s, %s, %s, 'initiated', %s, %s, %s)
    """, (patient_id, from_center, to_center, urgency, reason, notes or None, user['id']))

    dest_users = query_db("SELECT id FROM users WHERE center_id = %s AND is_active = 1", (to_center,)) or []
    for du in dest_users:
        execute_db("""
            INSERT INTO notifications (user_id, title, body, link)
            VALUES (%s, %s, %s, %s)
        """, (du['id'], f'New {urgency.title()} Referral Transfer (REF-{ref_id})',
              f'Patient {patient_id} referred from {from_center}. Reason: {reason}',
              url_for('phc.referrals')))

    log_audit('referral_initiated', 'referral', ref_id)
    flash(f'Referral REF-{ref_id} successfully initiated for transfer to destination center.', 'success')
    return redirect(url_for('phc.referrals'))


@phc_bp.route('/referrals/<int:referral_id>/update-status', methods=['POST'])
@role_required(*ALLOWED_ROLES)
def update_referral_status(referral_id):
    from utils.audit import log_audit
    user = get_current_user()
    new_status = request.form.get('status', '').strip()
    transition_notes = request.form.get('notes', '').strip()
    vehicle_id = request.form.get('vehicle_id', '').strip()
    counter_advice = request.form.get('counter_advice', '').strip()

    referral = query_db('SELECT * FROM referrals WHERE id = %s', (referral_id,), one=True)
    if not referral:
        flash('Referral case not found.', 'error')
        return redirect(url_for('phc.referrals'))

    valid_statuses = ('initiated', 'accepted', 'in_transit', 'completed', 'counter_referred', 'rejected')
    if new_status not in valid_statuses:
        flash('Invalid referral status specified.', 'error')
        return redirect(url_for('phc.referrals'))

    appended_notes = referral.get('notes') or ''
    timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M')

    if vehicle_id:
        appended_notes += f"\n[{timestamp_str}] Ambulance Assigned: {vehicle_id}"
    if transition_notes:
        appended_notes += f"\n[{timestamp_str}] Status -> {new_status.replace('_', ' ').title()}: {transition_notes}"
    if counter_advice:
        appended_notes += f"\n[{timestamp_str}] Counter-Referral Advice: {counter_advice}"

    accepted_by = referral.get('accepted_by')
    if new_status == 'accepted' and not accepted_by:
        accepted_by = user['id']

    completed_at = referral.get('completed_at')
    if new_status in ('completed', 'counter_referred') and not completed_at:
        completed_at = datetime.now()

    execute_db("""
        UPDATE referrals 
        SET status = %s, notes = %s, accepted_by = %s, completed_at = %s 
        WHERE id = %s
    """, (new_status, appended_notes.strip(), accepted_by, completed_at, referral_id))

    if vehicle_id and new_status == 'in_transit':
        execute_db("UPDATE vehicles SET status = 'dispatched' WHERE id = %s", (vehicle_id,))

    origin_users = query_db("SELECT id FROM users WHERE center_id = %s AND is_active = 1", (referral['from_center'],)) or []
    for ou in origin_users:
        execute_db("""
            INSERT INTO notifications (user_id, title, body, link)
            VALUES (%s, %s, %s, %s)
        """, (ou['id'], f'Referral REF-{referral_id} Updated to {new_status.replace("_", " ").title()}',
              f'Status update recorded by {user.get("full_name") or user.get("username")}',
              url_for('phc.referrals')))

    log_audit('referral_status_updated', 'referral', referral_id)
    flash(f'Referral REF-{referral_id} status updated to {new_status.replace("_", " ").title()}.', 'success')
    return redirect(url_for('phc.referrals'))
