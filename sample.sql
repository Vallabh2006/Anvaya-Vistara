SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

CREATE TABLE `appointments` (
  `id` int(11) NOT NULL,
  `patient_id` varchar(30) NOT NULL,
  `center_id` varchar(30) NOT NULL,
  `doctor_id` int(11) DEFAULT NULL,
  `token_number` varchar(30) DEFAULT NULL,
  `department` varchar(100) DEFAULT NULL,
  `referral_id` int(11) DEFAULT NULL,
  `slot_time` datetime NOT NULL,
  `end_time` datetime DEFAULT NULL,
  `reason` varchar(500) DEFAULT NULL,
  `urgency` tinyint(4) NOT NULL DEFAULT 3,
  `status` enum('scheduled','checked_in','in_progress','completed','cancelled','no_show') NOT NULL DEFAULT 'scheduled',
  `notes` text DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `updated_at` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE `audit_logs` (
  `id` bigint(20) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `action` varchar(100) NOT NULL,
  `entity_type` varchar(50) DEFAULT NULL,
  `entity_id` varchar(50) DEFAULT NULL,
  `detail` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`detail`)),
  `ip_address` varchar(45) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `centers` (
  `id` varchar(30) NOT NULL,
  `name` varchar(200) NOT NULL,
  `type` enum('PHC','CHC','DH','Dispensary','SubCentre') NOT NULL,
  `region` varchar(100) NOT NULL,
  `state` varchar(100) NOT NULL DEFAULT '',
  `address` text DEFAULT NULL,
  `lat` decimal(10,7) DEFAULT NULL,
  `lng` decimal(10,7) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `resources` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`resources`)),
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `updated_at` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `centers` (`id`, `name`, `type`, `region`, `state`, `address`, `lat`, `lng`, `phone`, `resources`, `is_active`, `created_at`, `updated_at`) VALUES
('FAC-BAKROL-01', 'Primary Health Centre (PHC) Bakrol', 'PHC', 'Vallabh Vidyanagar', 'Gujarat', 'Near Bakrol Gate, Bakrol-Vadtal Road, Bakrol, Vallabh Vidyanagar 388315', 22.5488200, 72.9372100, '+91 2692 236104', '{\"beds\": 12, \"ambulance\": 1, \"oxygen\": 8, \"opd_daily\": 140, \"timings\": \"24x7 Emergency / OPD 9AM - 5PM\"}', 1, '2026-09-05 22:21:01', '2026-09-05 22:21:01'),
('FAC-BVM-07', 'Bhaikaka Community Care SubCentre (BVM Campus)', 'SubCentre', 'Vallabh Vidyanagar', 'Gujarat', 'Opposite BVM Engineering College, AV Road, Vallabh Vidyanagar 388120', 22.5522400, 72.9288700, '+91 2692 230104', '{\"first_aid\": true, \"teleconsult\": true, \"asha_workers\": 4, \"student_health\": true}', 1, '2026-09-05 22:21:01', '2026-09-05 22:21:01'),
('FAC-CIVIL-08', 'Anand General Civil District Hospital', 'DH', 'Anand', 'Gujarat', 'Borsad Chokdi, Station Road, Anand 388001', 22.5645000, 72.9585000, '+91 2692 250100', '{\"beds\": 350, \"blood_bank\": true, \"burn_unit\": true, \"dialysis\": true, \"emergency_24x7\": true}', 1, '2026-09-05 22:21:01', '2026-09-05 22:21:01'),
('FAC-GAMDI-05', 'Urban Primary Health Centre (UPHC) Gamdi Gate', 'PHC', 'Anand', 'Gujarat', 'Near Gamdi Gate, Anand - Vidyanagar Highway, Anand 388001', 22.5582300, 72.9461200, '+91 2692 245220', '{\"beds\": 10, \"ambulance\": 1, \"maternal_care\": true, \"immunization\": true}', 1, '2026-09-05 22:21:01', '2026-09-05 22:21:01'),
('FAC-KARAMSAD-03', 'Community Health Centre (CHC) Karamsad', 'CHC', 'Karamsad', 'Gujarat', 'Karamsad Main Road, Near Sardar Patel Memorial, Karamsad 388325', 22.5495100, 72.9052300, '+91 2692 222108', '{\"beds\": 30, \"ambulance\": 2, \"maternity_ward\": true, \"lab\": true}', 1, '2026-09-05 22:21:01', '2026-09-05 22:21:01'),
('FAC-SKH-02', 'Shree Krishna Hospital & Bhaikaka Medical Centre', 'DH', 'Karamsad', 'Gujarat', 'Gokal Nagar, Karamsad - Vidyanagar Road, Anand 388325', 22.5471400, 72.8986500, '+91 2692 228411', '{\"beds\": 550, \"icu_beds\": 60, \"ambulance\": 6, \"blood_bank\": true, \"specialities\": [\"Cardiology\", \"Trauma\", \"Pediatrics\", \"Oncology\"]}', 1, '2026-09-05 22:21:01', '2026-09-05 22:21:01'),
('FAC-VVN-04', 'Vidyanagar Municipal Dispensary & Health Post', 'Dispensary', 'Vallabh Vidyanagar', 'Gujarat', 'Mota Bazaar, Near Shastri Maidan, Vallabh Vidyanagar 388120', 22.5530100, 72.9240300, '+91 2692 230457', '{\"opd_rooms\": 3, \"pharmacy\": true, \"vaccination\": true, \"timings\": \"9:00 AM - 1:00 PM, 4:00 PM - 7:00 PM\"}', 1, '2026-09-05 22:21:01', '2026-09-05 22:21:01'),
('FAC-ZYDUS-06', 'Zydus Healthcare Hospital & Trauma Centre', 'DH', 'Anand', 'Gujarat', 'Anand-Lambhvel Road, Near GIDC Phase 2, Anand 388001', 22.5760500, 72.9520400, '+91 2692 667000', '{\"beds\": 200, \"icu_beds\": 30, \"emergency_24x7\": true, \"trauma_centre\": true}', 1, '2026-09-05 22:21:01', '2026-09-05 22:21:01');

CREATE TABLE `follow_ups` (
  `id` int(11) NOT NULL,
  `patient_id` varchar(30) NOT NULL,
  `category` enum('maternal','child','chronic','high_risk','general','post_referral') NOT NULL,
  `due_date` date NOT NULL,
  `status` enum('pending','completed','missed','rescheduled') NOT NULL DEFAULT 'pending',
  `assigned_to` int(11) DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `completed_at` datetime DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `updated_at` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `inventory_items` (
  `id` int(11) NOT NULL,
  `center_id` varchar(30) NOT NULL,
  `item_name` varchar(200) NOT NULL,
  `category` varchar(100) DEFAULT NULL,
  `quantity` int(11) NOT NULL DEFAULT 0,
  `unit` varchar(30) NOT NULL DEFAULT 'units',
  `expiry_date` date DEFAULT NULL,
  `reorder_level` int(11) NOT NULL DEFAULT 10,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `updated_at` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `inventory_items` (`id`, `center_id`, `item_name`, `category`, `quantity`, `unit`, `expiry_date`, `reorder_level`, `created_at`, `updated_at`) VALUES
(58, 'FAC-BAKROL-01', 'Ibuprofen 400mg', 'Analgesic', 2400, 'tablets', '2028-06-30', 200, '2026-09-06 11:58:23', '2026-09-06 12:15:33'),
(59, 'FAC-BAKROL-01', 'Amoxicillin 500mg', 'Antibiotic', 1600, 'capsules', '2027-09-30', 150, '2026-09-06 11:58:23', '2026-09-06 12:15:33'),
(60, 'FAC-BAKROL-01', 'Azithromycin 500mg', 'Antibiotic', 900, 'tablets', '2027-11-30', 100, '2026-09-06 11:58:23', '2026-09-06 12:15:33'),
(61, 'FAC-BAKROL-01', 'Cetirizine 10mg', 'Antihistamine', 4000, 'tablets', '2028-03-31', 300, '2026-09-06 11:58:23', '2026-09-06 12:15:33'),
(62, 'FAC-BAKROL-01', 'ORS Sachets', 'Rehydration', 7000, 'sachets', '2028-12-31', 500, '2026-09-06 11:58:23', '2026-09-06 12:15:33'),
(63, 'FAC-BAKROL-01', 'Vitamin C 500mg', 'Supplement', 3000, 'tablets', '2028-05-31', 200, '2026-09-06 11:58:23', '2026-09-06 12:15:33'),
(64, 'FAC-BAKROL-01', 'Calcium 500mg', 'Supplement', 1800, 'tablets', '2028-02-29', 150, '2026-09-06 11:58:23', '2026-09-06 12:15:33'),
(65, 'FAC-BAKROL-01', 'Iron Folic Acid', 'Supplement', 4400, 'tablets', '2028-08-31', 300, '2026-09-06 11:58:23', '2026-09-06 12:15:33'),
(66, 'FAC-BAKROL-01', 'Metformin 500mg', 'Antidiabetic', 2200, 'tablets', '2028-04-30', 200, '2026-09-06 11:58:23', '2026-09-06 12:15:33'),
(67, 'FAC-BAKROL-01', 'Amlodipine 5mg', 'Antihypertensive', 1500, 'tablets', '2028-07-31', 100, '2026-09-06 11:58:23', '2026-09-06 12:15:33'),
(68, 'FAC-BAKROL-01', 'Paracetamol 500mg Tablets', 'Analgesic', 1000, 'tablets', '2027-12-31', 100, '2026-09-06 12:15:44', '2026-09-06 12:15:58'),
(69, 'FAC-BAKROL-01', 'Amoxicillin 250mg Capsules', 'Antibiotic', 500, 'capsules', '2027-06-30', 50, '2026-09-06 12:15:44', '2026-09-06 12:15:58'),
(70, 'FAC-SKH-02', 'Normal Saline 0.9% IV 500ml', 'IV Fluids', 200, 'bottles', '2027-10-31', 30, '2026-09-06 12:15:44', '2026-09-06 12:15:58'),
(71, 'FAC-CIVIL-08', 'Paracetamol 650mg', 'Analgesic', 3200, 'tablets', '2028-01-31', 250, '2026-09-06 13:00:00', '2026-09-06 13:00:00'),
(72, 'FAC-CIVIL-08', 'Diclofenac 50mg', 'Analgesic', 1800, 'tablets', '2027-10-31', 150, '2026-09-06 13:00:00', '2026-09-06 13:00:00'),
(73, 'FAC-CIVIL-08', 'Ceftriaxone 1g Injection', 'Antibiotic', 600, 'vials', '2027-08-31', 80, '2026-09-06 13:00:00', '2026-09-06 13:00:00'),
(74, 'FAC-CIVIL-08', 'Metronidazole 400mg', 'Antibiotic', 2000, 'tablets', '2027-12-31', 200, '2026-09-06 13:00:00', '2026-09-06 13:00:00'),
(75, 'FAC-CIVIL-08', 'Insulin Regular 40IU', 'Antidiabetic', 300, 'vials', '2027-05-31', 50, '2026-09-06 13:00:00', '2026-09-06 13:00:00'),
(76, 'FAC-CIVIL-08', 'Ringer Lactate IV 500ml', 'IV Fluids', 450, 'bottles', '2028-02-28', 60, '2026-09-06 13:00:00', '2026-09-06 13:00:00'),
(77, 'FAC-CIVIL-08', 'Surgical Gloves (Sterile)', 'PPE', 5000, 'pairs', '2029-01-31', 500, '2026-09-06 13:00:00', '2026-09-06 13:00:00'),
(78, 'FAC-CIVIL-08', 'N95 Masks', 'PPE', 3500, 'pieces', '2028-11-30', 300, '2026-09-06 13:00:00', '2026-09-06 13:00:00'),
(79, 'FAC-CIVIL-08', 'Betadine Solution 500ml', 'Antiseptic', 400, 'bottles', '2028-04-30', 40, '2026-09-06 13:00:00', '2026-09-06 13:00:00'),
(80, 'FAC-GAMDI-05', 'Cough Syrup (Dextromethorphan)', 'Antitussive', 800, 'bottles', '2027-09-30', 80, '2026-09-06 13:05:00', '2026-09-06 13:05:00'),
(81, 'FAC-GAMDI-05', 'Ranitidine 150mg', 'Antacid', 2600, 'tablets', '2027-07-31', 200, '2026-09-06 13:05:00', '2026-09-06 13:05:00'),
(82, 'FAC-GAMDI-05', 'Omeprazole 20mg', 'Antacid', 3000, 'capsules', '2028-03-31', 250, '2026-09-06 13:05:00', '2026-09-06 13:05:00'),
(83, 'FAC-GAMDI-05', 'Salbutamol Inhaler', 'Bronchodilator', 350, 'units', '2027-11-30', 40, '2026-09-06 13:05:00', '2026-09-06 13:05:00'),
(84, 'FAC-GAMDI-05', 'Multivitamin Syrup', 'Supplement', 900, 'bottles', '2028-06-30', 90, '2026-09-06 13:05:00', '2026-09-06 13:05:00'),
(85, 'FAC-GAMDI-05', 'Chlorhexidine Mouthwash', 'Antiseptic', 500, 'bottles', '2028-01-31', 50, '2026-09-06 13:05:00', '2026-09-06 13:05:00'),
(86, 'FAC-GAMDI-05', 'Disposable Syringes 5ml', 'Consumables', 8000, 'pieces', '2029-05-31', 800, '2026-09-06 13:05:00', '2026-09-06 13:05:00'),
(87, 'FAC-GAMDI-05', 'IV Cannula 20G', 'Consumables', 2500, 'pieces', '2028-09-30', 200, '2026-09-06 13:05:00', '2026-09-06 13:05:00'),
(88, 'FAC-KARAMSAD-03', 'Losartan 50mg', 'Antihypertensive', 2100, 'tablets', '2028-05-31', 180, '2026-09-06 13:10:00', '2026-09-06 13:10:00'),
(89, 'FAC-KARAMSAD-03', 'Atorvastatin 10mg', 'Lipid-Lowering', 1900, 'tablets', '2028-07-31', 150, '2026-09-06 13:10:00', '2026-09-06 13:10:00'),
(90, 'FAC-KARAMSAD-03', 'Gliclazide 80mg', 'Antidiabetic', 1400, 'tablets', '2027-10-31', 120, '2026-09-06 13:10:00', '2026-09-06 13:10:00'),
(91, 'FAC-KARAMSAD-03', 'Folic Acid 5mg', 'Supplement', 3600, 'tablets', '2028-08-31', 300, '2026-09-06 13:10:00', '2026-09-06 13:10:00'),
(92, 'FAC-KARAMSAD-03', 'Tetanus Toxoid Injection', 'Vaccine', 700, 'vials', '2027-12-31', 100, '2026-09-06 13:10:00', '2026-09-06 13:10:00'),
(93, 'FAC-KARAMSAD-03', 'Hepatitis B Vaccine', 'Vaccine', 500, 'vials', '2028-02-28', 60, '2026-09-06 13:10:00', '2026-09-06 13:10:00'),
(94, 'FAC-KARAMSAD-03', 'Surgical Sutures 3-0', 'Surgical Supplies', 1200, 'packs', '2028-10-31', 100, '2026-09-06 13:10:00', '2026-09-06 13:10:00'),
(95, 'FAC-SKH-02', 'Dextrose 5% IV 500ml', 'IV Fluids', 380, 'bottles', '2027-11-30', 50, '2026-09-06 13:15:00', '2026-09-06 13:15:00'),
(96, 'FAC-SKH-02', 'Adrenaline Injection 1mg', 'Emergency Drugs', 250, 'ampoules', '2027-06-30', 40, '2026-09-06 13:15:00', '2026-09-06 13:15:00'),
(97, 'FAC-SKH-02', 'Atropine Injection', 'Emergency Drugs', 200, 'ampoules', '2027-09-30', 30, '2026-09-06 13:15:00', '2026-09-06 13:15:00'),
(98, 'FAC-SKH-02', 'Hydrocortisone Injection', 'Steroid', 300, 'vials', '2027-08-31', 40, '2026-09-06 13:15:00', '2026-09-06 13:15:00'),
(99, 'FAC-SKH-02', 'Surgical Face Masks', 'PPE', 6000, 'pieces', '2028-12-31', 500, '2026-09-06 13:15:00', '2026-09-06 13:15:00'),
(100, 'FAC-SKH-02', 'Alcohol Swabs', 'Consumables', 10000, 'pieces', '2029-03-31', 1000, '2026-09-06 13:15:00', '2026-09-06 13:15:00'),
(101, 'FAC-SKH-02', 'Blood Collection Tubes (EDTA)', 'Consumables', 4000, 'pieces', '2028-06-30', 400, '2026-09-06 13:15:00', '2026-09-06 13:15:00'),
(102, 'FAC-VVN-04', 'Cefixime 200mg', 'Antibiotic', 1700, 'tablets', '2027-10-31', 150, '2026-09-06 13:20:00', '2026-09-06 13:20:00'),
(103, 'FAC-VVN-04', 'Doxycycline 100mg', 'Antibiotic', 1500, 'capsules', '2027-12-31', 120, '2026-09-06 13:20:00', '2026-09-06 13:20:00'),
(104, 'FAC-VVN-04', 'Loperamide 2mg', 'Antidiarrheal', 2200, 'tablets', '2028-01-31', 200, '2026-09-06 13:20:00', '2026-09-06 13:20:00'),
(105, 'FAC-VVN-04', 'Zinc Sulphate Syrup', 'Supplement', 1100, 'bottles', '2028-04-30', 100, '2026-09-06 13:20:00', '2026-09-06 13:20:00'),
(106, 'FAC-VVN-04', 'Diazepam 5mg', 'Sedative', 900, 'tablets', '2027-07-31', 80, '2026-09-06 13:20:00', '2026-09-06 13:20:00'),
(107, 'FAC-VVN-04', 'Digital Thermometers', 'Equipment', 150, 'units', NULL, 20, '2026-09-06 13:20:00', '2026-09-06 13:20:00'),
(108, 'FAC-VVN-04', 'Pulse Oximeters', 'Equipment', 100, 'units', NULL, 15, '2026-09-06 13:20:00', '2026-09-06 13:20:00'),
(109, 'FAC-ZYDUS-06', 'Clopidogrel 75mg', 'Antiplatelet', 1300, 'tablets', '2028-03-31', 100, '2026-09-06 13:25:00', '2026-09-06 13:25:00'),
(110, 'FAC-ZYDUS-06', 'Aspirin 75mg', 'Antiplatelet', 3400, 'tablets', '2028-05-31', 300, '2026-09-06 13:25:00', '2026-09-06 13:25:00'),
(111, 'FAC-ZYDUS-06', 'Furosemide 40mg', 'Diuretic', 1600, 'tablets', '2027-11-30', 150, '2026-09-06 13:25:00', '2026-09-06 13:25:00'),
(112, 'FAC-ZYDUS-06', 'Spironolactone 25mg', 'Diuretic', 1000, 'tablets', '2027-09-30', 100, '2026-09-06 13:25:00', '2026-09-06 13:25:00'),
(113, 'FAC-ZYDUS-06', 'Prednisolone 5mg', 'Steroid', 1200, 'tablets', '2027-12-31', 100, '2026-09-06 13:25:00', '2026-09-06 13:25:00'),
(114, 'FAC-ZYDUS-06', 'Fexofenadine 120mg', 'Antihistamine', 1800, 'tablets', '2028-02-29', 150, '2026-09-06 13:25:00', '2026-09-06 13:25:00'),
(115, 'FAC-ZYDUS-06', 'Antiseptic Hand Sanitizer 500ml', 'Antiseptic', 700, 'bottles', '2028-08-31', 70, '2026-09-06 13:25:00', '2026-09-06 13:25:00'),
(116, 'FAC-CIVIL-08', 'Oral Rehydration Salts (WHO)', 'Rehydration', 5000, 'sachets', '2028-10-31', 400, '2026-09-06 13:30:00', '2026-09-06 13:30:00'),
(117, 'FAC-GAMDI-05', 'Vitamin D3 60000IU', 'Supplement', 2000, 'capsules', '2028-07-31', 180, '2026-09-06 13:30:00', '2026-09-06 13:30:00'),
(118, 'FAC-KARAMSAD-03', 'Surgical Cotton Rolls', 'Surgical Supplies', 900, 'rolls', '2029-01-31', 90, '2026-09-06 13:30:00', '2026-09-06 13:30:00'),
(119, 'FAC-SKH-02', 'Elastic Crepe Bandage', 'Surgical Supplies', 1500, 'rolls', '2028-11-30', 150, '2026-09-06 13:30:00', '2026-09-06 13:30:00'),
(120, 'FAC-VVN-04', 'Glucometer Test Strips', 'Consumables', 3000, 'pieces', '2027-12-31', 250, '2026-09-06 13:30:00', '2026-09-06 13:30:00');

CREATE TABLE `lab_records` (
  `id` int(11) NOT NULL,
  `patient_id` varchar(30) NOT NULL,
  `test_name` varchar(200) NOT NULL,
  `test_category` varchar(100) DEFAULT NULL,
  `result` text DEFAULT NULL,
  `result_data` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`result_data`)),
  `status` enum('ordered','sample_collected','processing','resulted','cancelled') NOT NULL DEFAULT 'ordered',
  `center_id` varchar(30) NOT NULL,
  `ordered_by` int(11) NOT NULL,
  `resulted_at` datetime DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `updated_at` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `medical_records` (
  `id` int(11) NOT NULL,
  `patient_id` varchar(30) NOT NULL,
  `record_type` enum('consultation','lab','imaging','note','discharge_summary') NOT NULL,
  `title` varchar(200) DEFAULT NULL,
  `data` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`data`)),
  `center_id` varchar(30) NOT NULL,
  `created_by` int(11) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `notifications` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `title` varchar(300) NOT NULL,
  `body` text DEFAULT NULL,
  `link` varchar(500) DEFAULT NULL,
  `is_read` tinyint(1) NOT NULL DEFAULT 0,
  `created_at` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `patients` (
  `id` varchar(30) NOT NULL,
  `linked_user_id` int(11) DEFAULT NULL,
  `full_name` varchar(200) NOT NULL,
  `dob` date DEFAULT NULL,
  `gender` enum('M','F','Other') NOT NULL DEFAULT 'Other',
  `phone` varchar(20) DEFAULT NULL,
  `address` text DEFAULT NULL,
  `aadhaar_hash` varchar(64) DEFAULT NULL,
  `blood_group` varchar(20) DEFAULT NULL,
  `allergies` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`allergies`)),
  `chronic_conditions` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`chronic_conditions`)),
  `center_id` varchar(30) DEFAULT NULL,
  `is_high_risk` tinyint(1) NOT NULL DEFAULT 0,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `updated_at` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `prescriptions` (
  `id` int(11) NOT NULL,
  `record_id` int(11) DEFAULT NULL,
  `patient_id` varchar(30) NOT NULL,
  `medicines` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`medicines`)),
  `notes` text DEFAULT NULL,
  `prescribed_by` int(11) NOT NULL,
  `center_id` varchar(30) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `referrals` (
  `id` int(11) NOT NULL,
  `patient_id` varchar(30) NOT NULL,
  `from_center` varchar(30) NOT NULL,
  `to_center` varchar(30) NOT NULL,
  `urgency` enum('critical','high','medium','low') NOT NULL DEFAULT 'medium',
  `status` enum('initiated','accepted','in_transit','completed','counter_referred','rejected') NOT NULL DEFAULT 'initiated',
  `reason` text DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `created_by` int(11) NOT NULL,
  `accepted_by` int(11) DEFAULT NULL,
  `completed_at` datetime DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `updated_at` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `role_permissions` (
  `role` varchar(50) NOT NULL,
  `action` varchar(100) NOT NULL,
  `is_allowed` tinyint(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `role_permissions` (`role`, `action`, `is_allowed`) VALUES
('doctor', 'create_consultation', 1),
('doctor', 'manage_appointments', 1),
('doctor', 'manage_facilities', 0),
('doctor', 'manage_inventory', 0),
('doctor', 'manage_permissions', 0),
('doctor', 'manage_prescriptions', 1),
('doctor', 'manage_referrals', 1),
('doctor', 'manage_staff', 0),
('doctor', 'register_patient', 1),
('doctor', 'teleconsult', 1),
('doctor', 'view_analytics', 0),
('doctor', 'view_appointments', 1),
('doctor', 'view_audit_logs', 0),
('doctor', 'view_inventory', 1),
('doctor', 'view_records', 1),
('nurse', 'create_consultation', 0),
('nurse', 'manage_appointments', 1),
('nurse', 'manage_facilities', 0),
('nurse', 'manage_inventory', 0),
('nurse', 'manage_permissions', 0),
('nurse', 'manage_prescriptions', 0),
('nurse', 'manage_referrals', 0),
('nurse', 'manage_staff', 0),
('nurse', 'register_patient', 1),
('nurse', 'teleconsult', 0),
('nurse', 'view_analytics', 0),
('nurse', 'view_appointments', 1),
('nurse', 'view_audit_logs', 0),
('nurse', 'view_inventory', 1),
('nurse', 'view_records', 1),
('patient', 'create_consultation', 0),
('patient', 'manage_appointments', 0),
('patient', 'manage_facilities', 0),
('patient', 'manage_inventory', 0),
('patient', 'manage_permissions', 0),
('patient', 'manage_prescriptions', 0),
('patient', 'manage_referrals', 0),
('patient', 'manage_staff', 0),
('patient', 'register_patient', 0),
('patient', 'teleconsult', 1),
('patient', 'view_analytics', 0),
('patient', 'view_appointments', 1),
('patient', 'view_audit_logs', 0),
('patient', 'view_inventory', 0),
('patient', 'view_records', 1),
('pharmacist', 'create_consultation', 0),
('pharmacist', 'manage_appointments', 0),
('pharmacist', 'manage_facilities', 0),
('pharmacist', 'manage_inventory', 1),
('pharmacist', 'manage_permissions', 0),
('pharmacist', 'manage_prescriptions', 1),
('pharmacist', 'manage_referrals', 0),
('pharmacist', 'manage_staff', 0),
('pharmacist', 'register_patient', 0),
('pharmacist', 'teleconsult', 0),
('pharmacist', 'view_analytics', 0),
('pharmacist', 'view_appointments', 0),
('pharmacist', 'view_audit_logs', 0),
('pharmacist', 'view_inventory', 1),
('pharmacist', 'view_records', 1),
('receptionist', 'create_consultation', 0),
('receptionist', 'manage_appointments', 1),
('receptionist', 'manage_facilities', 0),
('receptionist', 'manage_inventory', 0),
('receptionist', 'manage_permissions', 0),
('receptionist', 'manage_prescriptions', 0),
('receptionist', 'manage_referrals', 0),
('receptionist', 'manage_staff', 0),
('receptionist', 'register_patient', 1),
('receptionist', 'teleconsult', 0),
('receptionist', 'view_analytics', 0),
('receptionist', 'view_appointments', 1),
('receptionist', 'view_audit_logs', 0),
('receptionist', 'view_inventory', 0),
('receptionist', 'view_records', 0),
('region_admin', 'create_consultation', 1),
('region_admin', 'manage_appointments', 1),
('region_admin', 'manage_facilities', 0),
('region_admin', 'manage_inventory', 1),
('region_admin', 'manage_permissions', 0),
('region_admin', 'manage_prescriptions', 1),
('region_admin', 'manage_referrals', 1),
('region_admin', 'manage_staff', 1),
('region_admin', 'register_patient', 1),
('region_admin', 'teleconsult', 1),
('region_admin', 'view_analytics', 1),
('region_admin', 'view_appointments', 1),
('region_admin', 'view_audit_logs', 1),
('region_admin', 'view_inventory', 1),
('region_admin', 'view_records', 1),
('system_admin', 'create_consultation', 1),
('system_admin', 'manage_appointments', 1),
('system_admin', 'manage_facilities', 1),
('system_admin', 'manage_inventory', 1),
('system_admin', 'manage_permissions', 1),
('system_admin', 'manage_prescriptions', 1),
('system_admin', 'manage_referrals', 1),
('system_admin', 'manage_staff', 1),
('system_admin', 'register_patient', 1),
('system_admin', 'teleconsult', 1),
('system_admin', 'view_analytics', 1),
('system_admin', 'view_appointments', 1),
('system_admin', 'view_audit_logs', 1),
('system_admin', 'view_inventory', 1),
('system_admin', 'view_records', 1);

CREATE TABLE `teleconsult_messages` (
  `id` int(11) NOT NULL,
  `session_id` int(11) NOT NULL,
  `sender_id` int(11) NOT NULL,
  `body` text NOT NULL,
  `sent_at` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `teleconsult_sessions` (
  `id` int(11) NOT NULL,
  `patient_id` varchar(30) NOT NULL,
  `doctor_id` int(11) NOT NULL,
  `center_id` varchar(30) NOT NULL,
  `status` enum('requested','active','completed','cancelled') NOT NULL DEFAULT 'requested',
  `summary` text DEFAULT NULL,
  `started_at` datetime DEFAULT NULL,
  `ended_at` datetime DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `triage_entries` (
  `id` int(11) NOT NULL,
  `patient_id` varchar(30) NOT NULL,
  `center_id` varchar(30) NOT NULL,
  `assessed_by` int(11) NOT NULL,
  `urgency_score` tinyint(4) NOT NULL,
  `symptoms` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`symptoms`)),
  `vitals` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`vitals`)),
  `recommendation` text DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `staff_id` varchar(30) DEFAULT NULL,
  `username` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `full_name` varchar(200) NOT NULL,
  `role` varchar(50) NOT NULL,
  `center_id` varchar(30) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `email` varchar(200) DEFAULT NULL,
  `totp_secret` varchar(64) DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `lang_pref` varchar(10) NOT NULL DEFAULT 'en',
  `invite_status` varchar(30) NOT NULL DEFAULT 'active',
  `invite_token` varchar(100) DEFAULT NULL,
  `designation` varchar(100) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `updated_at` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `failed_login_count` int(11) DEFAULT 0,
  `locked_until` datetime DEFAULT NULL,
  `session_version` int(11) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `users` (`id`, `staff_id`, `username`, `password_hash`, `full_name`, `role`, `center_id`, `phone`, `email`, `totp_secret`, `is_active`, `lang_pref`, `invite_status`, `invite_token`, `designation`, `created_at`, `updated_at`, `failed_login_count`, `locked_until`, `session_version`) VALUES
(1, 'ADM-2026-001', 'admin', '$2b$12$4o4lqHmY0MDN8wksSvpXPeEI4wZ8dPqqi2XMwA8A.fH78QTZJ7BNa', 'Master Health Administrator', 'system_admin', NULL, '+91 2692 230000', 'admin@anvayavistara.in', NULL, 1, 'en', 'active', NULL, 'Chief Health Officer / System Governor', '2026-09-05 22:21:01', '2026-09-06 12:33:51', 0, NULL, 2),
(2, 'RAD-2026-001', 'admin_bakrol', '$2b$12$4o4lqHmY0MDN8wksSvpXPeEI4wZ8dPqqi2XMwA8A.fH78QTZJ7BNa', 'Bakrol PHC Administrator', 'region_admin', 'FAC-BAKROL-01', '+91 2692 236105', 'bakrol.admin@anvayavistara.in', NULL, 1, 'en', 'active', NULL, 'Facility Health In-Charge', '2026-09-05 22:21:01', '2026-09-06 12:33:51', 0, NULL, 2),
(3, 'RAD-2026-002', 'admin_skh', '$2b$12$4o4lqHmY0MDN8wksSvpXPeEI4wZ8dPqqi2XMwA8A.fH78QTZJ7BNa', 'Shree Krishna Hospital Admin', 'region_admin', 'FAC-SKH-02', '+91 2692 228412', 'skh.admin@anvayavistara.in', NULL, 1, 'en', 'active', NULL, 'Medical Superintendent Admin', '2026-09-05 22:21:01', '2026-09-06 12:33:51', 0, NULL, 2),
(4, 'RAD-2026-003', 'admin_karamsad', '$2b$12$4o4lqHmY0MDN8wksSvpXPeEI4wZ8dPqqi2XMwA8A.fH78QTZJ7BNa', 'Karamsad CHC Administrator', 'region_admin', 'FAC-KARAMSAD-03', '+91 2692 222109', 'karamsad.admin@anvayavistara.in', NULL, 1, 'en', 'active', NULL, 'CHC Regional Supervisor', '2026-09-05 22:21:01', '2026-09-06 13:25:20', 0, NULL, 2),
(5, 'RAD-2026-004', 'admin_vvn', '$2b$12$4o4lqHmY0MDN8wksSvpXPeEI4wZ8dPqqi2XMwA8A.fH78QTZJ7BNa', 'Vidyanagar Dispensary Admin', 'region_admin', 'FAC-VVN-04', '+91 2692 230457', 'vvn.admin@anvayavistara.in', NULL, 1, 'en', 'active', NULL, 'Municipal Health Supervisor', '2026-09-05 22:21:01', '2026-09-06 12:33:51', 0, NULL, 2),
(6, 'RAD-2026-005', 'admin_gamdi', '$2b$12$4o4lqHmY0MDN8wksSvpXPeEI4wZ8dPqqi2XMwA8A.fH78QTZJ7BNa', 'Gamdi UPHC Administrator', 'region_admin', 'FAC-GAMDI-05', '+91 2692 245221', 'gamdi.admin@anvayavistara.in', NULL, 1, 'en', 'active', NULL, 'Urban Health Center Admin', '2026-09-05 22:21:01', '2026-09-06 12:33:51', 0, NULL, 2),
(7, 'RAD-2026-006', 'admin_zydus', '$2b$12$4o4lqHmY0MDN8wksSvpXPeEI4wZ8dPqqi2XMwA8A.fH78QTZJ7BNa', 'Zydus Trauma Centre Admin', 'region_admin', 'FAC-ZYDUS-06', '+91 2692 667001', 'zydus.admin@anvayavistara.in', NULL, 1, 'en', 'active', NULL, 'Hospital Operations Admin', '2026-09-05 22:21:01', '2026-09-06 12:33:51', 0, NULL, 2),
(8, 'RAD-2026-007', 'admin_bvm', '$2b$12$4o4lqHmY0MDN8wksSvpXPeEI4wZ8dPqqi2XMwA8A.fH78QTZJ7BNa', 'BVM SubCentre Administrator', 'region_admin', 'FAC-BVM-07', '+91 2692 230105', 'bvm.admin@anvayavistara.in', NULL, 1, 'en', 'active', NULL, 'SubCentre Field Coordinator', '2026-09-05 22:21:01', '2026-09-06 12:33:51', 0, NULL, 2),
(9, 'RAD-2026-008', 'admin_anand', '$2b$12$4o4lqHmY0MDN8wksSvpXPeEI4wZ8dPqqi2XMwA8A.fH78QTZJ7BNa', 'District Civil Hospital Admin', 'region_admin', 'FAC-CIVIL-08', '+91 2692 250101', 'anand.admin@anvayavistara.in', NULL, 1, 'en', 'active', NULL, 'District Administrative Officer', '2026-09-05 22:21:01', '2026-09-06 12:34:55', 5, '2026-09-06 12:49:55', 2),
(10, 'PHM-2026-001', 'vallabh.m', '$2b$12$xYbUC5Yx0lXq7ghmmrZAGujXcDSISmxtmTCMVYuL8qmehqIvdHE8G', 'Dr. Vallabh Mehrotra', 'doctor', 'FAC-BAKROL-01', '+91 98765 43210', 'vallabhmehrotra45@gmail.com', NULL, 1, 'en', 'active', NULL, 'Medical Officer / General Physician', '2026-09-05 22:21:01', '2026-09-06 13:24:07', 0, NULL, 2);

CREATE TABLE `vehicles` (
  `id` varchar(30) NOT NULL,
  `type` varchar(50) NOT NULL DEFAULT 'ambulance',
  `region` varchar(100) NOT NULL,
  `status` enum('available','dispatched','en_route','at_scene','returning','maintenance') NOT NULL DEFAULT 'available',
  `center_id` varchar(30) DEFAULT NULL,
  `driver_name` varchar(200) DEFAULT NULL,
  `driver_phone` varchar(20) DEFAULT NULL,
  `lat` decimal(10,7) DEFAULT NULL,
  `lng` decimal(10,7) DEFAULT NULL,
  `updated_at` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


INSERT INTO `vehicles` (`id`, `type`, `region`, `status`, `center_id`, `driver_name`, `driver_phone`, `lat`, `lng`, `updated_at`) VALUES
('AMB-BAKROL-01', 'Basic Life Support Ambulance', 'Vallabh Vidyanagar', 'available', 'FAC-BAKROL-01', 'Ramesh Kumar', '+91 98250 11223', 22.5488000, 72.9372000, '2026-09-05 22:21:01'),
('AMB-BAKROL-02', 'Patient Transport Vehicle', 'Vallabh Vidyanagar', 'on-duty', 'FAC-BAKROL-01', 'Dinesh Vaghela', '+91 98250 11224', 22.5502000, 72.9350000, '2026-09-06 08:12:45'),
('AMB-BAKROL-03', 'Basic Life Support Ambulance', 'Vallabh Vidyanagar', 'maintenance', 'FAC-BAKROL-01', 'Kiran Thakor', '+91 98250 11225', 22.5479000, 72.9391000, '2026-09-06 07:40:10'),
('AMB-BAKROL-04', 'Mobile ICU', 'Vallabh Vidyanagar', 'available', 'FAC-BAKROL-01', 'Vijay Rathod', '+91 98250 11226', 22.5495000, 72.9365000, '2026-09-06 09:05:30'),
('AMB-CIVIL-01', 'Trauma Emergency Ambulance', 'Anand', 'available', 'FAC-CIVIL-08', 'Mahesh Solanki', '+91 98250 77889', 22.5645000, 72.9585000, '2026-09-05 22:21:01'),
('AMB-CIVIL-02', 'Advanced Cardiac Life Support (ACLS)', 'Anand', 'on-duty', 'FAC-CIVIL-08', 'Prakash Chauhan', '+91 98250 77890', 22.5658000, 72.9601000, '2026-09-06 10:22:15'),
('AMB-CIVIL-03', 'Basic Life Support Ambulance', 'Anand', 'available', 'FAC-CIVIL-08', 'Nilesh Baria', '+91 98250 77891', 22.5631000, 72.9572000, '2026-09-06 06:55:00'),
('AMB-CIVIL-04', 'Patient Transport Vehicle', 'Anand', 'available', 'FAC-CIVIL-08', 'Ashok Rana', '+91 98250 77892', 22.5620000, 72.9598000, '2026-09-06 09:48:22'),
('AMB-CIVIL-05', 'Mobile ICU', 'Anand', 'out-of-service', 'FAC-CIVIL-08', 'Bharat Zala', '+91 98250 77893', 22.5649000, 72.9560000, '2026-09-06 05:30:12'),
('AMB-CIVIL-06', 'Trauma Emergency Ambulance', 'Anand', 'on-duty', 'FAC-CIVIL-08', 'Sanjay Parmar', '+91 98250 77894', 22.5662000, 72.9612000, '2026-09-06 11:02:40'),
('AMB-SKH-01', 'Advanced Cardiac Life Support (ACLS)', 'Karamsad', 'available', 'FAC-SKH-02', 'Suresh Patel', '+91 98250 44556', 22.5471000, 72.8986000, '2026-09-05 22:21:01'),
('AMB-SKH-02', 'Trauma Emergency Ambulance', 'Karamsad', 'available', 'FAC-SKH-02', 'Manoj Desai', '+91 98250 44557', 22.5460000, 72.9002000, '2026-09-06 07:15:05'),
('AMB-SKH-03', 'Basic Life Support Ambulance', 'Karamsad', 'on-duty', 'FAC-SKH-02', 'Yogesh Mistry', '+91 98250 44558', 22.5488000, 72.8970000, '2026-09-06 10:45:33'),
('AMB-SKH-04', 'Mobile ICU', 'Karamsad', 'available', 'FAC-SKH-02', 'Rajendra Solanki', '+91 98250 44559', 22.5452000, 72.8994000, '2026-09-06 08:30:18'),
('AMB-SKH-05', 'Patient Transport Vehicle', 'Karamsad', 'maintenance', 'FAC-SKH-02', 'Girish Trivedi', '+91 98250 44560', 22.5477000, 72.8955000, '2026-09-06 06:00:00'),
('AMB-GAMDI-01', 'Basic Life Support Ambulance', 'Gamdi', 'available', 'FAC-GAMDI-05', 'Hitesh Padhiyar', '+91 98250 33445', 22.5210000, 72.9455000, '2026-09-06 09:10:20'),
('AMB-GAMDI-02', 'Trauma Emergency Ambulance', 'Gamdi', 'on-duty', 'FAC-GAMDI-05', 'Jayesh Makwana', '+91 98250 33446', 22.5225000, 72.9470000, '2026-09-06 11:20:05'),
('AMB-GAMDI-03', 'Patient Transport Vehicle', 'Gamdi', 'available', 'FAC-GAMDI-05', 'Bipin Chavda', '+91 98250 33447', 22.5198000, 72.9440000, '2026-09-06 07:52:44'),
('AMB-GAMDI-04', 'Mobile ICU', 'Gamdi', 'available', 'FAC-GAMDI-05', 'Rakesh Dabhi', '+91 98250 33448', 22.5233000, 72.9482000, '2026-09-06 08:40:11'),
('AMB-GAMDI-05', 'Basic Life Support Ambulance', 'Gamdi', 'out-of-service', 'FAC-GAMDI-05', 'Naresh Vasava', '+91 98250 33449', 22.5205000, 72.9448000, '2026-09-06 05:15:30'),
('AMB-KARAMSAD-01', 'Advanced Cardiac Life Support (ACLS)', 'Karamsad', 'available', 'FAC-KARAMSAD-03', 'Chetan Bhatt', '+91 98250 55667', 22.5915000, 72.8460000, '2026-09-06 09:25:12'),
('AMB-KARAMSAD-02', 'Basic Life Support Ambulance', 'Karamsad', 'on-duty', 'FAC-KARAMSAD-03', 'Alpesh Joshi', '+91 98250 55668', 22.5928000, 72.8475000, '2026-09-06 10:55:00'),
('AMB-KARAMSAD-03', 'Trauma Emergency Ambulance', 'Karamsad', 'available', 'FAC-KARAMSAD-03', 'Devang Shah', '+91 98250 55669', 22.5902000, 72.8442000, '2026-09-06 07:33:28'),
('AMB-KARAMSAD-04', 'Patient Transport Vehicle', 'Karamsad', 'available', 'FAC-KARAMSAD-03', 'Paresh Vyas', '+91 98250 55670', 22.5940000, 72.8488000, '2026-09-06 08:18:47'),
('AMB-KARAMSAD-05', 'Mobile ICU', 'Karamsad', 'maintenance', 'FAC-KARAMSAD-03', 'Umang Pandya', '+91 98250 55671', 22.5895000, 72.8455000, '2026-09-06 06:20:33'),
('AMB-KARAMSAD-06', 'Basic Life Support Ambulance', 'Karamsad', 'available', 'FAC-KARAMSAD-03', 'Ketan Modi', '+91 98250 55672', 22.5920000, 72.8467000, '2026-09-06 09:58:10'),
('AMB-VVN-01', 'Trauma Emergency Ambulance', 'Vallabh Vidyanagar', 'available', 'FAC-VVN-04', 'Sandeep Chauhan', '+91 98250 66778', 22.5580000, 72.9160000, '2026-09-06 08:05:15'),
('AMB-VVN-02', 'Basic Life Support Ambulance', 'Vallabh Vidyanagar', 'on-duty', 'FAC-VVN-04', 'Nitin Barot', '+91 98250 66779', 22.5595000, 72.9175000, '2026-09-06 11:12:22'),
('AMB-VVN-03', 'Patient Transport Vehicle', 'Vallabh Vidyanagar', 'available', 'FAC-VVN-04', 'Anil Vaghela', '+91 98250 66780', 22.5567000, 72.9148000, '2026-09-06 07:20:00'),
('AMB-VVN-04', 'Advanced Cardiac Life Support (ACLS)', 'Vallabh Vidyanagar', 'available', 'FAC-VVN-04', 'Tarun Bhatt', '+91 98250 66781', 22.5602000, 72.9188000, '2026-09-06 09:35:44'),
('AMB-VVN-05', 'Mobile ICU', 'Vallabh Vidyanagar', 'out-of-service', 'FAC-VVN-04', 'Snehal Parekh', '+91 98250 66782', 22.5558000, 72.9139000, '2026-09-06 05:50:18'),
('AMB-ZYDUS-01', 'Basic Life Support Ambulance', 'Anand', 'available', 'FAC-ZYDUS-06', 'Harsh Panchal', '+91 98250 88990', 22.5390000, 72.9680000, '2026-09-06 08:48:29'),
('AMB-ZYDUS-02', 'Trauma Emergency Ambulance', 'Anand', 'on-duty', 'FAC-ZYDUS-06', 'Vipul Sindhav', '+91 98250 88991', 22.5405000, 72.9695000, '2026-09-06 10:30:52'),
('AMB-ZYDUS-03', 'Advanced Cardiac Life Support (ACLS)', 'Anand', 'available', 'FAC-ZYDUS-06', 'Mitesh Gohil', '+91 98250 88992', 22.5378000, 72.9662000, '2026-09-06 07:05:37'),
('AMB-ZYDUS-04', 'Patient Transport Vehicle', 'Anand', 'available', 'FAC-ZYDUS-06', 'Kalpesh Rathwa', '+91 98250 88993', 22.5412000, 72.9708000, '2026-09-06 09:15:00'),
('AMB-ZYDUS-05', 'Mobile ICU', 'Anand', 'maintenance', 'FAC-ZYDUS-06', 'Bhavesh Christian', '+91 98250 88994', 22.5369000, 72.9650000, '2026-09-06 06:42:14'),
('AMB-ZYDUS-06', 'Basic Life Support Ambulance', 'Anand', 'available', 'FAC-ZYDUS-06', 'Jignesh Solanki', '+91 98250 88995', 22.5398000, 72.9673000, '2026-09-06 08:22:05'),
('AMB-BAKROL-05', 'Trauma Emergency Ambulance', 'Vallabh Vidyanagar', 'available', 'FAC-BAKROL-01', 'Pratik Mehta', '+91 98250 11227', 22.5510000, 72.9340000, '2026-09-06 11:40:00'),
('AMB-BAKROL-06', 'Advanced Cardiac Life Support (ACLS)', 'Vallabh Vidyanagar', 'on-duty', 'FAC-BAKROL-01', 'Deepak Sarvaiya', '+91 98250 11228', 22.5465000, 72.9385000, '2026-09-06 10:05:19'),
('AMB-CIVIL-07', 'Basic Life Support Ambulance', 'Anand', 'available', 'FAC-CIVIL-08', 'Faisal Shaikh', '+91 98250 77895', 22.5638000, 72.9578000, '2026-09-06 09:00:00'),
('AMB-CIVIL-08', 'Patient Transport Vehicle', 'Anand', 'available', 'FAC-CIVIL-08', 'Imran Malek', '+91 98250 77896', 22.5610000, 72.9590000, '2026-09-06 07:48:10'),
('AMB-SKH-06', 'Trauma Emergency Ambulance', 'Karamsad', 'available', 'FAC-SKH-02', 'Ravindra Vora', '+91 98250 44561', 22.5495000, 72.8978000, '2026-09-06 08:55:35'),
('AMB-SKH-07', 'Basic Life Support Ambulance', 'Karamsad', 'out-of-service', 'FAC-SKH-02', 'Sunil Dave', '+91 98250 44562', 22.5443000, 72.9010000, '2026-09-06 05:05:00'),
('AMB-GAMDI-06', 'Advanced Cardiac Life Support (ACLS)', 'Gamdi', 'available', 'FAC-GAMDI-05', 'Ajay Rohit', '+91 98250 33450', 22.5218000, 72.9462000, '2026-09-06 10:10:48'),
('AMB-GAMDI-07', 'Trauma Emergency Ambulance', 'Gamdi', 'on-duty', 'FAC-GAMDI-05', 'Vishal Damor', '+91 98250 33451', 22.5241000, 72.9490000, '2026-09-06 11:25:33'),
('AMB-KARAMSAD-07', 'Mobile ICU', 'Karamsad', 'available', 'FAC-KARAMSAD-03', 'Manish Trivedi', '+91 98250 55673', 22.5910000, 72.8450000, '2026-09-06 09:42:00');

ALTER TABLE `appointments`
  ADD PRIMARY KEY (`id`),
  ADD KEY `doctor_id` (`doctor_id`),
  ADD KEY `idx_appt_center_date` (`center_id`,`slot_time`),
  ADD KEY `idx_appt_patient` (`patient_id`);

ALTER TABLE `audit_logs`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_audit_user` (`user_id`),
  ADD KEY `idx_audit_entity` (`entity_type`,`entity_id`),
  ADD KEY `idx_audit_time` (`created_at`);

ALTER TABLE `centers`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_center_type` (`type`),
  ADD KEY `idx_center_region` (`region`);

ALTER TABLE `follow_ups`
  ADD PRIMARY KEY (`id`),
  ADD KEY `patient_id` (`patient_id`),
  ADD KEY `idx_fu_due` (`due_date`,`status`),
  ADD KEY `idx_fu_assigned` (`assigned_to`);


ALTER TABLE `inventory_items`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_inv_center` (`center_id`),
  ADD KEY `idx_inv_expiry` (`expiry_date`);

ALTER TABLE `lab_records`
  ADD PRIMARY KEY (`id`),
  ADD KEY `center_id` (`center_id`),
  ADD KEY `ordered_by` (`ordered_by`),
  ADD KEY `idx_lab_patient` (`patient_id`),
  ADD KEY `idx_lab_status` (`status`);

ALTER TABLE `medical_records`
  ADD PRIMARY KEY (`id`),
  ADD KEY `created_by` (`created_by`),
  ADD KEY `idx_mr_patient` (`patient_id`),
  ADD KEY `idx_mr_center` (`center_id`);

ALTER TABLE `notifications`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_notif_user_read` (`user_id`,`is_read`);

ALTER TABLE `patients`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `linked_user_id` (`linked_user_id`),
  ADD KEY `idx_patient_name` (`full_name`),
  ADD KEY `idx_patient_center` (`center_id`);

ALTER TABLE `prescriptions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `record_id` (`record_id`),
  ADD KEY `prescribed_by` (`prescribed_by`),
  ADD KEY `idx_rx_patient` (`patient_id`),
  ADD KEY `idx_rx_center` (`center_id`);

ALTER TABLE `referrals`
  ADD PRIMARY KEY (`id`),
  ADD KEY `patient_id` (`patient_id`),
  ADD KEY `created_by` (`created_by`),
  ADD KEY `accepted_by` (`accepted_by`),
  ADD KEY `idx_ref_from` (`from_center`),
  ADD KEY `idx_ref_to` (`to_center`),
  ADD KEY `idx_ref_status` (`status`);

ALTER TABLE `role_permissions`
  ADD PRIMARY KEY (`role`,`action`);

ALTER TABLE `teleconsult_messages`
  ADD PRIMARY KEY (`id`),
  ADD KEY `sender_id` (`sender_id`),
  ADD KEY `idx_tcm_session` (`session_id`,`sent_at`);

ALTER TABLE `teleconsult_sessions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `patient_id` (`patient_id`),
  ADD KEY `center_id` (`center_id`),
  ADD KEY `idx_tc_doctor` (`doctor_id`),
  ADD KEY `idx_tc_status` (`status`);

ALTER TABLE `triage_entries`
  ADD PRIMARY KEY (`id`),
  ADD KEY `patient_id` (`patient_id`),
  ADD KEY `assessed_by` (`assessed_by`),
  ADD KEY `idx_tri_center` (`center_id`),
  ADD KEY `idx_tri_urgency` (`urgency_score`);

ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `staff_id` (`staff_id`),
  ADD KEY `idx_user_role` (`role`),
  ADD KEY `idx_user_center` (`center_id`);

ALTER TABLE `vehicles`
  ADD PRIMARY KEY (`id`),
  ADD KEY `center_id` (`center_id`),
  ADD KEY `idx_veh_status` (`status`),
  ADD KEY `idx_veh_region` (`region`);

ALTER TABLE `appointments`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=110;

ALTER TABLE `audit_logs`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=675;

ALTER TABLE `follow_ups`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `inventory_items`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8081;

ALTER TABLE `lab_records`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `medical_records`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=54;

ALTER TABLE `notifications`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=591;

ALTER TABLE `prescriptions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=52;

ALTER TABLE `referrals`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=90;

ALTER TABLE `teleconsult_messages`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=72;

ALTER TABLE `teleconsult_sessions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=39;

ALTER TABLE `triage_entries`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=20;

ALTER TABLE `appointments`
  ADD CONSTRAINT `1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `2` FOREIGN KEY (`center_id`) REFERENCES `centers` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `3` FOREIGN KEY (`doctor_id`) REFERENCES `users` (`id`) ON DELETE SET NULL;

ALTER TABLE `audit_logs`
  ADD CONSTRAINT `1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL;

ALTER TABLE `follow_ups`
  ADD CONSTRAINT `1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `2` FOREIGN KEY (`assigned_to`) REFERENCES `users` (`id`) ON DELETE SET NULL;

ALTER TABLE `inventory_items`
  ADD CONSTRAINT `1` FOREIGN KEY (`center_id`) REFERENCES `centers` (`id`) ON DELETE CASCADE;

ALTER TABLE `lab_records`
  ADD CONSTRAINT `1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `2` FOREIGN KEY (`center_id`) REFERENCES `centers` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `3` FOREIGN KEY (`ordered_by`) REFERENCES `users` (`id`) ON DELETE CASCADE;

ALTER TABLE `medical_records`
  ADD CONSTRAINT `1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `2` FOREIGN KEY (`center_id`) REFERENCES `centers` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `3` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE CASCADE;

ALTER TABLE `notifications`
  ADD CONSTRAINT `1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

ALTER TABLE `patients`
  ADD CONSTRAINT `1` FOREIGN KEY (`linked_user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `2` FOREIGN KEY (`center_id`) REFERENCES `centers` (`id`) ON DELETE SET NULL;

ALTER TABLE `prescriptions`
  ADD CONSTRAINT `1` FOREIGN KEY (`record_id`) REFERENCES `medical_records` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `2` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `3` FOREIGN KEY (`prescribed_by`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `4` FOREIGN KEY (`center_id`) REFERENCES `centers` (`id`) ON DELETE CASCADE;

ALTER TABLE `referrals`
  ADD CONSTRAINT `1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `2` FOREIGN KEY (`from_center`) REFERENCES `centers` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `3` FOREIGN KEY (`to_center`) REFERENCES `centers` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `4` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `5` FOREIGN KEY (`accepted_by`) REFERENCES `users` (`id`) ON DELETE SET NULL;

ALTER TABLE `teleconsult_messages`
  ADD CONSTRAINT `1` FOREIGN KEY (`session_id`) REFERENCES `teleconsult_sessions` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `2` FOREIGN KEY (`sender_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

ALTER TABLE `teleconsult_sessions`
  ADD CONSTRAINT `1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `2` FOREIGN KEY (`doctor_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `3` FOREIGN KEY (`center_id`) REFERENCES `centers` (`id`) ON DELETE CASCADE;

ALTER TABLE `triage_entries`
  ADD CONSTRAINT `1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `2` FOREIGN KEY (`center_id`) REFERENCES `centers` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `3` FOREIGN KEY (`assessed_by`) REFERENCES `users` (`id`) ON DELETE CASCADE;

ALTER TABLE `users`
  ADD CONSTRAINT `1` FOREIGN KEY (`center_id`) REFERENCES `centers` (`id`) ON DELETE SET NULL;


ALTER TABLE `vehicles`
  ADD CONSTRAINT `1` FOREIGN KEY (`center_id`) REFERENCES `centers` (`id`) ON DELETE SET NULL;
COMMIT;
