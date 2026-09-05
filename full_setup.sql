
CREATE DATABASE IF NOT EXISTS rural_health_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE rural_health_db;

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS audit_logs;
DROP TABLE IF EXISTS notifications;
DROP TABLE IF EXISTS vehicles;
DROP TABLE IF EXISTS teleconsult_messages;
DROP TABLE IF EXISTS teleconsult_sessions;
DROP TABLE IF EXISTS follow_ups;
DROP TABLE IF EXISTS referrals;
DROP TABLE IF EXISTS triage_entries;
DROP TABLE IF EXISTS inventory_items;
DROP TABLE IF EXISTS lab_records;
DROP TABLE IF EXISTS prescriptions;
DROP TABLE IF EXISTS medical_records;
DROP TABLE IF EXISTS appointments;
DROP TABLE IF EXISTS role_permissions;
DROP TABLE IF EXISTS patients;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS centers;

CREATE TABLE centers (
    id            VARCHAR(30)  PRIMARY KEY,
    name          VARCHAR(200) NOT NULL,
    type          ENUM('PHC','CHC','DH','Dispensary','SubCentre') NOT NULL,
    region        VARCHAR(100) NOT NULL,
    state         VARCHAR(100) NOT NULL DEFAULT '',
    address       TEXT,
    lat           DECIMAL(10,7),
    lng           DECIMAL(10,7),
    phone         VARCHAR(20),
    resources     JSON,
    is_active     TINYINT(1)   NOT NULL DEFAULT 1,
    created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_center_type (type),
    INDEX idx_center_region (region)
) ENGINE=InnoDB;

CREATE TABLE users (
    id            INT          AUTO_INCREMENT PRIMARY KEY,
    staff_id      VARCHAR(30)  UNIQUE,
    username      VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name     VARCHAR(200) NOT NULL,
    role          VARCHAR(50)  NOT NULL,
    center_id     VARCHAR(30),
    phone         VARCHAR(20),
    email         VARCHAR(200),
    totp_secret   VARCHAR(64),
    is_active     TINYINT(1)   NOT NULL DEFAULT 1,
    lang_pref     VARCHAR(10)  NOT NULL DEFAULT 'en',
    invite_status VARCHAR(30)  NOT NULL DEFAULT 'active',
    invite_token  VARCHAR(100),
    designation   VARCHAR(100),
    created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (center_id) REFERENCES centers(id) ON DELETE SET NULL,
    INDEX idx_user_role (role),
    INDEX idx_user_center (center_id)
) ENGINE=InnoDB;

CREATE TABLE patients (
    id                 VARCHAR(30)  PRIMARY KEY,
    linked_user_id     INT          UNIQUE,
    full_name          VARCHAR(200) NOT NULL,
    dob                DATE,
    gender             ENUM('M','F','Other') NOT NULL DEFAULT 'Other',
    phone              VARCHAR(20),
    address            TEXT,
    aadhaar_hash       VARCHAR(64),
    blood_group        VARCHAR(20),
    allergies          JSON,
    chronic_conditions JSON,
    center_id          VARCHAR(30),
    is_high_risk       TINYINT(1)   NOT NULL DEFAULT 0,
    created_at         DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at         DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (linked_user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (center_id)      REFERENCES centers(id) ON DELETE SET NULL,
    INDEX idx_patient_name (full_name),
    INDEX idx_patient_center (center_id)
) ENGINE=InnoDB;

CREATE TABLE role_permissions (
    role       VARCHAR(50)  NOT NULL,
    action     VARCHAR(100) NOT NULL,
    is_allowed TINYINT(1)   NOT NULL DEFAULT 1,
    PRIMARY KEY (role, action)
) ENGINE=InnoDB;

CREATE TABLE appointments (
    id            INT          AUTO_INCREMENT PRIMARY KEY,
    patient_id    VARCHAR(30)  NOT NULL,
    center_id     VARCHAR(30)  NOT NULL,
    doctor_id     INT,
    token_number  VARCHAR(30),
    department    VARCHAR(100),
    referral_id   INT,
    slot_time     DATETIME     NOT NULL,
    end_time      DATETIME,
    reason        VARCHAR(500),
    urgency       TINYINT      NOT NULL DEFAULT 3,
    status        ENUM('scheduled','checked_in','in_progress','completed','cancelled','no_show') NOT NULL DEFAULT 'scheduled',
    notes         TEXT,
    created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id)  REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY (center_id)   REFERENCES centers(id)  ON DELETE CASCADE,
    FOREIGN KEY (doctor_id)   REFERENCES users(id)    ON DELETE SET NULL,
    INDEX idx_appt_center_date (center_id, slot_time),
    INDEX idx_appt_patient (patient_id)
) ENGINE=InnoDB;

CREATE TABLE medical_records (
    id            INT          AUTO_INCREMENT PRIMARY KEY,
    patient_id    VARCHAR(30)  NOT NULL,
    record_type   ENUM('consultation','lab','imaging','note','discharge_summary') NOT NULL,
    title         VARCHAR(200),
    data          JSON         NOT NULL,
    center_id     VARCHAR(30)  NOT NULL,
    created_by    INT          NOT NULL,
    created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id)  REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY (center_id)   REFERENCES centers(id)  ON DELETE CASCADE,
    FOREIGN KEY (created_by)  REFERENCES users(id)    ON DELETE CASCADE,
    INDEX idx_mr_patient (patient_id),
    INDEX idx_mr_center (center_id)
) ENGINE=InnoDB;

CREATE TABLE prescriptions (
    id            INT          AUTO_INCREMENT PRIMARY KEY,
    record_id     INT,
    patient_id    VARCHAR(30)  NOT NULL,
    medicines     JSON         NOT NULL,
    notes         TEXT,
    prescribed_by INT          NOT NULL,
    center_id     VARCHAR(30)  NOT NULL,
    created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (record_id)     REFERENCES medical_records(id) ON DELETE SET NULL,
    FOREIGN KEY (patient_id)    REFERENCES patients(id)        ON DELETE CASCADE,
    FOREIGN KEY (prescribed_by) REFERENCES users(id)           ON DELETE CASCADE,
    FOREIGN KEY (center_id)     REFERENCES centers(id)         ON DELETE CASCADE,
    INDEX idx_rx_patient (patient_id),
    INDEX idx_rx_center (center_id)
) ENGINE=InnoDB;

CREATE TABLE lab_records (
    id            INT          AUTO_INCREMENT PRIMARY KEY,
    patient_id    VARCHAR(30)  NOT NULL,
    test_name     VARCHAR(200) NOT NULL,
    test_category VARCHAR(100),
    result        TEXT,
    result_data   JSON,
    status        ENUM('ordered','sample_collected','processing','resulted','cancelled') NOT NULL DEFAULT 'ordered',
    center_id     VARCHAR(30)  NOT NULL,
    ordered_by    INT          NOT NULL,
    resulted_at   DATETIME,
    created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id)  REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY (center_id)   REFERENCES centers(id)  ON DELETE CASCADE,
    FOREIGN KEY (ordered_by)  REFERENCES users(id)    ON DELETE CASCADE,
    INDEX idx_lab_patient (patient_id),
    INDEX idx_lab_status (status)
) ENGINE=InnoDB;

CREATE TABLE inventory_items (
    id            INT          AUTO_INCREMENT PRIMARY KEY,
    center_id     VARCHAR(30)  NOT NULL,
    item_name     VARCHAR(200) NOT NULL,
    category      VARCHAR(100),
    quantity      INT          NOT NULL DEFAULT 0,
    unit          VARCHAR(30)  NOT NULL DEFAULT 'units',
    expiry_date   DATE,
    reorder_level INT          NOT NULL DEFAULT 10,
    created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (center_id) REFERENCES centers(id) ON DELETE CASCADE,
    INDEX idx_inv_center (center_id),
    INDEX idx_inv_expiry (expiry_date)
) ENGINE=InnoDB;

CREATE TABLE triage_entries (
    id              INT          AUTO_INCREMENT PRIMARY KEY,
    patient_id      VARCHAR(30)  NOT NULL,
    center_id       VARCHAR(30)  NOT NULL,
    assessed_by     INT          NOT NULL,
    urgency_score   TINYINT      NOT NULL,
    symptoms        JSON         NOT NULL,
    vitals          JSON,
    recommendation  TEXT,
    created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id)  REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY (center_id)   REFERENCES centers(id)  ON DELETE CASCADE,
    FOREIGN KEY (assessed_by) REFERENCES users(id)    ON DELETE CASCADE,
    INDEX idx_tri_center (center_id),
    INDEX idx_tri_urgency (urgency_score)
) ENGINE=InnoDB;

CREATE TABLE referrals (
    id              INT          AUTO_INCREMENT PRIMARY KEY,
    patient_id      VARCHAR(30)  NOT NULL,
    from_center     VARCHAR(30)  NOT NULL,
    to_center       VARCHAR(30)  NOT NULL,
    urgency         ENUM('critical','high','medium','low') NOT NULL DEFAULT 'medium',
    status          ENUM('initiated','accepted','in_transit','completed','counter_referred','rejected') NOT NULL DEFAULT 'initiated',
    reason          TEXT,
    notes           TEXT,
    created_by      INT          NOT NULL,
    accepted_by     INT,
    completed_at    DATETIME,
    created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id)  REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY (from_center) REFERENCES centers(id)  ON DELETE CASCADE,
    FOREIGN KEY (to_center)   REFERENCES centers(id)  ON DELETE CASCADE,
    FOREIGN KEY (created_by)  REFERENCES users(id)    ON DELETE CASCADE,
    FOREIGN KEY (accepted_by) REFERENCES users(id)    ON DELETE SET NULL,
    INDEX idx_ref_from (from_center),
    INDEX idx_ref_to (to_center),
    INDEX idx_ref_status (status)
) ENGINE=InnoDB;

CREATE TABLE follow_ups (
    id            INT          AUTO_INCREMENT PRIMARY KEY,
    patient_id    VARCHAR(30)  NOT NULL,
    category      ENUM('maternal','child','chronic','high_risk','general','post_referral') NOT NULL,
    due_date      DATE         NOT NULL,
    status        ENUM('pending','completed','missed','rescheduled') NOT NULL DEFAULT 'pending',
    assigned_to   INT,
    notes         TEXT,
    completed_at  DATETIME,
    created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id)  REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_to) REFERENCES users(id)    ON DELETE SET NULL,
    INDEX idx_fu_due (due_date, status),
    INDEX idx_fu_assigned (assigned_to)
) ENGINE=InnoDB;

CREATE TABLE teleconsult_sessions (
    id            INT          AUTO_INCREMENT PRIMARY KEY,
    patient_id    VARCHAR(30)  NOT NULL,
    doctor_id     INT          NOT NULL,
    center_id     VARCHAR(30)  NOT NULL,
    status        ENUM('requested','active','completed','cancelled') NOT NULL DEFAULT 'requested',
    summary       TEXT,
    started_at    DATETIME,
    ended_at      DATETIME,
    created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id)  REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id)   REFERENCES users(id)    ON DELETE CASCADE,
    FOREIGN KEY (center_id)   REFERENCES centers(id)  ON DELETE CASCADE,
    INDEX idx_tc_doctor (doctor_id),
    INDEX idx_tc_status (status)
) ENGINE=InnoDB;

CREATE TABLE teleconsult_messages (
    id              INT          AUTO_INCREMENT PRIMARY KEY,
    session_id      INT          NOT NULL,
    sender_id       INT          NOT NULL,
    body            TEXT         NOT NULL,
    sent_at         DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES teleconsult_sessions(id) ON DELETE CASCADE,
    FOREIGN KEY (sender_id)  REFERENCES users(id)                ON DELETE CASCADE,
    INDEX idx_tcm_session (session_id, sent_at)
) ENGINE=InnoDB;

CREATE TABLE vehicles (
    id            VARCHAR(30)  PRIMARY KEY,
    type          VARCHAR(50)  NOT NULL DEFAULT 'ambulance',
    region        VARCHAR(100) NOT NULL,
    status        ENUM('available','dispatched','en_route','at_scene','returning','maintenance') NOT NULL DEFAULT 'available',
    center_id     VARCHAR(30),
    driver_name   VARCHAR(200),
    driver_phone  VARCHAR(20),
    lat           DECIMAL(10,7),
    lng           DECIMAL(10,7),
    updated_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (center_id) REFERENCES centers(id) ON DELETE SET NULL,
    INDEX idx_veh_status (status),
    INDEX idx_veh_region (region)
) ENGINE=InnoDB;

CREATE TABLE notifications (
    id            INT          AUTO_INCREMENT PRIMARY KEY,
    user_id       INT          NOT NULL,
    title         VARCHAR(300) NOT NULL,
    body          TEXT,
    link          VARCHAR(500),
    is_read       TINYINT(1)   NOT NULL DEFAULT 0,
    created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_notif_user_read (user_id, is_read)
) ENGINE=InnoDB;

CREATE TABLE audit_logs (
    id            BIGINT       AUTO_INCREMENT PRIMARY KEY,
    user_id       INT,
    action        VARCHAR(100) NOT NULL,
    entity_type   VARCHAR(50),
    entity_id     VARCHAR(50),
    detail        JSON,
    ip_address    VARCHAR(45),
    created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_audit_user (user_id),
    INDEX idx_audit_entity (entity_type, entity_id),
    INDEX idx_audit_time (created_at)
) ENGINE=InnoDB;


INSERT INTO centers (id, name, type, region, state, address, lat, lng, phone, resources, is_active) VALUES
('FAC-BAKROL-01', 'Primary Health Centre (PHC) Bakrol', 'PHC', 'Vallabh Vidyanagar', 'Gujarat', 'Near Bakrol Gate, Bakrol-Vadtal Road, Bakrol, Vallabh Vidyanagar 388315', 22.5488200, 72.9372100, '+91 2692 236104', '{"beds": 12, "ambulance": 1, "oxygen": 8, "opd_daily": 140, "timings": "24x7 Emergency / OPD 9AM - 5PM"}', 1),
('FAC-SKH-02', 'Shree Krishna Hospital & Bhaikaka Medical Centre', 'DH', 'Karamsad', 'Gujarat', 'Gokal Nagar, Karamsad - Vidyanagar Road, Anand 388325', 22.5471400, 72.8986500, '+91 2692 228411', '{"beds": 550, "icu_beds": 60, "ambulance": 6, "blood_bank": true, "specialities": ["Cardiology", "Trauma", "Pediatrics", "Oncology"]}', 1),
('FAC-KARAMSAD-03', 'Community Health Centre (CHC) Karamsad', 'CHC', 'Karamsad', 'Gujarat', 'Karamsad Main Road, Near Sardar Patel Memorial, Karamsad 388325', 22.5495100, 72.9052300, '+91 2692 222108', '{"beds": 30, "ambulance": 2, "maternity_ward": true, "lab": true}', 1),
('FAC-VVN-04', 'Vidyanagar Municipal Dispensary & Health Post', 'Dispensary', 'Vallabh Vidyanagar', 'Gujarat', 'Mota Bazaar, Near Shastri Maidan, Vallabh Vidyanagar 388120', 22.5530100, 72.9240300, '+91 2692 230457', '{"opd_rooms": 3, "pharmacy": true, "vaccination": true, "timings": "9:00 AM - 1:00 PM, 4:00 PM - 7:00 PM"}', 1),
('FAC-GAMDI-05', 'Urban Primary Health Centre (UPHC) Gamdi Gate', 'PHC', 'Anand', 'Gujarat', 'Near Gamdi Gate, Anand - Vidyanagar Highway, Anand 388001', 22.5582300, 72.9461200, '+91 2692 245220', '{"beds": 10, "ambulance": 1, "maternal_care": true, "immunization": true}', 1),
('FAC-ZYDUS-06', 'Zydus Healthcare Hospital & Trauma Centre', 'DH', 'Anand', 'Gujarat', 'Anand-Lambhvel Road, Near GIDC Phase 2, Anand 388001', 22.5760500, 72.9520400, '+91 2692 667000', '{"beds": 200, "icu_beds": 30, "emergency_24x7": true, "trauma_centre": true}', 1),
('FAC-BVM-07', 'Bhaikaka Community Care SubCentre (BVM Campus)', 'SubCentre', 'Vallabh Vidyanagar', 'Gujarat', 'Opposite BVM Engineering College, AV Road, Vallabh Vidyanagar 388120', 22.5522400, 72.9288700, '+91 2692 230104', '{"first_aid": true, "teleconsult": true, "asha_workers": 4, "student_health": true}', 1),
('FAC-CIVIL-08', 'Anand General Civil District Hospital', 'DH', 'Anand', 'Gujarat', 'Borsad Chokdi, Station Road, Anand 388001', 22.5645000, 72.9585000, '+91 2692 250100', '{"beds": 350, "blood_bank": true, "burn_unit": true, "dialysis": true, "emergency_24x7": true}', 1);

INSERT INTO role_permissions (role, action, is_allowed) VALUES
('system_admin', 'view_analytics', 1), ('system_admin', 'view_records', 1), ('system_admin', 'view_inventory', 1), ('system_admin', 'view_appointments', 1), ('system_admin', 'view_audit_logs', 1),
('system_admin', 'manage_staff', 1), ('system_admin', 'manage_facilities', 1), ('system_admin', 'manage_inventory', 1), ('system_admin', 'manage_permissions', 1), ('system_admin', 'manage_referrals', 1),
('system_admin', 'manage_prescriptions', 1), ('system_admin', 'manage_appointments', 1), ('system_admin', 'register_patient', 1), ('system_admin', 'create_consultation', 1), ('system_admin', 'teleconsult', 1),
('region_admin', 'view_analytics', 1), ('region_admin', 'view_records', 1), ('region_admin', 'view_inventory', 1), ('region_admin', 'view_appointments', 1), ('region_admin', 'view_audit_logs', 1),
('region_admin', 'manage_staff', 1), ('region_admin', 'manage_facilities', 0), ('region_admin', 'manage_inventory', 1), ('region_admin', 'manage_permissions', 0), ('region_admin', 'manage_referrals', 1),
('region_admin', 'manage_prescriptions', 1), ('region_admin', 'manage_appointments', 1), ('region_admin', 'register_patient', 1), ('region_admin', 'create_consultation', 1), ('region_admin', 'teleconsult', 1),
('doctor', 'view_analytics', 0), ('doctor', 'view_records', 1), ('doctor', 'view_inventory', 1), ('doctor', 'view_appointments', 1), ('doctor', 'view_audit_logs', 0),
('doctor', 'manage_staff', 0), ('doctor', 'manage_facilities', 0), ('doctor', 'manage_inventory', 0), ('doctor', 'manage_permissions', 0), ('doctor', 'manage_referrals', 1),
('doctor', 'manage_prescriptions', 1), ('doctor', 'manage_appointments', 1), ('doctor', 'register_patient', 1), ('doctor', 'create_consultation', 1), ('doctor', 'teleconsult', 1),
('nurse', 'view_analytics', 0), ('nurse', 'view_records', 1), ('nurse', 'view_inventory', 1), ('nurse', 'view_appointments', 1), ('nurse', 'view_audit_logs', 0),
('nurse', 'manage_staff', 0), ('nurse', 'manage_facilities', 0), ('nurse', 'manage_inventory', 0), ('nurse', 'manage_permissions', 0), ('nurse', 'manage_referrals', 0),
('nurse', 'manage_prescriptions', 0), ('nurse', 'manage_appointments', 1), ('nurse', 'register_patient', 1), ('nurse', 'create_consultation', 0), ('nurse', 'teleconsult', 0),
('pharmacist', 'view_analytics', 0), ('pharmacist', 'view_records', 1), ('pharmacist', 'view_inventory', 1), ('pharmacist', 'view_appointments', 0), ('pharmacist', 'view_audit_logs', 0),
('pharmacist', 'manage_staff', 0), ('pharmacist', 'manage_facilities', 0), ('pharmacist', 'manage_inventory', 1), ('pharmacist', 'manage_permissions', 0), ('pharmacist', 'manage_referrals', 0),
('pharmacist', 'manage_prescriptions', 1), ('pharmacist', 'manage_appointments', 0), ('pharmacist', 'register_patient', 0), ('pharmacist', 'create_consultation', 0), ('pharmacist', 'teleconsult', 0),
('receptionist', 'view_analytics', 0), ('receptionist', 'view_records', 0), ('receptionist', 'view_inventory', 0), ('receptionist', 'view_appointments', 1), ('receptionist', 'view_audit_logs', 0),
('receptionist', 'manage_staff', 0), ('receptionist', 'manage_facilities', 0), ('receptionist', 'manage_inventory', 0), ('receptionist', 'manage_permissions', 0), ('receptionist', 'manage_referrals', 0),
('receptionist', 'manage_prescriptions', 0), ('receptionist', 'manage_appointments', 1), ('receptionist', 'register_patient', 1), ('receptionist', 'create_consultation', 0), ('receptionist', 'teleconsult', 0),
('patient', 'view_analytics', 0), ('patient', 'view_records', 1), ('patient', 'view_inventory', 0), ('patient', 'view_appointments', 1), ('patient', 'view_audit_logs', 0),
('patient', 'manage_staff', 0), ('patient', 'manage_facilities', 0), ('patient', 'manage_inventory', 0), ('patient', 'manage_permissions', 0), ('patient', 'manage_referrals', 0),
('patient', 'manage_prescriptions', 0), ('patient', 'manage_appointments', 0), ('patient', 'register_patient', 0), ('patient', 'create_consultation', 0), ('patient', 'teleconsult', 1);

INSERT INTO users (id, staff_id, username, password_hash, full_name, role, center_id, phone, email, is_active, invite_status, designation) VALUES
(1, 'ADM-2026-001', 'admin', '$2b$12$aJqUfKdzJ60CZobOfS89aOs9EK/4.TQoAhZRRQbLVXb2erzfz3MCm', 'Master Health Administrator', 'system_admin', NULL, '+91 2692 230000', 'admin@anvayavistara.in', 1, 'active', 'Chief Health Officer / System Governor'),
(2, 'RAD-2026-001', 'admin_bakrol', '$2b$12$OHGWdC.gkoow1D7HLj.W5ezktYi4pluejjyhvRYcqIQiqEt8KADbq', 'Bakrol PHC Administrator', 'region_admin', 'FAC-BAKROL-01', '+91 2692 236105', 'bakrol.admin@anvayavistara.in', 1, 'active', 'Facility Health In-Charge'),
(3, 'RAD-2026-002', 'admin_skh', '$2b$12$OHGWdC.gkoow1D7HLj.W5ezktYi4pluejjyhvRYcqIQiqEt8KADbq', 'Shree Krishna Hospital Admin', 'region_admin', 'FAC-SKH-02', '+91 2692 228412', 'skh.admin@anvayavistara.in', 1, 'active', 'Medical Superintendent Admin'),
(4, 'RAD-2026-003', 'admin_karamsad', '$2b$12$OHGWdC.gkoow1D7HLj.W5ezktYi4pluejjyhvRYcqIQiqEt8KADbq', 'Karamsad CHC Administrator', 'region_admin', 'FAC-KARAMSAD-03', '+91 2692 222109', 'karamsad.admin@anvayavistara.in', 1, 'active', 'CHC Regional Supervisor'),
(5, 'RAD-2026-004', 'admin_vvn', '$2b$12$OHGWdC.gkoow1D7HLj.W5ezktYi4pluejjyhvRYcqIQiqEt8KADbq', 'Vidyanagar Dispensary Admin', 'region_admin', 'FAC-VVN-04', '+91 2692 230457', 'vvn.admin@anvayavistara.in', 1, 'active', 'Municipal Health Supervisor'),
(6, 'RAD-2026-005', 'admin_gamdi', '$2b$12$OHGWdC.gkoow1D7HLj.W5ezktYi4pluejjyhvRYcqIQiqEt8KADbq', 'Gamdi UPHC Administrator', 'region_admin', 'FAC-GAMDI-05', '+91 2692 245221', 'gamdi.admin@anvayavistara.in', 1, 'active', 'Urban Health Center Admin'),
(7, 'RAD-2026-006', 'admin_zydus', '$2b$12$OHGWdC.gkoow1D7HLj.W5ezktYi4pluejjyhvRYcqIQiqEt8KADbq', 'Zydus Trauma Centre Admin', 'region_admin', 'FAC-ZYDUS-06', '+91 2692 667001', 'zydus.admin@anvayavistara.in', 1, 'active', 'Hospital Operations Admin'),
(8, 'RAD-2026-007', 'admin_bvm', '$2b$12$OHGWdC.gkoow1D7HLj.W5ezktYi4pluejjyhvRYcqIQiqEt8KADbq', 'BVM SubCentre Administrator', 'region_admin', 'FAC-BVM-07', '+91 2692 230105', 'bvm.admin@anvayavistara.in', 1, 'active', 'SubCentre Field Coordinator'),
(9, 'RAD-2026-008', 'admin_anand', '$2b$12$OHGWdC.gkoow1D7HLj.W5ezktYi4pluejjyhvRYcqIQiqEt8KADbq', 'District Civil Hospital Admin', 'region_admin', 'FAC-CIVIL-08', '+91 2692 250101', 'anand.admin@anvayavistara.in', 1, 'active', 'District Administrative Officer'),
(11, NULL, 'vallabh2006', '$2b$12$OHGWdC.gkoow1D7HLj.W5ezktYi4pluejjyhvRYcqIQiqEt8KADbq', 'Vallabh Mehrotra', 'patient', NULL, '+91 98765 43211', 'vallabhmehrotra@gmail.com', 1, 'active', 'Registered Patient'),
(13, 'PHM-2026-001', 'vallu', '$2b$12$OHGWdC.gkoow1D7HLj.W5ezktYi4pluejjyhvRYcqIQiqEt8KADbq', 'Dr. Vallabh Mehrotra', 'doctor', 'FAC-BAKROL-01', '+91 98765 43210', 'vallabhmehrotra45@gmail.com', 1, 'active', 'Medical Officer / General Physician'),
(17, NULL, 'patient_test_updated', '$2b$12$OHGWdC.gkoow1D7HLj.W5ezktYi4pluejjyhvRYcqIQiqEt8KADbq', 'Test Patient Updated', 'patient', NULL, '+91 98765 43212', 'updated_email@patient.com', 1, 'active', 'Registered Patient');

INSERT INTO patients (id, linked_user_id, full_name, dob, gender, phone, address, blood_group, allergies, chronic_conditions, center_id, is_high_risk) VALUES
('PAT-2026-0001', 17, 'Test Patient Updated', '1995-05-15', 'M', '+91 98765 43211', '12 Vallabh Vidyanagar Main Road, Anand 388120', 'O+', '["Not Allergic"]', '["Hypertension"]', 'FAC-BAKROL-01', 0),
('PAT-2026-0002', 11, 'Vallabh Mehrotra', '1988-08-20', 'F', '+91 98765 43212', '45 Station Road, Anand 388001', 'A+', '["Penicillin"]', '["Diabetes Type 2"]', 'FAC-BAKROL-01', 1);

INSERT INTO vehicles (id, type, region, status, center_id, driver_name, driver_phone, lat, lng) VALUES
('AMB-BAKROL-01', 'Basic Life Support Ambulance', 'Vallabh Vidyanagar', 'available', 'FAC-BAKROL-01', 'Ramesh Kumar', '+91 98250 11223', 22.5488000, 72.9372000),
('AMB-SKH-01', 'Advanced Cardiac Life Support (ACLS)', 'Karamsad', 'available', 'FAC-SKH-02', 'Suresh Patel', '+91 98250 44556', 22.5471000, 72.8986000),
('AMB-CIVIL-01', 'Trauma Emergency Ambulance', 'Anand', 'available', 'FAC-CIVIL-08', 'Mahesh Solanki', '+91 98250 77889', 22.5645000, 72.9585000);

INSERT INTO inventory_items (center_id, item_name, category, quantity, unit, expiry_date, reorder_level) VALUES
('FAC-BAKROL-01', 'Paracetamol 500mg', 'Analgesic', 4500, 'tablets', '2027-12-31', 500),
('FAC-BAKROL-01', 'Amoxicillin 500mg Capsules', 'Antibiotics', 1200, 'capsules', '2026-11-30', 200),
('FAC-BAKROL-01', 'Metformin 500mg', 'Antidiabetic', 2500, 'tablets', '2027-08-31', 300),
('FAC-BAKROL-01', 'Oral Rehydration Salts (ORS)', 'Essential Medicine', 800, 'sachets', '2028-05-31', 150),
('FAC-BAKROL-01', 'Telmisartan 40mg', 'Antihypertensive', 1800, 'tablets', '2027-10-31', 250),
('FAC-SKH-02', 'Adrenaline Injection 1mg/ml', 'Emergency Critical', 450, 'ampoules', '2027-06-30', 50),
('FAC-SKH-02', 'IV Normal Saline 500ml', 'IV Fluids', 950, 'bottles', '2028-01-31', 100);

SET FOREIGN_KEY_CHECKS = 1;
