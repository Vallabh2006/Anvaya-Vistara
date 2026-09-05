# Rural Healthcare Platform
  
## 1. Project Overview

Integrated multi-tiered healthcare management platform for rural health networks, Primary Health Centres (PHCs), Community Health Centres (CHCs), Sub-Centres, and District Hospitals. It features triage priority OPD queue management, inter-hospital referral tracking with visual steppers, 2-step OTP password reset, patient medical records and inventory management..

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

## 4. Project Structure
```
Anvaya-Vistara/
│
├── app.py
├── config.py
├── schema.sql
├── full_setup.sql
├── reset_and_seed.py
├── create_admin.py
├── requirements.txt
├── README.md
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
│ ├── region/
│ └── shell.html
│
├── tests/
│ ├── test_appointment_queue_referrals.py
│ ├── test_email_masking_password_reset.py
│ ├── test_referrals_and_teleconsult.py
│ └── test_two_step_password_reset.py
│
├── translations/
│ ├── en.json
│ └── hi.json
│
└── utils/
├── __init__.py
├── audit.py
├── auth_helpers.py
├── db.py
├── email_helper.py
├── i18n.py
├── id_gen.py
└── permissions.py
```

## 5. Technology Stack

-  **Backend:** Python 3.x, Flask (Web Framework)
-  **Database:** MySQL (DictCursor)
-  **Frontend:** HTML, CSS, JavaScript (Jinja2 Templates)
-  **Authentication:** Sessions, bcrypt (Password Hashing), pyotp (2FA/OTP)

## 6. Database Recreation & Testing

-  **Recreate Complete Database:**

```bash
mysql -u root -p rural_health_db < full_setup.sql
```

## 7. Dependencies

The project relies on the following Python packages (defined in `requirements.txt`):

-  `Flask==3.1.1`: Core web framework.
-  `flask-mysqldb==2.0.0`: MySQL database integration.
-  `Flask-Session==0.8.0`: Server-side session management (filesystem-based).
-  `pyotp==2.9.0`: One-Time Password generation for 2FA.
-  `bcrypt==4.3.0`: Secure password hashing.
-  `python-dotenv==1.1.0`: Loading environment variables from `.env` files.
-  `qrcode==8.0` & `Pillow==11.2.1`: QR code generation and image processing.