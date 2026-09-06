
# Rural Healthcare Platform
  
## 1. Project Overview

Anvaya Vistara is an integrated multi-tiered healthcare management platform designed for rural health networks, Primary Health Centres (PHCs), Community Health Centres (CHCs), Sub-Centres, and District Hospitals. It streamlines patient registration, triage queue management, inter-hospital referral tracking, inventory control, electronic health records (EHR), and two-step authentication recovery.

### Key Features
-  **OPD Queue & Token Management**: Triage priority token generation (OPD-001, EMG-001, REF-001), queue status progression (scheduled -> checked_in -> in_progress -> completed / no_show), live public display board polling, and patient estimated wait time calculations.
-  **Inter-Hospital Referral Tracking**: Visual 5-stage referral transfer stepper and 1-click priority destination queue auto-enqueue between PHCs, CHCs, and District Hospitals.
-  **2-Step Password Reset & Privacy**: Masked email privacy protection (e.g. va*************a@g***l.com) and mandatory 2-step OTP verification before new password creation.
-  **Teleconsultation Feature Roadmap**: Modern glassmorphic Coming Soon feature pages for PHC clinical staff and patient portals.
-  **Time Sync & Validation**: Server-side world clock verification endpoint (/api/time) and past slot booking prevention.
-  **Database Recreation Script**: Standalone SQL database creation and seeding script (full_setup.sql) with RBAC permissions and default health facilities.

## 2. Available Routes & Specifications

### I) Authentication & Account Recovery (`/` prefix)

-  `/login` - Role-aware sign-in for staff, doctors, and patients.
-  `/forgot-password` - Account recovery request with email privacy masking.
-  `/reset-password` - Step 1 OTP code verification & Step 2 password update.
-  `/logout` - Secure session clearance and audit log record.
 
### II) Primary Health Centre - PHC (`/phc` prefix) 

Management and operations for Primary Health Centres.

-  `/phc/dashboard` - Main overview for PHC Medical Officers and staff.
-  `/phc/queue` - Live triage priority queue & token management.
-  `/phc/queue/display` - Public OPD queue display board.
-  `/phc/consultation` - Clinical consultation, vitals & EHR prescription notes.
-  `/phc/teleconsult` - Virtual teleconsultation coming soon roadmap.
-  `/phc/prescriptions` - Pharmacy prescription dispatch.
-  `/phc/inventory` - PHC medical inventory and vaccine stock control.
-  `/phc/referrals` - Incoming and outgoing inter-hospital referrals.

### III) Regional & District Hospital (`/region` prefix)

Higher-level care management for Regional and District Hospitals.
  
-  `/region/dashboard` - District hospital operational overview.
-  `/region/referrals` - Manage incoming referrals from PHCs and 1-click queue enqueue.
-  `/region/counter_referrals` - Specialist counter-referral guidance.
-  `/region/admissions` - Patient ward admissions tracking.
-  `/region/discharges` - Patient discharge summaries.

### IV) Administration (`/admin` prefix)

System administration and oversight.

-  `/admin/dashboard` - Administrator system dashboard.
-  `/admin/analytics` - System analytics and epidemiological metrics.
-  `/admin/surveillance` - Health outbreak surveillance data.
-  `/admin/facilities` - Manage healthcare facility directory and resources.
-  `/admin/inventory` - Global medical supply inventory overview.
-  `/admin/reports` - Generate health network reports.
-  `/admin/users` - Staff and patient account management.
-  `/admin/permissions` - Role-based access control (RBAC) configuration.
-  `/admin/audit-logs` - System audit logs for security and compliance.

### V) Patients (`/patient` prefix)  

-  `/patient/appointments` - Online OPD booking and live queue position tracker.
-  `/patient/my_records` - Personal medical history, prescriptions, and lab reports.
-  `/patient/teleconsult` - Virtual care coming soon preview.

### VI) Facilities (`/facilities` prefix)

-  `/facilities/` - Directory of all regional facilities.
-  `/facilities/<facility_id>` - Specific facility details and capacity.
-  `/map` - Regional interactive healthcare facility map.

## 3. Configuration & Environment

Environment variables are loaded via `python-dotenv`. Active configuration is expected in `.env`.

Key Configurations:
-  **Database (MySQL):**  `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DB`
-  **Security:**  `SECRET_KEY`, `SESSION_TYPE`
-  **Email**: `ZOHO_EMAIL`, `ZOHO_PASSWORD`

## 4. Project Structure
```
Anvaya-Vistara/
│
├── .env
├── .env.example
├── app.py
├── config.py
├── create_admin.py
├── requirements.txt
├── README.md
├── sample.sql
│
├── blueprints/
│ ├── admin/
│ ├── api/
│ ├── auth/
│ ├── center/
│ ├── dashboard/
│ ├── patient/
│ ├── phc/
│ └── region/
│
├── static/
│ ├── js/
│ │ └── main.js
│ └── styles.css
│
├── templates/
│ ├── admin/
│ ├── auth/
│ ├── center/
│ ├── dashboard/
│ ├── errors/
│ ├── facilities/
│ ├── patient/
│ ├── phc/
│ └── region/
│
├── translations/
│ ├── en.json
│ └── hi.json
│
└── utils/
├── __init__.py
├── audit.py
├── auth_helpers.py
├── constants.py
├── db.py
├── defaults.py
├── email_helper.py
├── i18n.py
├── id_gen.py
├── id_generator.py
├── notifications.py
├── permissions.py
├── sanitize.py
└── permissions.py
```

## 5. Technology Stack

-  **Backend**: Python 3.x, Flask
-  **Database**: MySQL (DictCursor)
-  **Frontend**: HTML5, Vanilla CSS3, JavaScript
-  **Authentication & Security**: Flask-Session, bcrypt, pyotp

## 6. Database Recreation & Testing

-  **Recreate Complete Database:**

```bash
mysql -u root -p rural_health_db < sample.sql
```

-  **Run Automated Test Suite:**

## 7. Dependencies

The project relies on the following Python packages (defined in `requirements.txt`):

-  `Flask==3.1.1`: Core web framework.
-  `flask-mysqldb==2.0.0`: MySQL database integration.
-  `Flask-Session==0.8.0`: Server-side session management (filesystem-based).
-  `pyotp==2.9.0`: One-Time Password generation for 2FA.
-  `bcrypt==4.3.0`: Secure password hashing.
-  `python-dotenv==1.1.0`: Loading environment variables from `.env` files.
-  `qrcode==8.0` & `Pillow==11.2.1`: QR code generation and image processing.
