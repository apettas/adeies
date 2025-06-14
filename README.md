# 🏛️ Σύστημα Διαχείρισης Αδειών ΠΔΕΔΕ

Ολοκληρωμένο σύστημα διαχείρισης αδειών για την Περιφερειακή Διεύθυνση Εκπαίδευσης Δυτικής Ελλάδας (ΠΔΕΔΕ).

## 📋 Περιγραφή

Το σύστημα διαχειρίζεται:
- ✅ **Αιτήσεις αδειών** με πλήρες workflow έγκρισης
- 👥 **Διαχείριση χρηστών** με πολλαπλούς ρόλους
- 🏢 **Οργανωτική δομή** (ΠΔΕΔΕ, ΚΕΔΑΣΥ, ΚΕΠΕΑ, ΣΔΕΥ)
- 📄 **Συνημμένα αρχεία** με ασφάλεια
- 📅 **Ημερολόγιο αργιών** (εθνικές, τοπικές)
- 📊 **Αναφορές και στατιστικά**
- 🔒 **GDPR compliance**

## 🏗️ Αρχιτεκτονική

- **Backend**: Django 5.2+ με PostgreSQL
- **Frontend**: Django Templates + Bootstrap (mobile-friendly)
- **Containerization**: Docker & Docker Compose
- **Caching**: Redis
- **File Storage**: Local με secure access
- **Internationalization**: Ελληνικά (el) με dd/mm/yyyy format

## 🚀 Εγκατάσταση

### Προαπαιτούμενα

- Docker & Docker Compose
- Git

### 1. Clone του Repository

```bash
git clone <repository-url>
cd adeies
```

### 2. Αρχικοποίηση Environment

```bash
# Αντιγραφή του .env αρχείου
cp .env.example .env

# Επεξεργασία των ρυθμίσεων (προαιρετικό για development)
nano .env
```

### 3. Εκκίνηση με Docker

```bash
# Εκκίνηση development environment
docker-compose up -d

# Περιμένετε να ξεκινήσουν όλα τα services
docker-compose logs -f web
```

### 4. Αρχική Φόρτωση Δεδομένων

```bash
# Εκτέλεση του setup command
docker-compose exec web python manage.py setup_initial_data

# Δημιουργία superuser (προαιρετικό)
docker-compose exec web python manage.py createsuperuser
```

### 5. Πρόσβαση στο Σύστημα

- **Εφαρμογή**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin/
- **Database**: localhost:5432

## 🛠️ Development Setup

### Τοπική Εγκατάσταση (χωρίς Docker)

```bash
# Εγκατάσταση dependencies
pip install -r requirements.txt

# Ρύθμιση PostgreSQL
createdb adeies_db

# Migrations
python manage.py makemigrations
python manage.py migrate

# Αρχική φόρτωση δεδομένων
python manage.py setup_initial_data

# Εκκίνηση development server
python manage.py runserver
```

## 📚 Django Apps Structure

```
adeies/
├── users/              # Χρήστες & Ρόλοι
├── core_app/           # Βασικές οντότητες (Services, Departments)
├── leave_app/          # Διαχείριση αδειών
├── attachments_app/    # Συνημμένα αρχεία
├── calendar_app/       # Ημερολόγιο & Αργίες
├── audit_app/          # Logs & History tracking
├── gdpr_app/           # GDPR compliance
├── notifications_app/  # Ειδοποιήσεις
└── reports_app/        # Αναφορές & Dashboard
```

## 👥 Ρόλοι Χρηστών

1. **Administrator** - Πλήρη διαχείριση συστήματος
2. **Χειριστής αδειών** - Επεξεργασία όλων των αδειών
3. **Προϊστάμενος τμήματος** - Έγκριση αδειών υπαλλήλων
4. **Περιφερειακός Διευθυντής** - Πρόσβαση σε όλες τις υπηρεσίες
5. **Γραμματέας ΚΕΔΑΣΥ** - Πρωτόκολλο ΚΕΔΑΣΥ
6. **Υπεύθυνος ΣΔΕΥ** - Προβολή αδειών ΣΔΕΥ (χωρίς συνημμένα)
7. **Υπεύθυνος ΕΣΠΑ** - View-only για Αναπληρωτές
8. **Υπάλληλος** - Βασικός χρήστης

## 🔄 Workflow Αδειών

```
ΚΑΤΑΧΩΡΗΘΗΚΕ
     ↓
ΕΓΚΡΙΣΗ_ΑΠΟ_ΠΡΟΪΣΤΑΜΕΝΟ (εκτός αναρρωτικών)
     ↓
ΓΙΑ_ΠΡΩΤΟΚΟΛΛΟ_ΚΕΔΑΣΥ (για ΚΕΔΑΣΥ/ΚΕΠΕΑ)
     ↓
ΓΙΑ_ΠΡΩΤΟΚΟΛΛΟ_ΠΔΕΔΕ
     ↓
ΠΡΟΣ_ΕΠΕΞΕΡΓΑΣΙΑ
     ↓
ΕΠΕΞΕΡΓΑΣΙΑ
     ↓
ΣΗΔΕ_ΠΡΟΣ_ΥΠΟΓΡΑΦΕΣ
     ↓
ΟΛΟΚΛΗΡΩΜΕΝΗ
```

## 📁 Τύποι Αδειών

- **Κανονική Άδεια** - 24 ημέρες/έτος με μεταφορά υπολοίπου
- **Αναρρωτική Άδεια** - Με/χωρίς υπεύθυνη δήλωση (2 ημέρες/έτος)
- **Άδεια Αιμοδοσίας** - 1+2 ημέρες
- **Προφορική/Εορταστική/Επιμόρφωση** - Χωρίς πρωτόκολλο

## 🔧 Management Commands

```bash
# Αρχική φόρτωση δεδομένων
python manage.py setup_initial_data

# Δημιουργία αργιών για συγκεκριμένο έτος
python manage.py setup_initial_data --year 2025

# Εξαγωγή backup
python manage.py dumpdata > backup.json

# Εισαγωγή backup
python manage.py loaddata backup.json
```

## 🐳 Docker Commands

```bash
# Εκκίνηση services
docker-compose up -d

# Σταμάτημα services
docker-compose down

# Logs
docker-compose logs -f web

# Πρόσβαση στο container
docker-compose exec web bash

# Database backup
docker-compose exec db pg_dump -U adeies_user adeies_db > backup.sql

# Database restore
docker-compose exec -T db psql -U adeies_user adeies_db < backup.sql
```

## 🔒 Ασφάλεια & GDPR

- 🔐 **Ασφαλής αποθήκευση αρχείων** με role-based access
- 📋 **Audit logs** για όλες τις ενέργειες
- 🛡️ **GDPR compliance** με συναινέσεις χρηστών
- 🔍 **Επαλήθευση εγγράφων** με UUID
- 📱 **Mobile-responsive** interface

## 📝 Ειδικές Λειτουργίες

### Αναρρωτικές Άδειες
- 2 ημέρες/έτος με υπεύθυνη δήλωση
- Μετά τις 8 ημέρες → Υγειονομική Επιτροπή
- Συνημμένα ορατά μόνο σε χειριστές αδειών

### Αιμοδοσία
- 1 ημέρα για εξέταση
- +2 ημέρες αν επιτυχής (με βεβαίωση)
- Παρακολούθηση υπολοίπου ημερών

### Ανακλήσεις
- Πλήρης ή μερική ανάκληση
- Διαθέσιμη μέχρι κατάσταση "ΕΠΕΞΕΡΓΑΣΙΑ"
- Ανάκληση ολοκληρωμένων αδειών

## 🚧 Production Deployment

```bash
# Production με SSL
docker-compose --profile production up -d

# Ενημέρωση του .env για production
DEBUG=False
ALLOWED_HOSTS=your-domain.com
SECURE_SSL_REDIRECT=True
```

## 📊 Monitoring & Logs

- **Application logs**: `logs/adeies.log`
- **Audit logs**: Database tables
- **System monitoring**: Django Debug Toolbar (development)
- **Database**: PostgreSQL logs

## 🤝 Contributing

1. Fork το repository
2. Δημιουργία feature branch (`git checkout -b feature/amazing-feature`)
3. Commit αλλαγές (`git commit -m 'Add amazing feature'`)
4. Push στο branch (`git push origin feature/amazing-feature`)
5. Άνοιγμα Pull Request

## 📄 License

Αυτό το project είναι licensed υπό την MIT License.

## 📞 Support

Για υποστήριξη, δημιουργήστε ένα issue στο GitHub repository.

---

**Σημείωση**: Το σύστημα αναπτύχθηκε για την ΠΔΕΔΕ με βάση τις ελληνικές διοικητικές διαδικασίες και τον GDPR.