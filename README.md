
# Rural Healthcare Platform

## 1. Project Overview

The Rural Healthcare Platform is a web-based application designed to streamline and manage healthcare services across various levels, from local ASHA workers to Primary Health Centres (PHCs) and District Hospitals. It features role-based access to provide specific tools for different healthcare providers and administrators.


## 2. Available Routes & Specifications
 
### I) ASHA Worker (`/asha` prefix)

Tools and views for ASHA (Accredited Social Health Activist) workers.

-  `/asha/dashboard` - Main overview for the ASHA worker.
-  `/asha/triage` - Initial patient assessment and triage.
-  `/asha/visits` - Track and log patient visits.
-  `/asha/follow-ups` - Manage follow-up appointments.
-  `/asha/referrals` - Referrals made by the ASHA worker.
-  `/asha/patients` - List of patients under the ASHA worker's care.

  

###  II) Primary Health Centre - PHC (`/phc` prefix)

Management and operations for Primary Health Centres.

-  `/phc/dashboard` - Main overview for PHC staff.
-  `/phc/queue` - Patient queue management.
-  `/phc/consultation` - Ongoing consultations.
-  `/phc/teleconsult` - Teleconsultation services.
-  `/phc/prescriptions` - Prescription management.
-  `/phc/inventory` - PHC medical inventory.
-  `/phc/referrals` - Incoming and outgoing referrals at the PHC level.

  

### III) District Hospital (`/district` prefix)

Higher-level care management for District Hospitals.

-  `/district/dashboard` - District hospital overview.
-  `/district/referrals` - Manage incoming referrals from PHCs.
-  `/district/admissions` - Patient admissions tracking.
-  `/district/discharges` - Patient discharges.
-  `/district/counter-referrals` - Referrals sent back to PHCs/ASHAs for follow-up.

### IV) Administration (`/admin` prefix)

System administration and oversight.

-  `/admin/dashboard` - Administrator dashboard.
-  `/admin/analytics` - System analytics and metrics.
-  `/admin/surveillance` - Health surveillance data.
-  `/admin/facilities` - Manage healthcare facilities.
-  `/admin/inventory` - Global inventory overview.
-  `/admin/reports` - Generate system reports.
-  `/admin/users` - User management.
-  `/admin/audit-logs` - System audit logs for security and compliance.

### V) Patients (`/patients` prefix)

-  `/patients/` - Patient directory/list.
-  `/patients/me` - Logged-in patient's profile.
-  `/patients/<patient_id>` - Specific patient profile.

### VI) Facilities (`/facilities` prefix)

-  `/facilities/` - Directory of all facilities.
-  `/facilities/<facility_id>` - Specific facility details.

## 3. Configuration & Environment

Environment variables are loaded via `python-dotenv`. An `.env.example` is provided, and active configuration is expected in `.env`.

Key Configurations:

-  **Database (MySQL):**  `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DB`
-  **Security:**  `SECRET_KEY`

## 4. Project Structure

```
SetuHealth/
│
├── app.py 
├── config.py
├── schema.sql
├── requirements.txt
├── README.md
│
├── blueprints/
│   ├── admin/
│   ├── api/
│   ├── asha/
│   ├── auth/
│   ├── dashboard/
│   ├── facilities/
│   ├── phc/
│   ├── region/
│   └── user/
│
├── static/
│   ├── css/
│   └── js/
│
├── templates/
│   ├── base.html
│   ├── admin/
│   ├── api/
│   ├── asha/
│   ├── auth/
│   ├── dashboard/
│   ├── errors/
│   ├── facilities/
│   ├── phc/
│   ├── region/
│   └── user/
│
├── translations/
│
└── utils/
    ├── __init__.py
    ├── audit.py
    ├── auth_helpers.py
    ├── db.py
    ├── i18n.py
    └── id_gen.py
```
  

## 5. Technology Stack

-  **Backend:** Python 3.x, Flask (Web Framework)

-  **Database:** MySQL

-  **Frontend:** HTML, CSS, JavaScript (Jinja2 Templates)

-  **Authentication:** Sessions, bcrypt (Password Hashing), pyotp (2FA/OTP)

## 6. Dependencies

The project relies on the following Python packages (defined in `requirements.txt`):

-  `Flask==3.1.1`: Core web framework.

-  `flask-mysqldb==2.0.0`: MySQL database integration.

-  `Flask-Session==0.8.0`: Server-side session management (filesystem-based).

-  `pyotp==2.9.0`: One-Time Password generation for 2FA.

-  `bcrypt==4.3.0`: Secure password hashing.

-  `python-dotenv==1.1.0`: Loading environment variables from `.env` files.

-  `qrcode==8.0` & `Pillow==11.2.1`: QR code generation and image processing (likely for patient IDs or facility codes).