# 🏛️ ΛΕΠΤΟΜΕΡΕΣ DATABASE SCHEMA - ΣΥΣΤΗΜΑ ΑΔΕΙΩΝ ΠΔΕΔΕ

## 📋 ΠΕΡΙΕΧΟΜΕΝΑ
1. [Βασικοί Πίνακες Αναφοράς](#1-βασικοί-πίνακες-αναφοράς)
2. [Οργανωτική Δομή](#2-οργανωτική-δομή)
3. [Χρήστες & Υπάλληλοι](#3-χρήστες--υπάλληλοι)
4. [Άδειες & Workflow](#4-άδειες--workflow)
5. [Αργίες & Ημερολόγιο](#5-αργίες--ημερολόγιο)
6. [Audit & Logs](#6-audit--logs)
7. [GDPR & Security](#7-gdpr--security)
8. [Django Models](#8-django-models)

---

## 1. ΒΑΣΙΚΟΙ ΠΙΝΑΚΕΣ ΑΝΑΦΟΡΑΣ

### 1.1 employee_types
```sql
CREATE TABLE employee_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Προκαθορισμένα δεδομένα
INSERT INTO employee_types (name, description) VALUES 
('Διοικητικοί', 'Διοικητικό προσωπικό'),
('Εκπαιδευτικοί', 'Εκπαιδευτικό προσωπικό'),
('Αναπληρωτές', 'Αναπληρωτές εκπαιδευτικοί'),
('Κέντρο Στήριξης ΣΔΕΥ', 'Υπεύθυνοι Κέντρου Στήριξης ΣΔΕΥ'),
('Δ/ντές Εκπαίδευσης', 'Διευθυντές Εκπαίδευσης'),
('Άλλο', 'Άλλες κατηγορίες προσωπικού');
```

### 1.2 specialties
```sql
CREATE TABLE specialties (
    id SERIAL PRIMARY KEY,
    specialty_full VARCHAR(200) NOT NULL,
    specialty_short VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(specialty_full),
    UNIQUE(specialty_short)
);

-- Παράδειγμα δεδομένων
INSERT INTO specialties (specialty_full, specialty_short) VALUES 
('ΔΕ1 - ΔΕ ΔΙΟΙΚΗΤΙΚΟΥ-ΛΟΓΙΣΤΙΚΟΥ', 'ΔΕ1'),
('ΠΕ ΠΛΗΡΟΦΟΡΙΚΗΣ', 'ΠΕ'),
('ΥΕ ΔΙΟΙΚΗΤΙΚΟΥ', 'ΥΕ');
```

### 1.3 leave_types
```sql
CREATE TABLE leave_types (
    id SERIAL PRIMARY KEY,
    id_adeias VARCHAR(50) UNIQUE NOT NULL,
    eidos_adeias VARCHAR(200) NOT NULL,
    eidos_adeias_aplo VARCHAR(100) NOT NULL,
    keimeno_thematos_adeia TEXT NOT NULL,
    keimeno_apofasis_adeia TEXT NOT NULL,
    thematikos_fakelos VARCHAR(200),
    requires_manager_approval BOOLEAN DEFAULT TRUE,
    requires_attachments BOOLEAN DEFAULT FALSE,
    requires_protocol BOOLEAN DEFAULT TRUE,
    requires_decision_pdf BOOLEAN DEFAULT TRUE,
    bypass_manager_for_sick_leave BOOLEAN DEFAULT FALSE, -- για αναρρωτικές
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Παραδείγματα τύπων αδειών
INSERT INTO leave_types (id_adeias, eidos_adeias, eidos_adeias_aplo, keimeno_thematos_adeia, keimeno_apofasis_adeia, requires_manager_approval, requires_protocol, requires_decision_pdf) VALUES 
('KANONIKI', 'Κανονική Άδεια', 'Κανονική', 'Χορήγηση κανονικής άδειας', 'κανονική άδεια', TRUE, TRUE, TRUE),
('ANARROTIKI', 'Αναρρωτική Άδεια', 'Αναρρωτική', 'Χορήγηση αναρρωτικής άδειας', 'αναρρωτική άδεια', FALSE, TRUE, TRUE),
('AIMODOSIA', 'Άδεια Αιμοδοσίας', 'Αιμοδοσία', 'Χορήγηση άδειας αιμοδοσίας', 'άδεια αιμοδοσίας', TRUE, TRUE, TRUE),
('PROFORIKI', 'Προφορική Άδεια', 'Προφορική', 'Προφορική άδεια', 'προφορική άδεια', TRUE, FALSE, FALSE),
('EORTASTIKI', 'Εορταστική Άδεια', 'Εορταστική', 'Εορταστική άδεια', 'εορταστική άδεια', TRUE, FALSE, FALSE),
('EPIMORFOSI', 'Άδεια Επιμόρφωσης', 'Επιμόρφωση', 'Άδεια επιμόρφωσης', 'άδεια επιμόρφωσης', TRUE, FALSE, FALSE);
```

---

## 2. ΟΡΓΑΝΩΤΙΚΗ ΔΟΜΗ

### 2.1 cities
```sql
CREATE TABLE cities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    prefecture VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

INSERT INTO cities (name, prefecture) VALUES 
('Πάτρα', 'Αχαΐα'),
('Μεσολόγγι', 'Αιτωλοακαρνανία'),
('Πύργος', 'Ηλεία'),
('Κλειτορία', 'Αχαΐα'),
('Κρέστενα', 'Ηλεία');
```

### 2.2 service_types
```sql
CREATE TABLE service_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    abbreviation VARCHAR(20),
    level INTEGER NOT NULL, -- 1=ΠΔΕΔΕ, 2=ΚΕΔΑΣΥ/ΚΕΠΕΑ, 3=ΣΔΕΥ
    requires_kedasy_protocol BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

INSERT INTO service_types (name, abbreviation, level, requires_kedasy_protocol) VALUES 
('ΠΕΡΙΦΕΡΕΙΑΚΗ ΔΙΕΥΘΥΝΣΗ', 'ΠΔΕΔΕ', 1, FALSE),
('ΚΕΔΑΣΥ', 'ΚΕΔΑΣΥ', 2, TRUE),
('ΚΕΠΕΑ', 'ΚΕΠΕΑ', 2, TRUE),
('ΣΔΕΥ', 'ΣΔΕΥ', 3, TRUE);
```

### 2.3 services
```sql
CREATE TABLE services (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    full_name VARCHAR(500),
    service_type_id INTEGER REFERENCES service_types(id),
    parent_service_id INTEGER REFERENCES services(id), -- για ιεραρχία
    city_id INTEGER REFERENCES cities(id),
    manager_id INTEGER REFERENCES employees(id), -- προϊστάμενος
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Κύρια ΠΔΕΔΕ
INSERT INTO services (name, full_name, service_type_id, city_id) VALUES 
('ΠΔΕΔΕ', 'Περιφερειακή Διεύθυνση Εκπαίδευσης Δυτικής Ελλάδας', 1, 1);

-- ΚΕΔΑΣΥ
INSERT INTO services (name, full_name, service_type_id, parent_service_id, city_id) VALUES 
('ΚΕΔΑΣΥ 1ο ΠΑΤΡΑΣ', 'ΚΕΔΑΣΥ 1ο ΠΑΤΡΑΣ', 2, 1, 1),
('ΚΕΔΑΣΥ 2ο ΠΑΤΡΑΣ', 'ΚΕΔΑΣΥ 2ο ΠΑΤΡΑΣ', 2, 1, 1),
('ΚΕΔΑΣΥ ΑΙΤ/ΝΙΑΣ', 'ΚΕΔΑΣΥ ΑΙΤΩΛΟΑΚΑΡΝΑΝΙΑΣ', 2, 1, 2),
('ΚΕΔΑΣΥ ΗΛΕΙΑΣ', 'ΚΕΔΑΣΥ ΗΛΕΙΑΣ', 2, 1, 3);

-- ΚΕΠΕΑ
INSERT INTO services (name, full_name, service_type_id, parent_service_id, city_id) VALUES 
('ΚΕΠΕΑ ΑΧΑΙΑΣ', 'ΚΕΠΕΑ ΑΧΑΙΑΣ', 3, 1, 4),
('ΚΕΠΕΑ ΗΛΕΙΑΣ', 'ΚΕΠΕΑ ΗΛΕΙΑΣ', 3, 1, 5),
('ΚΕΠΕΑ ΑΙΤΝΙΑΣ', 'ΚΕΠΕΑ ΑΙΤΩΛΟΑΚΑΡΝΑΝΙΑΣ', 3, 1, 2);
```

### 2.4 departments
```sql
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    service_id INTEGER NOT NULL REFERENCES services(id),
    manager_id INTEGER REFERENCES employees(id),
    parent_department_id INTEGER REFERENCES departments(id),
    is_virtual BOOLEAN DEFAULT FALSE, -- για ΣΔΕΥ
    sdeu_supervisor_id INTEGER REFERENCES employees(id), -- για ΣΔΕΥ
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(name, service_id)
);

-- Τμήματα ΠΔΕΔΕ
INSERT INTO departments (name, service_id) VALUES 
('ΑΥΤΟΤΕΛΗΣ ΔΙΕΥΘΥΝΣΗ', 1),
('ΤΜΗΜΑ Α', 1),
('ΤΜΗΜΑ Β', 1),
('ΤΜΗΜΑ Γ', 1),
('ΤΜΗΜΑ Δ', 1),
('ΓΡΑΦΕΙΟ ΝΟΜΙΚΗΣ', 1);

-- ΣΔΕΥ (εικονικά τμήματα)
INSERT INTO departments (name, service_id, is_virtual) VALUES 
('ΣΔΕΥ1', 2, TRUE),
('ΣΔΕΥ2', 2, TRUE),
('ΣΔΕΥ3', 2, TRUE),
('ΣΔΕΥ11', 3, TRUE),
('ΣΔΕΥ12', 3, TRUE),
('ΣΔΕΥ13', 3, TRUE);
```

---

## 3. ΧΡΗΣΤΕΣ & ΥΠΑΛΛΗΛΟΙ

### 3.1 roles
```sql
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    permissions JSONB, -- Django permissions
    is_system_role BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

INSERT INTO roles (name, description, is_system_role) VALUES 
('Administrator', 'Διαχειριστής συστήματος', TRUE),
('Χειριστής αδειών', 'Υπάλληλος διαχείρισης αδειών', TRUE),
('Προϊστάμενος τμήματος', 'Προϊστάμενος τμήματος', TRUE),
('Υπεύθυνος Κέντρου Στήριξης ΣΔΕΥ', 'Υπεύθυνος ΣΔΕΥ', TRUE),
('Γραμματέας ΚΕΔΑΣΥ', 'Γραμματέας ΚΕΔΑΣΥ', TRUE),
('Περιφερειακός Διευθυντής', 'Περιφερειακός Διευθυντής', TRUE),
('Υπεύθυνος ΕΣΠΑ', 'Υπεύθυνος ΕΣΠΑ', TRUE),
('Υπάλληλος', 'Βασικός χρήστης', TRUE);
```

### 3.2 employees (επέκταση του Django User)
```sql
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    
    -- Προσωπικά στοιχεία
    name_in_accusative VARCHAR(100) NOT NULL,
    surname_in_accusative VARCHAR(100) NOT NULL,
    father_name_in_genitive VARCHAR(100),
    gender VARCHAR(10) CHECK (gender IN ('Άνδρας', 'Γυναίκα')),
    
    -- Επικοινωνία
    sch_email VARCHAR(200) UNIQUE NOT NULL CHECK (sch_email LIKE '%@sch.gr'),
    personal_email VARCHAR(200),
    phone1 VARCHAR(20),
    phone2 VARCHAR(20),
    
    -- Υπηρεσιακά στοιχεία
    specialty_id INTEGER REFERENCES specialties(id),
    employee_type_id INTEGER REFERENCES employee_types(id),
    current_service_id INTEGER REFERENCES services(id),
    department_id INTEGER REFERENCES departments(id),
    role_description TEXT,
    
    -- Άδειες
    regular_leave_days INTEGER DEFAULT 24,
    carryover_leave_days INTEGER DEFAULT 0,
    self_declaration_sick_days_remaining INTEGER DEFAULT 2,
    
    -- Ειδοποιήσεις
    notification_recipients TEXT,
    preferred_notification_email VARCHAR(200), -- sch_email ή personal_email
    
    -- Ρυθμίσεις
    schedule VARCHAR(200), -- ωράριο
    can_request_leave BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_notification_email CHECK (
        preferred_notification_email IN (sch_email, personal_email) OR 
        preferred_notification_email IS NULL
    )
);

-- Indexes για performance
CREATE INDEX idx_employees_sch_email ON employees(sch_email);
CREATE INDEX idx_employees_service ON employees(current_service_id);
CREATE INDEX idx_employees_department ON employees(department_id);
CREATE INDEX idx_employees_active ON employees(is_active);
```

### 3.3 user_roles (Many-to-Many για πολλαπλούς ρόλους)
```sql
CREATE TABLE user_roles (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    role_id INTEGER NOT NULL REFERENCES roles(id),
    assigned_by_id INTEGER REFERENCES employees(id),
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    
    UNIQUE(employee_id, role_id)
);
```

---

## 4. ΑΔΕΙΕΣ & WORKFLOW

### 4.1 leave_statuses
```sql
CREATE TABLE leave_statuses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    color_code VARCHAR(7), -- HEX color
    is_final_status BOOLEAN DEFAULT FALSE,
    order_priority INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

INSERT INTO leave_statuses (name, description, color_code, is_final_status, order_priority) VALUES 
('ΚΑΤΑΧΩΡΗΘΗΚΕ', 'Καταχωρήθηκε η αίτηση', '#FFA500', FALSE, 1),
('ΕΓΚΡΙΣΗ_ΑΠΟ_ΠΡΟΪΣΤΑΜΕΝΟ', 'Προς έγκριση από προϊστάμενο', '#FFE4B5', FALSE, 2),
('ΓΙΑ_ΠΡΩΤΟΚΟΛΛΟ_ΚΕΔΑΣΥ', 'Για πρωτόκολλο ΚΕΔΑΣΥ/ΚΕΠΕΑ', '#87CEEB', FALSE, 3),
('ΓΙΑ_ΠΡΩΤΟΚΟΛΛΟ_ΠΔΕΔΕ', 'Για πρωτόκολλο ΠΔΕΔΕ', '#87CEFA', FALSE, 4),
('ΠΡΟΣ_ΕΠΕΞΕΡΓΑΣΙΑ', 'Προς επεξεργασία', '#98FB98', FALSE, 5),
('ΕΠΕΞΕΡΓΑΣΙΑ', 'Υπό επεξεργασία', '#90EE90', FALSE, 6),
('ΑΝΑΜΟΝΗ_ΔΙΚΑΙΟΛΟΓΗΤΙΚΩΝ', 'Αναμονή δικαιολογητικών', '#F0E68C', FALSE, 7),
('ΥΓΕΙΟΝΟΜΙΚΗ_ΕΠΙΤΡΟΠΗ', 'Υγειονομική επιτροπή', '#DDA0DD', FALSE, 8),
('ΣΗΔΕ_ΠΡΟΣ_ΥΠΟΓΡΑΦΕΣ', 'ΣΗΔΕ - Προς υπογραφές', '#B0C4DE', FALSE, 9),
('ΟΛΟΚΛΗΡΩΜΕΝΗ', 'Ολοκληρωμένη', '#90EE90', TRUE, 10),
('ΜΗ_ΕΓΚΡΙΣΗ_ΑΠΟ_ΠΡΟΪΣΤΑΜΕΝΟ', 'Μη έγκριση από προϊστάμενο', '#FF6347', TRUE, 11),
('ΑΠΟΡΡΙΨΗ_ΑΠΟ_ΤΜΗΜΑ_ΑΔΕΙΩΝ', 'Απόρριψη από τμήμα αδειών', '#FF4500', TRUE, 12),
('ΑΝΑΚΛΗΣΗ_ΑΙΤΗΣΗΣ_ΑΠΟ_ΑΙΤΟΥΝΤΑ', 'Ανάκληση αίτησης από αιτούντα', '#D3D3D3', TRUE, 13),
('ΑΝΑΚΛΗΣΗ_ΟΛΟΚΛΗΡΩΜΕΝΗΣ_ΑΔΕΙΑΣ', 'Ανάκληση ολοκληρωμένης άδειας', '#C0C0C0', FALSE, 14);
```

### 4.2 leave_requests
```sql
CREATE TABLE leave_requests (
    id SERIAL PRIMARY KEY,
    
    -- Βασικά στοιχεία
    employee_id INTEGER NOT NULL REFERENCES employees(id),
    leave_type_id INTEGER NOT NULL REFERENCES leave_types(id),
    status_id INTEGER NOT NULL REFERENCES leave_statuses(id),
    
    -- Διαστήματα άδειας (υπολογίζεται από periods)
    total_days INTEGER NOT NULL DEFAULT 0,
    working_days INTEGER NOT NULL DEFAULT 0, -- αφαιρώντας Σ/Κ και αργίες
    
    -- Ειδικά πεδία
    description TEXT, -- για προφορικές/εορταστικές
    is_self_declaration BOOLEAN DEFAULT FALSE, -- αναρρωτικές με υπ. δήλωση
    comments_to_leave_department TEXT, -- σχόλια προς χειριστές αδειών
    
    -- Πρωτόκολλα
    kedasy_protocol_number VARCHAR(100),
    kedasy_protocol_date DATE,
    pdede_protocol_number VARCHAR(100),
    pdede_protocol_date DATE,
    
    -- Εγκρίσεις
    manager_approved_at TIMESTAMP WITH TIME ZONE,
    manager_approved_by_id INTEGER REFERENCES employees(id),
    manager_rejection_reason TEXT,
    
    -- Επεξεργασία
    processed_by_id INTEGER REFERENCES employees(id),
    processed_at TIMESTAMP WITH TIME ZONE,
    processing_notes TEXT,
    
    -- Τμήμα αδειών
    leave_dept_rejection_reason TEXT,
    required_documents TEXT, -- για ΑΝΑΜΟΝΗ_ΔΙΚΑΙΟΛΟΓΗΤΙΚΩΝ
    
    -- Υγειονομική επιτροπή
    health_committee_decision VARCHAR(50), -- 'Εγκρίθηκε'/'Απορρίφθηκε'
    health_committee_notes TEXT,
    health_committee_decided_at TIMESTAMP WITH TIME ZONE,
    
    -- Parent/Child relationships για ανακλήσεις
    parent_leave_id INTEGER REFERENCES leave_requests(id),
    is_cancellation BOOLEAN DEFAULT FALSE,
    is_partial_cancellation BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by_id INTEGER REFERENCES employees(id), -- για χειριστές που κάνουν αίτηση για άλλους
    
    -- Constraints
    CONSTRAINT positive_days CHECK (total_days > 0),
    CONSTRAINT valid_kedasy_protocol CHECK (
        (kedasy_protocol_number IS NULL AND kedasy_protocol_date IS NULL) OR
        (kedasy_protocol_number IS NOT NULL AND kedasy_protocol_date IS NOT NULL)
    )
);

-- Indexes
CREATE INDEX idx_leave_requests_employee ON leave_requests(employee_id);
CREATE INDEX idx_leave_requests_status ON leave_requests(status_id);
CREATE INDEX idx_leave_requests_created ON leave_requests(created_at);
CREATE INDEX idx_leave_requests_type ON leave_requests(leave_type_id);
```

### 4.3 leave_request_periods
```sql
CREATE TABLE leave_request_periods (
    id SERIAL PRIMARY KEY,
    leave_request_id INTEGER NOT NULL REFERENCES leave_requests(id) ON DELETE CASCADE,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    total_days INTEGER NOT NULL,
    working_days INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_period CHECK (end_date >= start_date)
);

CREATE INDEX idx_leave_periods_request ON leave_request_periods(leave_request_id);
CREATE INDEX idx_leave_periods_dates ON leave_request_periods(start_date, end_date);
```

### 4.4 leave_attachments
```sql
CREATE TABLE leave_attachments (
    id SERIAL PRIMARY KEY,
    leave_request_id INTEGER NOT NULL REFERENCES leave_requests(id) ON DELETE CASCADE,
    
    -- Αρχείο
    file_name VARCHAR(255) NOT NULL,
    original_file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER NOT NULL,
    file_type VARCHAR(10) NOT NULL CHECK (file_type IN ('PDF', 'JPG', 'JPEG')),
    file_hash VARCHAR(64), -- για integrity checking
    
    -- Περιγραφή (υποχρεωτική)
    description TEXT NOT NULL,
    
    -- Τύπος συνημμένου
    attachment_type VARCHAR(50) DEFAULT 'SUPPORTING_DOCUMENT',
    -- Τύποι: SUPPORTING_DOCUMENT, APPLICATION_PDF, DECISION_PDF, PROTOCOL_PDF
    
    -- Ασφάλεια
    is_sensitive BOOLEAN DEFAULT FALSE, -- για αναρρωτικές
    uploaded_by_id INTEGER NOT NULL REFERENCES employees(id),
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT max_file_size CHECK (file_size <= 5242880) -- 5MB
);

CREATE INDEX idx_attachments_request ON leave_attachments(leave_request_id);
CREATE INDEX idx_attachments_type ON leave_attachments(attachment_type);
```

---

## 5. ΑΡΓΙΕΣ & ΗΜΕΡΟΛΟΓΙΟ

### 5.1 public_holidays
```sql
CREATE TABLE public_holidays (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    date DATE NOT NULL,
    year INTEGER NOT NULL,
    is_fixed BOOLEAN DEFAULT TRUE, -- FALSE για κινητές εορτές
    is_national BOOLEAN DEFAULT TRUE, -- FALSE για τοπικές
    city_id INTEGER REFERENCES cities(id), -- NULL για εθνικές
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(date, city_id) -- αποτροπή διπλών εγγραφών
);

-- Παραδείγματα
INSERT INTO public_holidays (name, date, year, is_fixed, is_national) VALUES 
('Πρωτοχρονιά', '2025-01-01', 2025, TRUE, TRUE),
('Θεοφάνεια', '2025-01-06', 2025, TRUE, TRUE),
('25η Μαρτίου', '2025-03-25', 2025, TRUE, TRUE),
('Πρωτομαγιά', '2025-05-01', 2025, TRUE, TRUE),
('15 Αυγούστου', '2025-08-15', 2025, TRUE, TRUE),
('28η Οκτωβρίου', '2025-10-28', 2025, TRUE, TRUE),
('Χριστούγεννα', '2025-12-25', 2025, TRUE, TRUE),
('Δεύτερα των Χριστουγέννων', '2025-12-26', 2025, TRUE, TRUE);

-- Τοπικές αργίες
INSERT INTO public_holidays (name, date, year, is_fixed, is_national, city_id) VALUES 
('Άγιος Ανδρέας', '2025-11-30', 2025, TRUE, FALSE, 1); -- Πάτρα
```

### 5.2 holiday_overlap_checks (για έλεγχο επικαλύψεων)
```sql
CREATE TABLE holiday_overlap_checks (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    city_id INTEGER REFERENCES cities(id),
    holiday_count INTEGER DEFAULT 1,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(date, city_id)
);
```

---

## 6. AUDIT & LOGS

### 6.1 leave_action_logs
```sql
CREATE TABLE leave_action_logs (
    id SERIAL PRIMARY KEY,
    leave_request_id INTEGER NOT NULL REFERENCES leave_requests(id),
    
    -- Αλλαγή κατάστασης
    previous_status_id INTEGER REFERENCES leave_statuses(id),
    new_status_id INTEGER NOT NULL REFERENCES leave_statuses(id),
    
    -- Ποιος έκανε την ενέργεια
    user_id INTEGER NOT NULL REFERENCES employees(id),
    action VARCHAR(100) NOT NULL, -- 'STATUS_CHANGE', 'APPROVAL', 'REJECTION', etc.
    
    -- Λεπτομέρειες
    notes TEXT,
    ip_address INET,
    user_agent TEXT,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_logs_leave_request ON leave_action_logs(leave_request_id);
CREATE INDEX idx_logs_user ON leave_action_logs(user_id);
CREATE INDEX idx_logs_created ON leave_action_logs(created_at);
```

### 6.2 employee_history
```sql
CREATE TABLE employee_history (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employees(id),
    
    -- Τι άλλαξε
    field_name VARCHAR(100) NOT NULL,
    previous_value TEXT,
    new_value TEXT,
    
    -- Ποιος έκανε την αλλαγή
    changed_by_id INTEGER NOT NULL REFERENCES employees(id),
    change_reason TEXT,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_employee_history_employee ON employee_history(employee_id);
CREATE INDEX idx_employee_history_field ON employee_history(field_name);
```

### 6.3 system_logs
```sql
CREATE TABLE system_logs (
    id SERIAL PRIMARY KEY,
    level VARCHAR(20) NOT NULL, -- DEBUG, INFO, WARNING, ERROR, CRITICAL
    message TEXT NOT NULL,
    module VARCHAR(100),
    function_name VARCHAR(100),
    user_id INTEGER REFERENCES employees(id),
    ip_address INET,
    extra_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_system_logs_level ON system_logs(level);
CREATE INDEX idx_system_logs_created ON system_logs(created_at);
CREATE INDEX idx_system_logs_user ON system_logs(user_id);
```

---

## 7. GDPR & SECURITY

### 7.1 gdpr_consents
```sql
CREATE TABLE gdpr_consents (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employees(id),
    consent_text TEXT NOT NULL,
    consent_version VARCHAR(20) NOT NULL,
    ip_address INET,
    user_agent TEXT,
    consented_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_gdpr_consents_employee ON gdpr_consents(employee_id);
```

### 7.2 document_verifications
```sql
CREATE TABLE document_verifications (
    id SERIAL PRIMARY KEY,
    document_uuid UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    leave_request_id INTEGER REFERENCES leave_requests(id),
    attachment_id INTEGER REFERENCES leave_attachments(id),
    
    -- Τύπος εγγράφου
    document_type VARCHAR(50) NOT NULL, -- 'APPLICATION', 'DECISION'
    
    -- Στοιχεία εγγράφου
    document_title VARCHAR(200),
    document_hash VARCHAR(64),
    created_by_id INTEGER NOT NULL REFERENCES employees(id),
    
    -- Verification info
    is_active BOOLEAN DEFAULT TRUE,
    verified_count INTEGER DEFAULT 0,
    last_verified_at TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_document_verifications_uuid ON document_verifications(document_uuid);
```

### 7.3 access_logs (GDPR compliance)
```sql
CREATE TABLE access_logs (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employees(id), -- ποιος είδε
    viewed_employee_id INTEGER REFERENCES employees(id), -- ποιου τα δεδομένα
    leave_request_id INTEGER REFERENCES leave_requests(id),
    attachment_id INTEGER REFERENCES leave_attachments(id),
    
    -- Τύπος πρόσβασης
    access_type VARCHAR(50) NOT NULL, -- 'VIEW', 'DOWNLOAD', 'EDIT', 'DELETE'
    url_path VARCHAR(500),
    
    -- Metadata
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_access_logs_employee ON access_logs(employee_id);
CREATE INDEX idx_access_logs_viewed ON access_logs(viewed_employee_id);
CREATE INDEX idx_access_logs_created ON access_logs(created_at);
```

---

## 8. ΕΠΙΠΛΕΟΝ ΠΙΝΑΚΕΣ

### 8.1 system_settings
```sql
CREATE TABLE system_settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT,
    description TEXT,
    is_system BOOLEAN DEFAULT FALSE,
    updated_by_id INTEGER REFERENCES employees(id),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Προκαθορισμένες ρυθμίσεις
INSERT INTO system_settings (key, value, description, is_system) VALUES 
('DEFAULT_REGULAR_LEAVE_DAYS', '24', 'Προεπιλεγμένες ημέρες κανονικής άδειας', TRUE),
('SYSTEM_EMAIL_FROM', 'noreply@sch.gr', 'Email αποστολέα συστήματος', TRUE),
('PDF_HEADER_LOGO_TEXT', 'ΕΛΛΗΝΙΚΗ ΔΗΜΟΚΡΑΤΙΑ...', 'Κείμενο επικεφαλίδας PDF', FALSE),
('WORKING_DAYS_PER_WEEK', '5', 'Εργάσιμες ημέρες εβδομάδας', TRUE);
```

### 8.2 email_notifications
```sql
CREATE TABLE email_notifications (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employees(id),
    leave_request_id INTEGER REFERENCES leave_requests(id),
    
    -- Email details
    subject VARCHAR(500) NOT NULL,
    body TEXT NOT NULL,
    to_email VARCHAR(200) NOT NULL,
    cc_emails TEXT, -- comma separated
    
    -- Status
    status VARCHAR(20) DEFAULT 'PENDING', -- PENDING, SENT, FAILED
    sent_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_email_notifications_status ON email_notifications(status);
CREATE INDEX idx_email_notifications_employee ON email_notifications(employee_id);
```

### 8.3 blood_donation_tracking
```sql
CREATE TABLE blood_donation_tracking (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employees(id),
    leave_request_id INTEGER NOT NULL REFERENCES leave_requests(id),
    
    -- Στοιχεία αιμοδοσίας
    donation_date DATE NOT NULL,
    was_successful BOOLEAN,
    hospital_name VARCHAR(200),
    certificate_number VARCHAR(100),
    
    -- Υπόλοιπο ημερών
    additional_days_granted INTEGER DEFAULT 0, -- 0 ή 2
    additional_days_used INTEGER DEFAULT 0,
    
    -- Metadata
    year INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_additional_days CHECK (additional_days_granted IN (0, 2))
);

CREATE INDEX idx_blood_donation_employee ON blood_donation_tracking(employee_id);
CREATE INDEX idx_blood_donation_year ON blood_donation_tracking(year);
```

---

## 🔍 ΒΑΣΙΚΕΣ ΑΝΑΖΗΤΗΣΕΙΣ & QUERIES

### Εύρεση αδειών προς έγκριση για προϊστάμενο
```sql
SELECT lr.*, e.name_in_accusative, e.surname_in_accusative 
FROM leave_requests lr
JOIN employees e ON lr.employee_id = e.id
JOIN departments d ON e.department_id = d.id
WHERE d.manager_id = ? 
AND lr.status_id = (SELECT id FROM leave_statuses WHERE name = 'ΕΓΚΡΙΣΗ_ΑΠΟ_ΠΡΟΪΣΤΑΜΕΝΟ')
ORDER BY lr.created_at;
```

### Υπολογισμός εργάσιμων ημερών (εξαιρώντας αργίες)
```sql
WITH RECURSIVE date_series AS (
    SELECT ?::DATE as date_val
    UNION ALL
    SELECT date_val + INTERVAL '1 day'
    FROM date_series
    WHERE date_val < ?::DATE
)
SELECT COUNT(*) as working_days
FROM date_series ds
WHERE EXTRACT(DOW FROM ds.date_val) NOT IN (0, 6) -- όχι Κυριακή/Σάββατο
AND ds.date_val NOT IN (
    SELECT date FROM public_holidays 
    WHERE (is_national = TRUE OR city_id = ?)
    AND is_active = TRUE
);
```

### Εύρεση επικαλυπτόμενων αδειών
```sql
SELECT lr1.id, lr2.id, lrp1.start_date, lrp1.end_date
FROM leave_request_periods lrp1
JOIN leave_request_periods lrp2 ON lrp1.id != lrp2.id
JOIN leave_requests lr1 ON lrp1.leave_request_id = lr1.id
JOIN leave_requests lr2 ON lrp2.leave_request_id = lr2.id
WHERE lr1.employee_id = lr2.employee_id
AND lrp1.start_date <= lrp2.end_date
AND lrp1.end_date >= lrp2.start_date
AND lr1.status_id NOT IN (SELECT id FROM leave_statuses WHERE is_final_status = TRUE);
```

---

## 📊 ΣΤΑΤΙΣΤΙΚΑ & PERFORMANCE

### Indexes για βελτιστοποίηση
```sql
-- Composite indexes για συχνές αναζητήσεις
CREATE INDEX idx_leave_requests_employee_status ON leave_requests(employee_id, status_id);
CREATE INDEX idx_leave_requests_type_status ON leave_requests(leave_type_id, status_id);
CREATE INDEX idx_employees_service_active ON employees(current_service_id, is_active);
CREATE INDEX idx_employees_department_active ON employees(department_id, is_active);

-- Partial indexes για active records
CREATE INDEX idx_active_employees ON employees(id) WHERE is_active = TRUE;
CREATE INDEX idx_pending_leave_requests ON leave_requests(id) 
WHERE status_id NOT IN (SELECT id FROM leave_statuses WHERE is_final_status = TRUE);
```

### Constraints για data integrity
```sql
-- Εξασφάλιση ότι ο προϊστάμενος ανήκει στη σωστή υπηρεσία
ALTER TABLE departments ADD CONSTRAINT valid_manager_service
CHECK (
    manager_id IS NULL OR 
    manager_id IN (
        SELECT id FROM employees e2 
        WHERE e2.current_service_id = departments.service_id
    )
);

-- Εξασφάλιση ότι δεν υπάρχουν κυκλικές αναφορές
ALTER TABLE services ADD CONSTRAINT no_circular_parent
CHECK (parent_service_id != id);

ALTER TABLE departments ADD CONSTRAINT no_circular_parent_dept
CHECK (parent_department_id != id);
```

---

## 🚀 NEXT STEPS: Django Implementation

Τα επόμενα βήματα περιλαμβάνουν:

1. **Django Models Creation**
2. **Migrations Setup**
3. **Admin Interface Configuration**
4. **API Endpoints Design**
5. **Frontend Templates**
6. **Docker Configuration**
7. **PostgreSQL Setup**

Αυτό το schema καλύπτει όλες τις απαιτήσεις που περιγράψατε και παρέχει solid foundation για το σύστημα διαχείρισης αδειών της ΠΔΕΔΕ.