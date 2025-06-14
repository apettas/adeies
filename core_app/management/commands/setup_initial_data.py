"""
Management command για αρχική φόρτωση δεδομένων στο σύστημα αδειών ΠΔΕΔΕ
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from datetime import date

from users.models import Role
from core_app.models import (
    EmployeeType, Specialty, City, ServiceType, Service, Department, SystemSetting
)
from leave_app.models import LeaveType, LeaveStatus
from calendar_app.models import PublicHoliday


class Command(BaseCommand):
    help = 'Δημιουργία αρχικών δεδομένων για το σύστημα αδειών ΠΔΕΔΕ'

    def add_arguments(self, parser):
        parser.add_argument(
            '--year',
            type=int,
            default=timezone.now().year,
            help='Έτος για τη δημιουργία αργιών'
        )

    def handle(self, *args, **options):
        year = options['year']
        
        try:
            with transaction.atomic():
                self.stdout.write(
                    self.style.SUCCESS(f'🚀 Εκκίνηση αρχικής φόρτωσης δεδομένων για έτος {year}...')
                )
                
                # 1. Δημιουργία ρόλων
                self.create_roles()
                
                # 2. Δημιουργία τύπων υπαλλήλων
                self.create_employee_types()
                
                # 3. Δημιουργία ειδικοτήτων
                self.create_specialties()
                
                # 4. Δημιουργία πόλεων
                self.create_cities()
                
                # 5. Δημιουργία τύπων υπηρεσιών
                self.create_service_types()
                
                # 6. Δημιουργία υπηρεσιών
                self.create_services()
                
                # 7. Δημιουργία τμημάτων
                self.create_departments()
                
                # 8. Δημιουργία τύπων αδειών
                self.create_leave_types()
                
                # 9. Δημιουργία καταστάσεων αδειών
                self.create_leave_statuses()
                
                # 10. Δημιουργία αργιών
                self.create_holidays(year)
                
                # 11. Δημιουργία ρυθμίσεων συστήματος
                self.create_system_settings()
                
                self.stdout.write(
                    self.style.SUCCESS('✅ Η αρχική φόρτωση δεδομένων ολοκληρώθηκε επιτυχώς!')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Σφάλμα κατά την αρχική φόρτωση: {str(e)}')
            )
            raise

    def create_roles(self):
        """Δημιουργία ρόλων"""
        self.stdout.write('📋 Δημιουργία ρόλων...')
        
        roles_data = [
            ('Administrator', 'Διαχειριστής συστήματος'),
            ('Χειριστής αδειών', 'Υπάλληλος διαχείρισης αδειών'),
            ('Προϊστάμενος τμήματος', 'Προϊστάμενος τμήματος'),
            ('Υπεύθυνος Κέντρου Στήριξης ΣΔΕΥ', 'Υπεύθυνος ΣΔΕΥ'),
            ('Γραμματέας ΚΕΔΑΣΥ', 'Γραμματέας ΚΕΔΑΣΥ'),
            ('Περιφερειακός Διευθυντής', 'Περιφερειακός Διευθυντής'),
            ('Υπεύθυνος ΕΣΠΑ', 'Υπεύθυνος ΕΣΠΑ'),
            ('Υπάλληλος', 'Βασικός χρήστης'),
        ]
        
        for name, description in roles_data:
            role, created = Role.objects.get_or_create(
                name=name,
                defaults={
                    'description': description,
                    'is_system_role': True
                }
            )
            if created:
                self.stdout.write(f'  ✓ Δημιουργήθηκε ρόλος: {name}')

    def create_employee_types(self):
        """Δημιουργία τύπων υπαλλήλων"""
        self.stdout.write('👥 Δημιουργία τύπων υπαλλήλων...')
        
        types = [
            'Διοικητικοί',
            'Εκπαιδευτικοί', 
            'Αναπληρωτές',
            'Κέντρο Στήριξης ΣΔΕΥ',
            'Δ/ντές Εκπαίδευσης',
            'Άλλο'
        ]
        
        for type_name in types:
            emp_type, created = EmployeeType.objects.get_or_create(name=type_name)
            if created:
                self.stdout.write(f'  ✓ Δημιουργήθηκε τύπος: {type_name}')

    def create_specialties(self):
        """Δημιουργία ειδικοτήτων"""
        self.stdout.write('🎓 Δημιουργία ειδικοτήτων...')
        
        specialties_data = [
            ('ΔΕ1 - ΔΕ ΔΙΟΙΚΗΤΙΚΟΥ-ΛΟΓΙΣΤΙΚΟΥ', 'ΔΕ1'),
            ('ΠΕ ΠΛΗΡΟΦΟΡΙΚΗΣ', 'ΠΕ04'),
            ('ΥΕ ΔΙΟΙΚΗΤΙΚΟΥ', 'ΥΕ'),
            ('ΠΕ ΦΙΛΟΛΟΓΩΝ', 'ΠΕ02'),
            ('ΠΕ ΜΑΘΗΜΑΤΙΚΩΝ', 'ΠΕ03'),
            ('ΠΕ ΦΥΣΙΚΩΝ ΕΠΙΣΤΗΜΩΝ', 'ΠΕ05'),
            ('ΔΕ ΚΑΘΑΡΙΣΤΡΙΩΝ-ΣΧΟΛ. ΦΥΛΑΚΩΝ', 'ΔΕ02'),
        ]
        
        for full_name, short_name in specialties_data:
            specialty, created = Specialty.objects.get_or_create(
                specialty_full=full_name,
                defaults={'specialty_short': short_name}
            )
            if created:
                self.stdout.write(f'  ✓ Δημιουργήθηκε ειδικότητα: {short_name}')

    def create_cities(self):
        """Δημιουργία πόλεων"""
        self.stdout.write('🏙️ Δημιουργία πόλεων...')
        
        cities_data = [
            ('Πάτρα', 'Αχαΐα'),
            ('Μεσολόγγι', 'Αιτωλοακαρνανία'),
            ('Πύργος', 'Ηλεία'),
            ('Κλειτορία', 'Αχαΐα'),
            ('Κρέστενα', 'Ηλεία'),
        ]
        
        for name, prefecture in cities_data:
            city, created = City.objects.get_or_create(
                name=name,
                defaults={'prefecture': prefecture}
            )
            if created:
                self.stdout.write(f'  ✓ Δημιουργήθηκε πόλη: {name}')

    def create_service_types(self):
        """Δημιουργία τύπων υπηρεσιών"""
        self.stdout.write('🏢 Δημιουργία τύπων υπηρεσιών...')
        
        types_data = [
            ('ΠΕΡΙΦΕΡΕΙΑΚΗ ΔΙΕΥΘΥΝΣΗ', 'ΠΔΕΔΕ', 1, False),
            ('ΚΕΔΑΣΥ', 'ΚΕΔΑΣΥ', 2, True),
            ('ΚΕΠΕΑ', 'ΚΕΠΕΑ', 2, True),
            ('ΣΔΕΥ', 'ΣΔΕΥ', 3, True),
        ]
        
        for name, abbr, level, requires_protocol in types_data:
            service_type, created = ServiceType.objects.get_or_create(
                name=name,
                defaults={
                    'abbreviation': abbr,
                    'level': level,
                    'requires_kedasy_protocol': requires_protocol
                }
            )
            if created:
                self.stdout.write(f'  ✓ Δημιουργήθηκε τύπος υπηρεσίας: {name}')

    def create_services(self):
        """Δημιουργία υπηρεσιών"""
        self.stdout.write('🏛️ Δημιουργία υπηρεσιών...')
        
        # Παίρνουμε τα απαιτούμενα objects
        pdede_type = ServiceType.objects.get(name='ΠΕΡΙΦΕΡΕΙΑΚΗ ΔΙΕΥΘΥΝΣΗ')
        kedasy_type = ServiceType.objects.get(name='ΚΕΔΑΣΥ')
        kepea_type = ServiceType.objects.get(name='ΚΕΠΕΑ')
        sdeu_type = ServiceType.objects.get(name='ΣΔΕΥ')
        
        patra = City.objects.get(name='Πάτρα')
        mesolongi = City.objects.get(name='Μεσολόγγι')
        pyrgos = City.objects.get(name='Πύργος')
        kleitoria = City.objects.get(name='Κλειτορία')
        krestena = City.objects.get(name='Κρέστενα')
        
        # Κύρια ΠΔΕΔΕ
        pdede, created = Service.objects.get_or_create(
            name='ΠΔΕΔΕ',
            defaults={
                'full_name': 'Περιφερειακή Διεύθυνση Εκπαίδευσης Δυτικής Ελλάδας',
                'service_type': pdede_type,
                'city': patra
            }
        )
        if created:
            self.stdout.write(f'  ✓ Δημιουργήθηκε υπηρεσία: ΠΔΕΔΕ')
        
        # ΚΕΔΑΣΥ
        kedasy_data = [
            ('ΚΕΔΑΣΥ 1ο ΠΑΤΡΑΣ', patra),
            ('ΚΕΔΑΣΥ 2ο ΠΑΤΡΑΣ', patra),
            ('ΚΕΔΑΣΥ ΑΙΤ/ΝΙΑΣ', mesolongi),
            ('ΚΕΔΑΣΥ ΗΛΕΙΑΣ', pyrgos),
        ]
        
        kedasy_services = {}
        for name, city in kedasy_data:
            service, created = Service.objects.get_or_create(
                name=name,
                defaults={
                    'service_type': kedasy_type,
                    'parent_service': pdede,
                    'city': city
                }
            )
            kedasy_services[name] = service
            if created:
                self.stdout.write(f'  ✓ Δημιουργήθηκε υπηρεσία: {name}')
        
        # ΚΕΠΕΑ
        kepea_data = [
            ('ΚΕΠΕΑ ΑΧΑΙΑΣ', kleitoria),
            ('ΚΕΠΕΑ ΗΛΕΙΑΣ', krestena),
            ('ΚΕΠΕΑ ΑΙΤΝΙΑΣ', mesolongi),
        ]
        
        for name, city in kepea_data:
            service, created = Service.objects.get_or_create(
                name=name,
                defaults={
                    'service_type': kepea_type,
                    'parent_service': pdede,
                    'city': city
                }
            )
            if created:
                self.stdout.write(f'  ✓ Δημιουργήθηκε υπηρεσία: {name}')
        
        # Παραδείγματα ΣΔΕΥ
        sdeu_data = [
            ('ΣΔΕΥ1', 'ΚΕΔΑΣΥ 1ο ΠΑΤΡΑΣ'),
            ('ΣΔΕΥ2', 'ΚΕΔΑΣΥ 1ο ΠΑΤΡΑΣ'),
            ('ΣΔΕΥ3', 'ΚΕΔΑΣΥ 1ο ΠΑΤΡΑΣ'),
            ('ΣΔΕΥ11', 'ΚΕΔΑΣΥ 2ο ΠΑΤΡΑΣ'),
            ('ΣΔΕΥ12', 'ΚΕΔΑΣΥ 2ο ΠΑΤΡΑΣ'),
            ('ΣΔΕΥ21', 'ΚΕΔΑΣΥ ΑΙΤ/ΝΙΑΣ'),
            ('ΣΔΕΥ25', 'ΚΕΔΑΣΥ ΗΛΕΙΑΣ'),
        ]
        
        for sdeu_name, kedasy_name in sdeu_data:
            parent_kedasy = kedasy_services.get(kedasy_name)
            if parent_kedasy:
                service, created = Service.objects.get_or_create(
                    name=sdeu_name,
                    defaults={
                        'service_type': sdeu_type,
                        'parent_service': parent_kedasy,
                        'city': parent_kedasy.city
                    }
                )
                if created:
                    self.stdout.write(f'  ✓ Δημιουργήθηκε υπηρεσία: {sdeu_name}')

    def create_departments(self):
        """Δημιουργία τμημάτων"""
        self.stdout.write('🏛️ Δημιουργία τμημάτων...')
        
        try:
            pdede = Service.objects.get(name='ΠΔΕΔΕ')
            
            # Τμήματα ΠΔΕΔΕ
            pdede_departments = [
                'ΑΥΤΟΤΕΛΗΣ ΔΙΕΥΘΥΝΣΗ',
                'ΤΜΗΜΑ Α',
                'ΤΜΗΜΑ Β',
                'ΤΜΗΜΑ Γ',
                'ΤΜΗΜΑ Δ',
                'ΓΡΑΦΕΙΟ ΝΟΜΙΚΗΣ',
            ]
            
            for dept_name in pdede_departments:
                dept, created = Department.objects.get_or_create(
                    name=dept_name,
                    service=pdede
                )
                if created:
                    self.stdout.write(f'  ✓ Δημιουργήθηκε τμήμα: {dept_name}')
                    
        except Service.DoesNotExist:
            self.stdout.write(self.style.WARNING('  ⚠️ Δεν βρέθηκε η υπηρεσία ΠΔΕΔΕ'))

    def create_leave_types(self):
        """Δημιουργία τύπων αδειών"""
        self.stdout.write('📝 Δημιουργία τύπων αδειών...')
        
        types_data = [
            {
                'id_adeias': 'KANONIKI',
                'eidos_adeias': 'Κανονική Άδεια',
                'eidos_adeias_aplo': 'Κανονική',
                'keimeno_thematos_adeia': 'Χορήγηση κανονικής άδειας',
                'keimeno_apofasis_adeia': 'κανονική άδεια',
                'requires_manager_approval': True,
                'requires_protocol': True,
                'requires_decision_pdf': True,
            },
            {
                'id_adeias': 'ANARROTIKI',
                'eidos_adeias': 'Αναρρωτική Άδεια',
                'eidos_adeias_aplo': 'Αναρρωτική',
                'keimeno_thematos_adeia': 'Χορήγηση αναρρωτικής άδειας',
                'keimeno_apofasis_adeia': 'αναρρωτική άδεια',
                'requires_manager_approval': False,
                'bypass_manager_for_sick_leave': True,
                'requires_protocol': True,
                'requires_decision_pdf': True,
            },
            {
                'id_adeias': 'AIMODOSIA',
                'eidos_adeias': 'Άδεια Αιμοδοσίας',
                'eidos_adeias_aplo': 'Αιμοδοσία',
                'keimeno_thematos_adeia': 'Χορήγηση άδειας αιμοδοσίας',
                'keimeno_apofasis_adeia': 'άδεια αιμοδοσίας',
                'requires_manager_approval': True,
                'requires_protocol': True,
                'requires_decision_pdf': True,
            },
            {
                'id_adeias': 'PROFORIKI',
                'eidos_adeias': 'Προφορική Άδεια',
                'eidos_adeias_aplo': 'Προφορική',
                'keimeno_thematos_adeia': 'Προφορική άδεια',
                'keimeno_apofasis_adeia': 'προφορική άδεια',
                'requires_manager_approval': True,
                'requires_protocol': False,
                'requires_decision_pdf': False,
            },
            {
                'id_adeias': 'EORTASTIKI',
                'eidos_adeias': 'Εορταστική Άδεια',
                'eidos_adeias_aplo': 'Εορταστική',
                'keimeno_thematos_adeia': 'Εορταστική άδεια',
                'keimeno_apofasis_adeia': 'εορταστική άδεια',
                'requires_manager_approval': True,
                'requires_protocol': False,
                'requires_decision_pdf': False,
            },
            {
                'id_adeias': 'EPIMORFOSI',
                'eidos_adeias': 'Άδεια Επιμόρφωσης',
                'eidos_adeias_aplo': 'Επιμόρφωση',
                'keimeno_thematos_adeia': 'Άδεια επιμόρφωσης',
                'keimeno_apofasis_adeia': 'άδεια επιμόρφωσης',
                'requires_manager_approval': True,
                'requires_protocol': False,
                'requires_decision_pdf': False,
            },
        ]
        
        for type_data in types_data:
            leave_type, created = LeaveType.objects.get_or_create(
                id_adeias=type_data['id_adeias'], 
                defaults=type_data
            )
            if created:
                self.stdout.write(f'  ✓ Δημιουργήθηκε τύπος άδειας: {type_data["eidos_adeias"]}')

    def create_leave_statuses(self):
        """Δημιουργία καταστάσεων αδειών"""
        self.stdout.write('📊 Δημιουργία καταστάσεων αδειών...')
        
        statuses_data = [
            ('ΚΑΤΑΧΩΡΗΘΗΚΕ', 'Καταχωρήθηκε η αίτηση', '#FFA500', False, 1),
            ('ΕΓΚΡΙΣΗ_ΑΠΟ_ΠΡΟΪΣΤΑΜΕΝΟ', 'Προς έγκριση από προϊστάμενο', '#FFE4B5', False, 2),
            ('ΓΙΑ_ΠΡΩΤΟΚΟΛΛΟ_ΚΕΔΑΣΥ', 'Για πρωτόκολλο ΚΕΔΑΣΥ/ΚΕΠΕΑ', '#87CEEB', False, 3),
            ('ΓΙΑ_ΠΡΩΤΟΚΟΛΛΟ_ΠΔΕΔΕ', 'Για πρωτόκολλο ΠΔΕΔΕ', '#87CEFA', False, 4),
            ('ΠΡΟΣ_ΕΠΕΞΕΡΓΑΣΙΑ', 'Προς επεξεργασία', '#98FB98', False, 5),
            ('ΕΠΕΞΕΡΓΑΣΙΑ', 'Υπό επεξεργασία', '#90EE90', False, 6),
            ('ΑΝΑΜΟΝΗ_ΔΙΚΑΙΟΛΟΓΗΤΙΚΩΝ', 'Αναμονή δικαιολογητικών', '#F0E68C', False, 7),
            ('ΥΓΕΙΟΝΟΜΙΚΗ_ΕΠΙΤΡΟΠΗ', 'Υγειονομική επιτροπή', '#DDA0DD', False, 8),
            ('ΣΗΔΕ_ΠΡΟΣ_ΥΠΟΓΡΑΦΕΣ', 'ΣΗΔΕ - Προς υπογραφές', '#B0C4DE', False, 9),
            ('ΟΛΟΚΛΗΡΩΜΕΝΗ', 'Ολοκληρωμένη', '#90EE90', True, 10),
            ('ΜΗ_ΕΓΚΡΙΣΗ_ΑΠΟ_ΠΡΟΪΣΤΑΜΕΝΟ', 'Μη έγκριση από προϊστάμενο', '#FF6347', True, 11),
            ('ΑΠΟΡΡΙΨΗ_ΑΠΟ_ΤΜΗΜΑ_ΑΔΕΙΩΝ', 'Απόρριψη από τμήμα αδειών', '#FF4500', True, 12),
            ('ΑΝΑΚΛΗΣΗ_ΑΙΤΗΣΗΣ_ΑΠΟ_ΑΙΤΟΥΝΤΑ', 'Ανάκληση αίτησης από αιτούντα', '#D3D3D3', True, 13),
            ('ΑΝΑΚΛΗΣΗ_ΟΛΟΚΛΗΡΩΜΕΝΗΣ_ΑΔΕΙΑΣ', 'Ανάκληση ολοκληρωμένης άδειας', '#C0C0C0', False, 14),
        ]
        
        for name, desc, color, is_final, priority in statuses_data:
            status, created = LeaveStatus.objects.get_or_create(
                name=name,
                defaults={
                    'description': desc,
                    'color_code': color,
                    'is_final_status': is_final,
                    'order_priority': priority
                }
            )
            if created:
                self.stdout.write(f'  ✓ Δημιουργήθηκε κατάσταση: {name}')

    def create_holidays(self, year):
        """Δημιουργία αργιών"""
        self.stdout.write(f'🎄 Δημιουργία αργιών για έτος {year}...')
        
        # Σταθερές εθνικές αργίες
        fixed_holidays = [
            ('Πρωτοχρονιά', 1, 1),
            ('Θεοφάνεια', 1, 6),
            ('25η Μαρτίου', 3, 25),
            ('Πρωτομαγιά', 5, 1),
            ('15 Αυγούστου', 8, 15),
            ('28η Οκτωβρίου', 10, 28),
            ('Χριστούγεννα', 12, 25),
            ('Δεύτερα των Χριστουγέννων', 12, 26),
        ]
        
        for name, month, day in fixed_holidays:
            holiday_date = date(year, month, day)
            holiday, created = PublicHoliday.objects.get_or_create(
                name=name,
                date=holiday_date,
                defaults={
                    'year': year,
                    'is_fixed': True,
                    'is_national': True
                }
            )
            if created:
                self.stdout.write(f'  ✓ Δημιουργήθηκε αργία: {name} ({holiday_date.strftime("%d/%m/%Y")})')
        
        # Τοπικές αργίες
        try:
            patra = City.objects.get(name='Πάτρα')
            holiday, created = PublicHoliday.objects.get_or_create(
                name='Άγιος Ανδρέας',
                date=date(year, 11, 30),
                city=patra,
                defaults={
                    'year': year,
                    'is_fixed': True,
                    'is_national': False
                }
            )
            if created:
                self.stdout.write(f'  ✓ Δημιουργήθηκε τοπική αργία: Άγιος Ανδρέας (Πάτρα)')
        except City.DoesNotExist:
            pass

    def create_system_settings(self):
        """Δημιουργία ρυθμίσεων συστήματος"""
        self.stdout.write('⚙️ Δημιουργία ρυθμίσεων συστήματος...')
        
        settings_data = {
            'DEFAULT_REGULAR_LEAVE_DAYS': ('24', 'Προεπιλεγμένες ημέρες κανονικής άδειας'),
            'SYSTEM_EMAIL_FROM': ('noreply@sch.gr', 'Email αποστολέα συστήματος'),
            'PDF_HEADER_LOGO_TEXT': ('ΕΛΛΗΝΙΚΗ ΔΗΜΟΚΡΑΤΙΑ\nΥΠΟΥΡΓΕΙΟ ΠΑΙΔΕΙΑΣ, ΘΡΗΣΚΕΥΜΑΤΩΝ ΚΑΙ ΑΘΛΗΤΙΣΜΟΥ\nΠΕΡΙΦΕΡΕΙΑΚΗ ΔΙΕΥΘΥΝΣΗ Π/ΘΜΙΑΣ & Δ/ΘΜΙΑΣ ΕΚΠΑΙΔΕΥΣΗΣ ΔΥΤΙΚΗΣ ΕΛΛΑΔΑΣ\nΑΥΤΟΤΕΛΗΣ ΔΙΕΥΘΥΝΣΗ ΔΙΟΙΚΗΤΙΚΗΣ, ΟΙΚΟΝΟΜΙΚΗΣ ΚΑΙ ΠΑΙΔΑΓΩΓΙΚΗΣ ΥΠΟΣΤΗΡΙΞΗΣ\nΤΜΗΜΑ Γ\' ΠΡΟΣΩΠΙΚΟΥ', 'Κείμενο επικεφαλίδας PDF'),
            'WORKING_DAYS_PER_WEEK': ('5', 'Εργάσιμες ημέρες εβδομάδας'),
            'MAX_FILE_SIZE_MB': ('5', 'Μέγιστο μέγεθος αρχείου σε MB'),
            'ALLOWED_FILE_TYPES': ('PDF,JPG,JPEG', 'Επιτρεπόμενοι τύποι αρχείων'),
            'SICK_LEAVE_HEALTH_COMMITTEE_THRESHOLD': ('8', 'Όριο ημερών αναρρωτικής για υγειονομική επιτροπή'),
            'SELF_DECLARATION_SICK_DAYS_PER_YEAR': ('2', 'Ημέρες αναρρωτικής με υπεύθυνη δήλωση ανά έτος'),
            'BLOOD_DONATION_ADDITIONAL_DAYS': ('2', 'Επιπλέον ημέρες για επιτυχή αιμοδοσία'),
        }
        
        for key, (value, desc) in settings_data.items():
            setting, created = SystemSetting.objects.get_or_create(
                key=key,
                defaults={
                    'value': value, 
                    'description': desc, 
                    'is_system': True
                }
            )
            if created:
                self.stdout.write(f'  ✓ Δημιουργήθηκε ρύθμιση: {key}')