import os
from flask import Flask, render_template, redirect, url_for, session, jsonify, request, flash
from flask_session import Session

from config import config_map
from utils.db import init_db, query_db
from utils.i18n import init_i18n
from utils.auth_helpers import get_current_user


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'default')

    app = Flask(__name__)
    app.config.from_object(config_map.get(config_name, config_map['default']))

    Session(app)
    init_db(app)
    init_i18n(app)

    from utils.email_helper import mask_email

    @app.template_filter('mask_email')
    def mask_email_filter(email):
        return mask_email(email)

    @app.template_filter('age')
    def calculate_age(dob):
        if not dob:
            return 'N/A'
        try:
            from datetime import date, datetime
            if isinstance(dob, str):
                for fmt in ('%Y-%m-%d', '%d-%m-%Y', '%Y/%m/%d', '%d/%m/%Y'):
                    try:
                        dob_date = datetime.strptime(dob, fmt).date()
                        break
                    except ValueError:
                        continue
                else:
                    return str(dob)
            elif isinstance(dob, datetime):
                dob_date = dob.date()
            elif isinstance(dob, date):
                dob_date = dob
            else:
                return str(dob)
                
            today = date.today()
            age_years = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
            return f"{age_years} yrs"
        except Exception:
            return str(dob)

    @app.context_processor
    def inject_user():
        from utils.permissions import has_permission, can
        user = None
        if 'user_id' in session:
            try:
                user = get_current_user()
            except Exception:
                pass
        return dict(current_user=user, has_permission=has_permission, can=can)

    from blueprints.auth import auth_bp
    from blueprints.phc import phc_bp
    from blueprints.region import region_bp
    from blueprints.admin import admin_bp
    from blueprints.patient import patient_bp
    from blueprints.center import center_bp
    from blueprints.api import api_bp
    from blueprints.dashboard import dashboard_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(phc_bp)
    app.register_blueprint(region_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(center_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(dashboard_bp)

    @app.route('/')
    def landing():
        if 'user_id' in session:
            return redirect(url_for('auth.app_redirect'))
        return render_template('landing.html')

    @app.route('/facilities')
    @app.route('/facilities/@<username>')
    def facilities_view(username=None):
        user = get_current_user()
        facilities = query_db('SELECT * FROM centers ORDER BY name ASC') or []
        for fac in facilities:
            if not fac.get('district'):
                fac['district'] = fac.get('region') or fac.get('state') or 'Main Center'
        return render_template('facilities/list.html', facilities=facilities, current_user=user)

    @app.route('/facilities/<facility_id>')
    @app.route('/patient/facilities/<facility_id>')
    @app.route('/patient/facilities/<facility_id>/@<username>')
    def facility_detail(facility_id, username=None):
        user = get_current_user()
        facility = query_db('SELECT * FROM centers WHERE id = %s', (facility_id,), one=True)
        if not facility:
            from flask import abort
            abort(404)
        if not facility.get('district'):
            facility['district'] = facility.get('region') or facility.get('state') or 'Main Center'
            
        staff_members = query_db('SELECT id, full_name, role, phone, email FROM users WHERE center_id = %s ORDER BY full_name ASC', (facility_id,)) or []
        inventory_items = query_db('SELECT * FROM inventory_items WHERE center_id = %s ORDER BY quantity ASC', (facility_id,)) or []
        pat_count_row = query_db('SELECT COUNT(*) as cnt FROM patients WHERE center_id = %s', (facility_id,), one=True)
        patient_count = pat_count_row['cnt'] if pat_count_row else 0
        
        return render_template('facilities/detail.html', facility=facility, facility_id=facility_id, current_user=user, staff_members=staff_members, inventory_items=inventory_items, patient_count=patient_count)

    @app.route('/inventory')
    def inventory_redirect():
        user = get_current_user()
        if not user:
            return redirect(url_for('auth.login'))
        if user.get('role') == 'system_admin':
            return redirect(url_for('admin.inventory'))
        elif user.get('role') == 'patient':
            return redirect(f'/patient/@{user.get("username")}')
        return redirect(url_for('phc.inventory'))

    @app.route('/user')
    def user_redirect():
        user = get_current_user()
        if not user:
            return redirect(url_for('auth.login'))
        if user.get('role') == 'patient':
            return redirect(f'/patient/@{user.get("username")}')
        return redirect('/patient/')

    @app.route('/map')
    def map_view():
        user = get_current_user()
        selected_facility_id = request.args.get('facility', '').strip()
        facilities = query_db('SELECT * FROM centers ORDER BY name ASC') or []
        for fac in facilities:
            if not fac.get('district'):
                fac['district'] = fac.get('region') or fac.get('state') or 'Main Region'
            if not fac.get('phone'):
                fac['phone'] = '+91 11 2345 6789'
        if user and user.get('username'):
            return redirect(f'/patient/map/@{user["username"]}?facility={selected_facility_id}' if selected_facility_id else f'/patient/map/@{user["username"]}') if user.get('role') == 'patient' else render_template('map.html', profile_username=user.get('username'), current_user=user, facilities=facilities, selected_facility_id=selected_facility_id)
        return render_template('map.html', profile_username=None, current_user=user, facilities=facilities, selected_facility_id=selected_facility_id)

    @app.route('/map/@<username>')
    def map_view_user(username):
        username = username.strip().lstrip('@')
        user = get_current_user()
        selected_facility_id = request.args.get('facility', '').strip()
        facilities = query_db('SELECT * FROM centers ORDER BY name ASC') or []
        for fac in facilities:
            if not fac.get('district'):
                fac['district'] = fac.get('region') or fac.get('state') or 'Main Region'
            if not fac.get('phone'):
                fac['phone'] = '+91 11 2345 6789'
        return render_template('map.html', profile_username=username, current_user=user, facilities=facilities, selected_facility_id=selected_facility_id)

    @app.route('/emergency')
    def emergency_view():
        user = get_current_user()
        if user and user.get('username'):
            return redirect(f'/emergency/@{user["username"]}')
        return render_template('emergency.html', current_user=user)

    @app.route('/emergency/@<username>')
    @app.route('/emergency-contact/@<username>')
    def emergency_view_user(username):
        username = username.strip().lstrip('@')
        user = get_current_user()
        target_user = query_db('SELECT * FROM users WHERE username = %s', (username,), one=True)
        patient = None
        if target_user:
            patient = query_db('SELECT * FROM patients WHERE linked_user_id = %s', (target_user['id'],), one=True)
        return render_template('emergency.html', profile_username=username, patient=patient, current_user=user, target_user=target_user)

    @app.route('/records/@<username>')
    @app.route('/medical-records/@<username>')
    def records_view_user(username):
        import json
        username = username.strip().lstrip('@')
        user = get_current_user()
        target_user = query_db('SELECT * FROM users WHERE username = %s', (username,), one=True)
        records = []
        patient = None
        appointments = []
        prescriptions = []
        if target_user:
            patient = query_db('SELECT * FROM patients WHERE linked_user_id = %s', (target_user['id'],), one=True)
            if not patient:
                patient = query_db('SELECT * FROM patients WHERE linked_user_id = %s', (target_user['id'],), one=True)
            if patient:
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
        return render_template('patient/my_records.html', current_user=user, profile_username=username, records=records, target_user=target_user, patient=patient, appointments=appointments, prescriptions=prescriptions)

    @app.route('/notifications/@<username>')
    def notifications_user(username):
        username = username.strip().lstrip('@')
        user = get_current_user()
        notifs = []
        if user:
            notifs = query_db('SELECT * FROM notifications WHERE user_id = %s ORDER BY created_at DESC LIMIT 50', (user['id'],)) or []
        return render_template('notifications.html', profile_username=username, notifications=notifs, current_user=user)

    @app.route('/notifications')
    def notifications():
        user = get_current_user()
        if user and user.get('username'):
            return redirect(f'/notifications/@{user["username"]}')
        return redirect(url_for('auth.login'))

    @app.route('/settings', methods=['GET', 'POST'])
    @app.route('/settings/@<username>', methods=['GET', 'POST'])
    def settings_view(username=None):
        import json
        import re
        import secrets
        import time
        import bcrypt
        from utils.audit import log_audit
        from utils.db import execute_db
        from utils.email_helper import send_email_change_otp
        
        user = get_current_user()
        if not user:
            return redirect(url_for('auth.login'))

        current_db_user = query_db('SELECT * FROM users WHERE id = %s', (user['id'],), one=True)
        if not current_db_user:
            return redirect(url_for('auth.logout'))

        patient = None
        facility = None
        if current_db_user.get('center_id'):
            facility = query_db('SELECT * FROM centers WHERE id = %s', (current_db_user['center_id'],), one=True)

        if current_db_user['role'] == 'patient':
            patient = query_db('SELECT * FROM patients WHERE linked_user_id = %s', (current_db_user['id'],), one=True)
            if not patient:
                from utils.id_generator import generate_patient_id
                pat_id = generate_patient_id()
                execute_db('INSERT INTO patients (id, linked_user_id, full_name, center_id, allergies) VALUES (%s, %s, %s, %s, %s)', 
                           (pat_id, current_db_user['id'], current_db_user['full_name'], current_db_user.get('center_id') or 'FAC-BAKROL-01', json.dumps(['Not Allergic'])))
                patient = query_db('SELECT * FROM patients WHERE linked_user_id = %s', (current_db_user['id'],), one=True)

        if request.method == 'POST':
            errors = []
            
            new_full_name = request.form.get('full_name', '').strip()
            new_username = request.form.get('username', '').strip()
            new_email = request.form.get('email', '').strip().lower()
            new_phone = request.form.get('phone', '').strip()
            new_lang = request.form.get('lang_pref', 'en').strip()
            new_designation = request.form.get('designation', '').strip()
            curr_pass = request.form.get('current_password', '')

            if not new_full_name:
                errors.append('Full Name / Display Name is required.')

            if not new_username:
                errors.append('Username is required.')
            elif not re.match(r'^[a-z0-9._]{3,30}$', new_username):
                errors.append('Username can only contain lowercase letters (a-z), numbers (0-9), dots (.), and underscores (_), and must be 3-30 characters long.')
            else:
                existing_user = query_db('SELECT id FROM users WHERE username = %s AND id != %s', (new_username, current_db_user['id']), one=True)
                if existing_user:
                    errors.append('Username is already taken by another user.')

            account_name_changed = (new_username != current_db_user['username']) or (new_full_name != current_db_user['full_name'])
            password_verified = False
            if curr_pass:
                if bcrypt.checkpw(curr_pass.encode('utf-8'), current_db_user['password_hash'].encode('utf-8')):
                    password_verified = True
                else:
                    errors.append('Current password entered is incorrect.')

            if account_name_changed and not password_verified and 'Current password entered is incorrect.' not in errors:
                errors.append('Your current password is required to change your username or display name.')

            email_changed = False
            curr_email = (current_db_user.get('email') or '').strip().lower()
            if new_email and new_email != curr_email:
                email_changed = True
                if not password_verified and 'Current password entered is incorrect.' not in errors:
                    errors.append('Your current password is required to update your email address.')

                if '@' not in new_email or '.' not in new_email:
                    errors.append('Please provide a valid email address.')
                else:
                    existing_email = query_db('SELECT id FROM users WHERE LOWER(email) = %s AND id != %s', (new_email, current_db_user['id']), one=True)
                    if existing_email:
                        errors.append('Email is already registered with another account.')

            new_pass = request.form.get('new_password', '')
            conf_pass = request.form.get('confirm_password', '')
            update_password = False

            if new_pass or conf_pass:
                if not password_verified and 'Current password entered is incorrect.' not in errors:
                    errors.append('Current password is required to set a new password.')
                elif not new_pass or len(new_pass) < 8:
                    errors.append('New password must be at least 8 characters long.')
                elif new_pass != conf_pass:
                    errors.append('New password and confirmation do not match.')
                elif password_verified:
                    update_password = True

            patient_address = request.form.get('address', '').strip()
            patient_dob = request.form.get('dob', '').strip() or None
            patient_gender = request.form.get('gender', 'Other')
            patient_blood_group = request.form.get('blood_group', '').strip()
            allergies_raw = request.form.get('allergies', '').strip()
            chronic_conditions_raw = request.form.get('chronic_conditions', '').strip()

            if errors:
                for err in errors:
                    flash(err, 'error')
            else:
                allergies_list = []
                if allergies_raw:
                    try:
                        if allergies_raw.startswith('[') and allergies_raw.endswith(']'):
                            parsed = json.loads(allergies_raw)
                            if isinstance(parsed, list):
                                allergies_list = [str(x).strip() for x in parsed if str(x).strip()]
                        else:
                            allergies_list = [x.strip() for x in allergies_raw.split(',') if x.strip()]
                    except Exception:
                        allergies_list = [x.strip() for x in allergies_raw.split(',') if x.strip()]
                
                if not allergies_list:
                    allergies_list = ['Not Allergic']

                conditions_list = []
                if chronic_conditions_raw:
                    try:
                        if chronic_conditions_raw.startswith('[') and chronic_conditions_raw.endswith(']'):
                            parsed_c = json.loads(chronic_conditions_raw)
                            if isinstance(parsed_c, list):
                                conditions_list = [str(x).strip() for x in parsed_c if str(x).strip()]
                        else:
                            conditions_list = [x.strip() for x in chronic_conditions_raw.split(',') if x.strip()]
                    except Exception:
                        conditions_list = [x.strip() for x in chronic_conditions_raw.split(',') if x.strip()]

                chronic_conditions_val = json.dumps(conditions_list) if conditions_list else None

                email_to_save = curr_email if email_changed else (new_email or None)

                execute_db('UPDATE users SET full_name = %s, username = %s, email = %s, phone = %s, lang_pref = %s, designation = %s WHERE id = %s',
                           (new_full_name, new_username, email_to_save, new_phone or None, new_lang, new_designation or None, current_db_user['id']))

                if update_password:
                    hashed = bcrypt.hashpw(new_pass.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    execute_db('UPDATE users SET password_hash = %s WHERE id = %s', (hashed, current_db_user['id']))
                    log_audit('password_changed_by_user', 'user', current_db_user['id'])

                if current_db_user['role'] == 'patient' and patient:
                    execute_db('UPDATE patients SET full_name = %s, phone = %s, address = %s, dob = %s, gender = %s, blood_group = %s, allergies = %s, chronic_conditions = %s WHERE id = %s',
                               (new_full_name, new_phone or None, patient_address or None, patient_dob, patient_gender, patient_blood_group or None,
                                json.dumps(allergies_list), chronic_conditions_val, patient['id']))

                session['username'] = new_username
                session['lang'] = new_lang

                log_audit('profile_updated', 'user', current_db_user['id'])

                if email_changed:
                    otp_code = str(secrets.randbelow(900000) + 100000)
                    session['pending_email_change'] = new_email
                    session['pending_email_otp'] = otp_code
                    session['pending_email_expires'] = time.time() + 600
                    send_email_change_otp(new_email, new_full_name, otp_code)
                    flash(f'Profile updated! A 6-digit verification code was sent to {new_email}. Please enter the code to finalize your new email address.', 'info')
                    return redirect('/settings/verify-email')

                flash('Your profile settings have been successfully updated!', 'success')
                return redirect(f'/settings/@{new_username}')

        if patient:
            raw_allergies = patient.get('allergies')
            if isinstance(raw_allergies, str):
                try:
                    parsed = json.loads(raw_allergies)
                    patient['allergies_list'] = parsed if isinstance(parsed, list) else [str(parsed)]
                except Exception:
                    patient['allergies_list'] = [raw_allergies] if raw_allergies else ['Not Allergic']
            elif isinstance(raw_allergies, list):
                patient['allergies_list'] = raw_allergies
            else:
                patient['allergies_list'] = ['Not Allergic']
                
            raw_conditions = patient.get('chronic_conditions')
            if isinstance(raw_conditions, str):
                try:
                    parsed = json.loads(raw_conditions)
                    patient['conditions_list'] = parsed if isinstance(parsed, list) else [str(parsed)]
                except Exception:
                    patient['conditions_list'] = [x.strip() for x in raw_conditions.split(',') if x.strip()]
            elif isinstance(raw_conditions, list):
                patient['conditions_list'] = raw_conditions
            else:
                patient['conditions_list'] = []

        pending_email = session.get('pending_email_change')
        return render_template('settings.html', current_user=current_db_user, profile_username=current_db_user['username'], patient=patient, facility=facility, pending_email=pending_email)

    @app.route('/settings/verify-email', methods=['GET', 'POST'])
    def settings_verify_email():
        import time
        from utils.audit import log_audit
        from utils.db import execute_db
        
        user = get_current_user()
        if not user:
            return redirect(url_for('auth.login'))

        pending_email = session.get('pending_email_change')
        if not pending_email:
            return redirect('/settings')

        if request.method == 'POST':
            entered_otp = request.form.get('otp', '').strip()
            expected_otp = session.get('pending_email_otp')
            expires_at = session.get('pending_email_expires', 0)

            if not expected_otp or time.time() > expires_at:
                flash('The verification code has expired. Please request a new code.', 'error')
                return render_template('verify_email_change.html', current_user=user, pending_email=pending_email)

            if entered_otp != expected_otp:
                flash('Incorrect 6-digit verification code. Please try again.', 'error')
                return render_template('verify_email_change.html', current_user=user, pending_email=pending_email)

            execute_db('UPDATE users SET email = %s WHERE id = %s', (pending_email, user['id']))
            session.pop('pending_email_change', None)
            session.pop('pending_email_otp', None)
            session.pop('pending_email_expires', None)

            log_audit('email_change_verified', 'user', user['id'])
            flash(f'Your email address has been successfully verified and updated to {pending_email}!', 'success')
            return redirect('/settings')

        return render_template('verify_email_change.html', current_user=user, pending_email=pending_email)

    @app.route('/settings/resend-email-otp', methods=['POST'])
    def settings_resend_email_otp():
        import secrets
        import time
        from utils.email_helper import send_email_change_otp

        user = get_current_user()
        if not user:
            return redirect(url_for('auth.login'))

        pending_email = session.get('pending_email_change')
        if not pending_email:
            flash('No pending email verification found.', 'error')
            return redirect('/settings')

        otp_code = str(secrets.randbelow(900000) + 100000)
        session['pending_email_otp'] = otp_code
        session['pending_email_expires'] = time.time() + 600

        send_email_change_otp(pending_email, user.get('full_name') or user.get('username'), otp_code)
        flash(f'A fresh 6-digit verification code has been dispatched to {pending_email}.', 'info')
        return redirect('/settings/verify-email')

    @app.route('/settings/cancel-email-change', methods=['POST'])
    def settings_cancel_email_change():
        session.pop('pending_email_change', None)
        session.pop('pending_email_otp', None)
        session.pop('pending_email_expires', None)
        flash('Email address update request has been cancelled.', 'info')
        return redirect('/settings')

    @app.route('/api/time')
    def server_world_time():
        import time
        from datetime import datetime
        now = datetime.now()
        return jsonify({
            'ok': True,
            'epoch_ms': int(time.time() * 1000),
            'iso': now.isoformat(),
            'timezone': 'Asia/Kolkata (IST)',
            'formatted': now.strftime('%b %d, %Y - %I:%M:%S %p'),
            'date': now.strftime('%Y-%m-%d'),
            'time': now.strftime('%H:%M')
        })

    @app.route('/api/auth/set-lang', methods=['POST'])
    def set_lang():
        data = request.get_json(silent=True) or {}
        lang = data.get('lang', 'en')
        session['lang'] = lang

        if 'user_id' in session:
            try:
                from utils.db import execute_db
                execute_db('UPDATE users SET lang_pref = %s WHERE id = %s', (lang, session['user_id']))
            except Exception:
                pass
        resp = jsonify({'ok': True, 'lang': lang})
        resp.set_cookie('lang', lang, max_age=365*24*3600)
        return resp

    @app.errorhandler(404)
    def not_found(e):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Not found'}), 404
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden(e):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Forbidden'}), 403
        return render_template('errors/403.html'), 403

    @app.errorhandler(500)
    def server_error(e):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Internal server error'}), 500
        return render_template('errors/500.html'), 500

    return app


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=port)
