# 🐍 DJANGO MODELS - ΣΥΣΤΗΜΑ ΑΔΕΙΩΝ ΠΔΕΔΕ

## 📋 ΠΕΡΙΕΧΟΜΕΝΑ
1. [Accounts App - Χρήστες & Ρόλοι](#1-accounts-app---χρήστες--ρόλοι)
2. [Core App - Βασικές Οντότητες](#2-core-app---βασικές-οντότητες)
3. [Leaves App - Διαχείριση Αδειών](#3-leaves-app---διαχείριση-αδειών)
4. [Attachments App - Συνημμένα](#4-attachments-app---συνημμένα)
5. [Calendar App - Ημερολόγιο & Αργίες](#5-calendar-app---ημερολόγιο--αργίες)
6. [Audit App - Logs & History](#6-audit-app---logs--history)
7. [GDPR App - Compliance](#7-gdpr-app---compliance)
8. [Notifications App - Ειδοποιήσεις](#8-notifications-app---ειδοποιήσεις)

---

## 1. ACCOUNTS APP - ΧΡΗΣΤΕΣ & ΡΟΛΟΙ

### accounts/models.py

```python
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
import uuid

class Role(models.Model):
    """Ρόλοι χρηστών στο σύστημα"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Όνομα ρόλου")
    description = models.TextField(blank=True, verbose_name="Περιγραφή")
    permissions = models.JSONField(default=dict, verbose_name="Δικαιώματα")
    is_system_role = models.BooleanField(default=False, verbose_name="Ρόλος συστήματος")
    is_active = models.BooleanField(default=True, verbose_name="Ενεργός")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Ρόλος"
        verbose_name_plural = "Ρόλοι"
        ordering = ['name']

    def __str__(self):
        return self.name

    @classmethod
    def get_default_roles(cls):
        """Δημιουργία προεπιλεγμένων ρόλων"""
        roles = [
            ('Administrator', 'Διαχειριστής συστήματος'),
            ('Χειριστής αδειών', 'Υπάλληλος διαχείρισης αδειών'),
            ('Προϊστάμενος τμήματος', 'Προϊστάμενος τμήματος'),
            ('Υπεύθυνος Κέντρου Στήριξης ΣΔΕΥ', 'Υπεύθυνος ΣΔΕΥ'),
            ('Γραμματέας ΚΕΔΑΣΥ', 'Γραμματέας ΚΕΔΑΣΥ'),
            ('Περιφερειακός Διευθυντής', 'Περιφερειακός Διευθυντής'),
            ('Υπεύθυνος ΕΣΠΑ', 'Υπεύθυνος ΕΣΠΑ'),
            ('Υπάλληλος', 'Βασικός χρήστης'),
        ]
        for name, desc in roles:
            cls.objects.get_or_create(name=name, defaults={'description': desc, 'is_system_role': True})


class CustomUser(AbstractUser):
    """Επέκταση του Django User model"""
    email = models.EmailField(unique=True, verbose_name="Email")
    is_employee = models.BooleanField(default=False, verbose_name="Είναι υπάλληλος")
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = "Χρήστης"
        verbose_name_plural = "Χρήστες"

    def get_employee(self):
        """Επιστρέφει το Employee object αν υπάρχει"""
        if hasattr(self, 'employee'):
            return self.employee
        return None


class Employee(models.Model):
    """Υπάλληλοι - επέκταση του User model"""
    
    GENDER_CHOICES = [
        ('Άνδρας', 'Άνδρας'),
        ('Γυναίκα', 'Γυναίκα'),
    ]
    
    # One-to-One σχέση με User
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, verbose_name="Χρήστης")
    
    # Προσωπικά στοιχεία
    name_in_accusative = models.CharField(max_length=100, verbose_name="Όνομα (αιτιατική)")
    surname_in_accusative = models.CharField(max_length=100, verbose_name="Επώνυμο (αιτιατική)")
    father_name_in_genitive = models.CharField(max_length=100, blank=True, verbose_name="Πατρώνυμο (γενική)")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, verbose_name="Φύλο")
    
    # Επικοινωνία
    sch_email_validator = RegexValidator(
        regex=r'^[a-zA-Z0-9._%+-]+@sch\.gr$',
        message='Το email πρέπει να τελειώνει σε @sch.gr'
    )
    sch_email = models.EmailField(
        unique=True, 
        validators=[sch_email_validator],
        verbose_name="Υπηρεσιακό Email (@sch.gr)"
    )
    personal_email = models.EmailField(blank=True, verbose_name="Προσωπικό Email")
    phone1 = models.CharField(max_length=20, blank=True, verbose_name="Τηλέφωνο 1")
    phone2 = models.CharField(max_length=20, blank=True, verbose_name="Τηλέφωνο 2")
    
    # Υπηρεσιακά στοιχεία - Foreign Keys
    specialty = models.ForeignKey('core.Specialty', on_delete=models.PROTECT, verbose_name="Ειδικότητα")
    employee_type = models.ForeignKey('core.EmployeeType', on_delete=models.PROTECT, verbose_name="Τύπος υπαλλήλου")
    current_service = models.ForeignKey('core.Service', on_delete=models.PROTECT, verbose_name="Τρέχουσα υπηρεσία")
    department = models.ForeignKey('core.Department', on_delete=models.PROTECT, verbose_name="Τμήμα")
    
    # Περιγραφή ρόλου
    role_description = models.TextField(verbose_name="Περιγραφή ρόλου")
    
    # Άδειες
    regular_leave_days = models.PositiveIntegerField(default=24, verbose_name="Ημέρες κανονικής άδειας")
    carryover_leave_days = models.PositiveIntegerField(default=0, verbose_name="Μεταφερόμενες ημέρες άδειας")
    self_declaration_sick_days_remaining = models.PositiveIntegerField(
        default=2, 
        verbose_name="Υπόλοιπο ημερών αναρρωτικής με υπ. δήλωση"
    )
    
    # Ειδοποιήσεις
    notification_recipients = models.TextField(
        blank=True, 
        verbose_name="Παραλήπτες κοινοποίησης",
        help_text="Ονομασίες υπηρεσιών για κοινοποίηση"
    )
    preferred_notification_email = models.EmailField(
        blank=True, 
        verbose_name="Προτιμώμενο email ειδοποιήσεων"
    )
    
    # Ρυθμίσεις
    schedule = models.CharField(max_length=200, blank=True, verbose_name="Ωράριο")
    can_request_leave = models.BooleanField(default=True, verbose_name="Δικαίωμα αίτησης άδειας")
    is_active = models.BooleanField(default=True, verbose_name="Ενεργός")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Υπάλληλος"
        verbose_name_plural = "Υπάλληλοι"
        indexes = [
            models.Index(fields=['sch_email']),
            models.Index(fields=['current_service']),
            models.Index(fields=['department']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name_in_accusative} {self.surname_in_accusative}"

    def clean(self):
        """Validation για το preferred_notification_email"""
        if self.preferred_notification_email:
            if self.preferred_notification_email not in [self.sch_email, self.personal_email]:
                raise ValidationError({
                    'preferred_notification_email': 'Πρέπει να είναι είτε το υπηρεσιακό είτε το προσωπικό email'
                })

    def get_full_name_genitive(self):
        """Επιστρέφει πλήρες όνομα σε γενική πτώση για έγγραφα"""
        return f"{self.name_in_accusative} {self.surname_in_accusative} του {self.father_name_in_genitive}"

    def get_leave_balance(self, year=None):
        """Υπολογίζει το υπόλοιπο αδειών για το έτος"""
        from django.utils import timezone
        if not year:
            year = timezone.now().year
        
        # Υπολογισμός χρησιμοποιημένων αδειών
        from leaves.models import LeaveRequest
        used_days = LeaveRequest.objects.filter(
            employee=self,
            created_at__year=year,
            status__is_final_status=True,
            leave_type__id_adeias='KANONIKI'
        ).aggregate(
            total=models.Sum('working_days')
        )['total'] or 0
        
        total_available = self.regular_leave_days + self.carryover_leave_days
        return max(0, total_available - used_days)

    def has_pending_leave_requests(self):
        """Ελέγχει αν έχει εκκρεμείς αιτήσεις"""
        from leaves.models import LeaveRequest
        return LeaveRequest.objects.filter(
            employee=self,
            status__is_final_status=False
        ).exists()


class UserRole(models.Model):
    """Many-to-Many για πολλαπλούς ρόλους ανά χρήστη"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Υπάλληλος")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, verbose_name="Ρόλος")
    assigned_by = models.ForeignKey(
        Employee, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='assigned_roles',
        verbose_name="Ανατέθηκε από"
    )
    assigned_at = models.DateTimeField(auto_now_add=True, verbose_name="Ημερομηνία ανάθεσης")
    is_active = models.BooleanField(default=True, verbose_name="Ενεργός")

    class Meta:
        verbose_name = "Ρόλος Χρήστη"
        verbose_name_plural = "Ρόλοι Χρηστών"
        unique_together = ('employee', 'role')

    def __str__(self):
        return f"{self.employee} - {self.role}"
```

---

## 2. CORE APP - ΒΑΣΙΚΕΣ ΟΝΤΟΤΗΤΕΣ

### core/models.py

```python
from django.db import models
from django.core.exceptions import ValidationError

class EmployeeType(models.Model):
    """Τύποι υπαλλήλων"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Όνομα τύπου")
    description = models.TextField(blank=True, verbose_name="Περιγραφή")
    is_active = models.BooleanField(default=True, verbose_name="Ενεργός")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Τύπος Υπαλλήλου"
        verbose_name_plural = "Τύποι Υπαλλήλων"
        ordering = ['name']

    def __str__(self):
        return self.name

    @classmethod
    def get_default_types(cls):
        """Δημιουργία προεπιλεγμένων τύπων"""
        types = [
            'Διοικητικοί',
            'Εκπαιδευτικοί', 
            'Αναπληρωτές',
            'Κέντρο Στήριξης ΣΔΕΥ',
            'Δ/ντές Εκπαίδευσης',
            'Άλλο'
        ]
        for type_name in types:
            cls.objects.get_or_create(name=type_name)


class Specialty(models.Model):
    """Ειδικότητες υπαλλήλων"""
    specialty_full = models.CharField(max_length=200, unique=True, verbose_name="Πλήρης ειδικότητα")
    specialty_short = models.CharField(max_length=50, unique=True, verbose_name="Σύντομη ειδικότητα")
    is_active = models.BooleanField(default=True, verbose_name="Ενεργή")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Ειδικότητα"
        verbose_name_plural = "Ειδικότητες"
        ordering = ['specialty_short']

    def __str__(self):
        return self.specialty_full

    def save(self, *args, **kwargs):
        """Auto-generate specialty_short από το specialty_full"""
        if not self.specialty_short and '-' in self.specialty_full:
            self.specialty_short = self.specialty_full.split('-')[0].strip()
        super().save(*args, **kwargs)


class City(models.Model):
    """Πόλεις όπου βρίσκονται οι υπηρεσίες"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Όνομα πόλης")
    prefecture = models.CharField(max_length=100, blank=True, verbose_name="Νομός")
    is_active = models.BooleanField(default=True, verbose_name="Ενεργή")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Πόλη"
        verbose_name_plural = "Πόλεις"
        ordering = ['name']

    def __str__(self):
        return self.name


class ServiceType(models.Model):
    """Τύποι υπηρεσιών (ΠΔΕΔΕ, ΚΕΔΑΣΥ, ΚΕΠΕΑ, ΣΔΕΥ)"""
    
    LEVEL_CHOICES = [
        (1, 'ΠΔΕΔΕ'),
        (2, 'ΚΕΔΑΣΥ/ΚΕΠΕΑ'),
        (3, 'ΣΔΕΥ'),
    ]
    
    name = models.CharField(max_length=100, unique=True, verbose_name="Όνομα τύπου")
    abbreviation = models.CharField(max_length=20, blank=True, verbose_name="Συντομογραφία")
    level = models.PositiveIntegerField(choices=LEVEL_CHOICES, verbose_name="Επίπεδο ιεραρχίας")
    requires_kedasy_protocol = models.BooleanField(default=False, verbose_name="Απαιτεί πρωτόκολλο ΚΕΔΑΣΥ")
    is_active = models.BooleanField(default=True, verbose_name="Ενεργός")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Τύπος Υπηρεσίας"
        verbose_name_plural = "Τύποι Υπηρεσιών"
        ordering = ['level', 'name']

    def __str__(self):
        return self.name


class Service(models.Model):
    """Υπηρεσίες του συστήματος"""
    name = models.CharField(max_length=200, verbose_name="Όνομα υπηρεσίας")
    full_name = models.CharField(max_length=500, blank=True, verbose_name="Πλήρης ονομασία")
    service_type = models.ForeignKey(ServiceType, on_delete=models.PROTECT, verbose_name="Τύπος υπηρεσίας")
    parent_service = models.ForeignKey(
        'self', 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True,
        verbose_name="Γονική υπηρεσία"
    )
    city = models.ForeignKey(City, on_delete=models.PROTECT, verbose_name="Έδρα")
    manager = models.ForeignKey(
        'accounts.Employee', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Προϊστάμενος"
    )
    is_active = models.BooleanField(default=True, verbose_name="Ενεργή")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Υπηρεσία"
        verbose_name_plural = "Υπηρεσίες"
        ordering = ['service_type__level', 'name']

    def __str__(self):
        return self.name

    def clean(self):
        """Validation για κυκλικές αναφορές"""
        if self.parent_service == self:
            raise ValidationError("Η υπηρεσία δεν μπορεί να είναι γονέας του εαυτού της")

    def get_all_children(self):
        """Επιστρέφει όλες τις παιδικές υπηρεσίες (recursive)"""
        children = []
        for child in self.service_set.filter(is_active=True):
            children.append(child)
            children.extend(child.get_all_children())
        return children

    def get_kedasy_services(self):
        """Επιστρέφει όλα τα ΚΕΔΑΣΥ"""
        return Service.objects.filter(
            service_type__name='ΚΕΔΑΣΥ',
            is_active=True
        )

    def get_sdeu_by_kedasy(self, kedasy_service):
        """Επιστρέφει όλα τα ΣΔΕΥ ενός ΚΕΔΑΣΥ"""
        return Service.objects.filter(
            parent_service=kedasy_service,
            service_type__name='ΣΔΕΥ',
            is_active=True
        )


class Department(models.Model):
    """Τμήματα υπηρεσιών"""
    name = models.CharField(max_length=200, verbose_name="Όνομα τμήματος")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name="Υπηρεσία")
    manager = models.ForeignKey(
        'accounts.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Προϊστάμενος"
    )
    parent_department = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Γονικό τμήμα"
    )
    is_virtual = models.BooleanField(default=False, verbose_name="Εικονικό τμήμα (ΣΔΕΥ)")
    sdeu_supervisor = models.ForeignKey(
        'accounts.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='supervised_sdeu',
        verbose_name="Υπεύθυνος ΣΔΕΥ"
    )
    is_active = models.BooleanField(default=True, verbose_name="Ενεργό")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Τμήμα"
        verbose_name_plural = "Τμήματα"
        unique_together = ('name', 'service')

    def __str__(self):
        return f"{self.name} - {self.service}"

    def clean(self):
        """Validation"""
        if self.parent_department == self:
            raise ValidationError("Το τμήμα δεν μπορεί να είναι γονέας του εαυτού του")
        
        # Για ΣΔΕΥ πρέπει να έχει supervisor αλλά όχι manager
        if self.is_virtual:
            if not self.sdeu_supervisor:
                raise ValidationError("Τα εικονικά τμήματα (ΣΔΕΥ) πρέπει να έχουν υπεύθυνο")
            if self.manager:
                raise ValidationError("Τα εικονικά τμήματα (ΣΔΕΥ) δεν έχουν προϊστάμενο")

    def get_effective_manager(self):
        """Επιστρέφει τον αρμόδιο προϊστάμενο (για ΣΔΕΥ είναι του γονικού ΚΕΔΑΣΥ)"""
        if self.is_virtual and self.service.parent_service:
            return self.service.parent_service.manager
        return self.manager


class SystemSetting(models.Model):
    """Ρυθμίσεις συστήματος"""
    key = models.CharField(max_length=100, unique=True, verbose_name="Κλειδί")
    value = models.TextField(verbose_name="Τιμή")
    description = models.TextField(blank=True, verbose_name="Περιγραφή")
    is_system = models.BooleanField(default=False, verbose_name="Ρύθμιση συστήματος")
    updated_by = models.ForeignKey(
        'accounts.Employee',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Ενημερώθηκε από"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Ρύθμιση Συστήματος"
        verbose_name_plural = "Ρυθμίσεις Συστήματος"

    def __str__(self):
        return f"{self.key}: {self.value[:50]}"

    @classmethod
    def get_setting(cls, key, default=None):
        """Επιστρέφει τιμή ρύθμισης"""
        try:
            return cls.objects.get(key=key).value
        except cls.DoesNotExist:
            return default

    @classmethod
    def set_setting(cls, key, value, user=None):
        """Ορίζει τιμή ρύθμισης"""
        setting, created = cls.objects.get_or_create(
            key=key,
            defaults={'value': value, 'updated_by': user}
        )
        if not created:
            setting.value = value
            setting.updated_by = user
            setting.save()
        return setting

    @classmethod
    def get_default_settings(cls):
        """Δημιουργία προεπιλεγμένων ρυθμίσεων"""
        defaults = {
            'DEFAULT_REGULAR_LEAVE_DAYS': ('24', 'Προεπιλεγμένες ημέρες κανονικής άδειας'),
            'SYSTEM_EMAIL_FROM': ('noreply@sch.gr', 'Email αποστολέα συστήματος'),
            'PDF_HEADER_LOGO_TEXT': ('ΕΛΛΗΝΙΚΗ ΔΗΜΟΚΡΑΤΙΑ...', 'Κείμενο επικεφαλίδας PDF'),
            'WORKING_DAYS_PER_WEEK': ('5', 'Εργάσιμες ημέρες εβδομάδας'),
            'MAX_FILE_SIZE_MB': ('5', 'Μέγιστο μέγεθος αρχείου σε MB'),
            'ALLOWED_FILE_TYPES': ('PDF,JPG,JPEG', 'Επιτρεπόμενοι τύποι αρχείων'),
        }
        
        for key, (value, desc) in defaults.items():
            cls.objects.get_or_create(
                key=key,
                defaults={'value': value, 'description': desc, 'is_system': True}
            )
```

---

## 3. LEAVES APP - ΔΙΑΧΕΙΡΙΣΗ ΑΔΕΙΩΝ

### leaves/models.py

```python
from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, timedelta
import uuid

class LeaveType(models.Model):
    """Τύποι αδειών"""
    id_adeias = models.CharField(max_length=50, unique=True, verbose_name="ID άδειας")
    eidos_adeias = models.CharField(max_length=200, verbose_name="Είδος άδειας")
    eidos_adeias_aplo = models.CharField(max_length=100, verbose_name="Είδος άδειας απλό")
    keimeno_thematos_adeia = models.TextField(verbose_name="Κείμενο θέματος άδειας")
    keimeno_apofasis_adeia = models.TextField(verbose_name="Κείμενο απόφασης άδειας")
    thematikos_fakelos = models.CharField(max_length=200, blank=True, verbose_name="Θεματικός φάκελος")
    
    # Workflow settings
    requires_manager_approval = models.BooleanField(default=True, verbose_name="Απαιτεί έγκριση προϊσταμένου")
    requires_attachments = models.BooleanField(default=False, verbose_name="Απαιτεί συνημμένα")
    requires_protocol = models.BooleanField(default=True, verbose_name="Απαιτεί πρωτόκολλο")
    requires_decision_pdf = models.BooleanField(default=True, verbose_name="Απαιτεί PDF απόφασης")
    bypass_manager_for_sick_leave = models.BooleanField(
        default=False, 
        verbose_name="Παράκαμψη προϊσταμένου για αναρρωτικές"
    )
    
    # Settings
    is_active = models.BooleanField(default=True, verbose_name="Ενεργός")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Τύπος Άδειας"
        verbose_name_plural = "Τύποι Αδειών"
        ordering = ['eidos_adeias']

    def __str__(self):
        return self.eidos_adeias

    @classmethod
    def get_default_types(cls):
        """Δημιουργία προεπιλεγμένων τύπων αδειών"""
        types = [
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
        
        for type_data in types:
            cls.objects.get_or_create(id_adeias=type_data['id_adeias'], defaults=type_data)


class LeaveStatus(models.Model):
    """Καταστάσεις αδειών"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Όνομα κατάστασης")
    description = models.TextField(blank=True, verbose_name="Περιγραφή")
    color_code = models.CharField(max_length=7, default="#CCCCCC", verbose_name="Χρώμα (HEX)")
    is_final_status = models.BooleanField(default=False, verbose_name="Τελική κατάσταση")
    order_priority = models.PositiveIntegerField(default=0, verbose_name="Σειρά προτεραιότητας")
    is_active = models.BooleanField(default=True, verbose_name="Ενεργή")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Κατάσταση Άδειας"
        verbose_name_plural = "Καταστάσεις Αδειών"
        ordering = ['order_priority', 'name']

    def __str__(self):
        return self.name

    @classmethod
    def get_default_statuses(cls):
        """Δημιουργία προεπιλεγμένων καταστάσεων"""
        statuses = [
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
        
        for name, desc, color, is_final, priority in statuses:
            cls.objects.get_or_create(
                name=name,
                defaults={
                    'description': desc,
                    'color_code': color,
                    'is_final_status': is_final,
                    'order_priority': priority
                }
            )


class LeaveRequest(models.Model):
    """Αιτήσεις αδειών"""
    
    # Βασικά στοιχεία
    employee = models.ForeignKey(
        'accounts.Employee', 
        on_delete=models.CASCADE, 
        verbose_name="Υπάλληλος"
    )
    leave_type = models.ForeignKey(LeaveType, on_delete=models.PROTECT, verbose_name="Τύπος άδειας")
    status = models.ForeignKey(LeaveStatus, on_delete=models.PROTECT, verbose_name="Κατάσταση")
    
    # Διαστήματα άδειας (υπολογίζεται από periods)
    total_days = models.PositiveIntegerField(
        default=0, 
        validators=[MinValueValidator(1)],
        verbose_name="Συνολικές ημέρες"
    )
    working_days = models.PositiveIntegerField(
        default=0,
        verbose_name="Εργάσιμες ημέρες"
    )
    
    # Ειδικά πεδία
    description = models.TextField(
        blank=True, 
        verbose_name="Περιγραφή",
        help_text="Για προφορικές/εορταστικές άδειες"
    )
    is_self_declaration = models.BooleanField(
        default=False, 
        verbose_name="Με υπεύθυνη δήλωση"
    )
    comments_to_leave_department = models.TextField(
        blank=True,
        verbose_name="Σχόλια προς τμήμα αδειών"
    )
    
    # Πρωτόκολλα
    kedasy_protocol_number = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name="Αρ. Πρωτοκόλλου ΚΕΔΑΣΥ/ΚΕΠΕΑ"
    )
    kedasy_protocol_date = models.DateField(
        null=True, 
        blank=True, 
        verbose_name="Ημερομηνία πρωτοκόλλου ΚΕΔΑΣΥ/ΚΕΠΕΑ"
    )
    pdede_protocol_number = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name="Αρ. Πρωτ. ΠΔΕΔΕ"
    )
    pdede_protocol_date = models.DateField(
        null=True, 
        blank=True, 
        verbose_name="Ημερομηνία πρωτοκόλλου ΠΔΕΔΕ"
    )
    
    # Εγκρίσεις
    manager_approved_at = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name="Ημερομηνία έγκρισης προϊσταμένου"
    )
    manager_approved_by = models.ForeignKey(
        'accounts.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_leave_requests',
        verbose_name="Εγκρίθηκε από προϊστάμενο"
    )
    manager_rejection_reason = models.TextField(
        blank=True,
        verbose_name="Λόγος μη έγκρισης από προϊστάμενο"
    )
    
    # Επεξεργασία
    processed_by = models.ForeignKey(
        'accounts.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_leave_requests',
        verbose_name="Επεξεργάστηκε από"
    )
    processed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Ημερομηνία επεξεργασίας"
    )
    processing_notes = models.TextField(
        blank=True,
        verbose_name="Σημειώσεις επεξεργασίας"
    )
    
    # Τμήμα αδειών
    leave_dept_rejection_reason = models.TextField(
        blank=True,
        verbose_name="Λόγοι απόρριψης από τμήμα αδειών"
    )
    required_documents = models.TextField(
        blank=True,
        verbose_name="Απαιτούμενα δικαιολογητικά"
    )
    
    # Υγειονομική επιτροπή
    HEALTH_COMMITTEE_CHOICES = [
        ('', '---'),
        ('Εγκρίθηκε', 'Εγκρίθηκε'),
        ('Απορρίφθηκε', 'Απορρίφθηκε'),
    ]
    health_committee_decision = models.CharField(
        max_length=50,
        choices=HEALTH_COMMITTEE_CHOICES,
        blank=True,
        verbose_name="Απόφαση υγειονομικής επιτροπής"
    )
    health_committee_notes = models.TextField(
        blank=True,
        verbose_name="Σημειώσεις υγειονομικής επιτροπής"
    )
    health_committee_decided_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Ημερομηνία απόφασης επιτροπής"
    )
    
    # Parent/Child relationships για ανακλήσεις
    parent_leave = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Γονική άδεια"
    )
    is_cancellation = models.BooleanField(default=False, verbose_name="Είναι ανάκληση")
    is_partial_cancellation = models.BooleanField(default=False, verbose_name="Είναι μερική ανάκληση")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Δημιουργήθηκε")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ενημερώθηκε")
    created_by = models.ForeignKey(
        'accounts.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_leave_requests',
        verbose_name="Δημιουργήθηκε από"
    )

    class Meta:
        verbose_name = "Αίτηση Άδειας"
        verbose_name_plural = "Αιτήσεις Αδειών"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['employee']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['leave_type']),
            models.Index(fields=['employee', 'status']),
        ]

    def __str__(self):
        return f"{self.employee} - {self.leave_type} ({self.created_at.strftime('%d/%m/%Y')})"

    def clean(self):
        """Validation"""
        # Έλεγχος πρωτοκόλλου ΚΕΔΑΣΥ
        if (self.kedasy_protocol_number and not self.kedasy_protocol_date) or \
           (not self.kedasy_protocol_number and self.kedasy_protocol_date):
            raise ValidationError("Και τα δύο πεδία πρωτοκόλλου ΚΕΔΑΣΥ πρέπει να συμπληρωθούν")
        
        # Έλεγχος πρωτοκόλλου ΠΔΕΔΕ
        if (self.pdede_protocol_number and not self.pdede_protocol_date) or \
           (not self.pdede_protocol_number and self.pdede_protocol_date):
            raise ValidationError("Και τα δύο πεδία πρωτοκόλλου ΠΔΕΔΕ πρέπει να συμπληρωθούν")

    def save(self, *args, **kwargs):
        """Override save για υπολογισμούς"""
        # Υπολογισμός εργάσιμων ημερών από periods
        if self.pk:  # Αν υπάρχει ήδη
            self.calculate_working_days()
        super().save(*args, **kwargs)

    def calculate_working_days(self):
        """Υπολογίζει τις εργάσιμες ημέρες από τα periods"""
        from calendar.models import PublicHoliday
        
        total_working_days = 0
        for period in self.periods.all():
            # Υπολογισμός εργάσιμων ημερών για κάθε period
            current_date = period.start_date
            working_days = 0
            
            while current_date <= period.end_date:
                # Έλεγχος αν είναι Σαββατοκύριακο
                if current_date.weekday() < 5:  # Δευτέρα=0, Παρασκευή=4
                    # Έλεγχος για αργίες
                    is_holiday = PublicHoliday.objects.filter(
                        date=current_date,
                        is_active=True
                    ).filter(
                        models.Q(is_national=True) | 
                        models.Q(city=self.employee.current_service.city)
                    ).exists()
                    
                    if not is_holiday:
                        working_days += 1
                
                current_date += timedelta(days=1)
            
            period.working_days = working_days
            period.save()
            total_working_days += working_days
        
        self.working_days = total_working_days
        self.total_days = sum(period.total_days for period in self.periods.all())

    def can_be_cancelled_by_employee(self):
        """Ελέγχει αν μπορεί να ανακληθεί από τον υπάλληλο"""
        # Μπορεί να ανακληθεί μέχρι την κατάσταση ΕΠΕΞΕΡΓΑΣΙΑ
        restricted_statuses = ['ΕΠΕΞΕΡΓΑΣΙΑ', 'ΣΗΔΕ_ΠΡΟΣ_ΥΠΟΓΡΑΦΕΣ']
        final_statuses = LeaveStatus.objects.filter(is_final_status=True).values_list('name', flat=True)
        
        return self.status.name not in restricted_statuses and self.status.name not in final_statuses

    def get_next_available_statuses(self):
        """Επιστρέφει τις επόμενες διαθέσιμες καταστάσεις βάσει workflow"""
        current_status = self.status.name
        leave_type = self.leave_type.id_adeias
        service_type = self.employee.current_service.service_type.name
        
        # Workflow logic
        if current_status == 'ΚΑΤΑΧΩΡΗΘΗΚΕ':
            if leave_type == 'ANARROTIKI':
                if service_type == 'ΠΔΕΔΕ':
                    return ['ΓΙΑ_ΠΡΩΤΟΚΟΛΛΟ_ΠΔΕΔΕ']
                else:
                    return ['ΓΙΑ_ΠΡΩΤΟΚΟΛΛΟ_ΚΕΔΑΣΥ']
            else:
                return ['ΕΓΚΡΙΣΗ_ΑΠΟ_ΠΡΟΪΣΤΑΜΕΝΟ']
        
        elif current_status == 'ΕΓΚΡΙΣΗ_ΑΠΟ_ΠΡΟΪΣΤΑΜΕΝΟ':
            if service_type == 'ΠΔΕΔΕ':
                return ['ΓΙΑ_ΠΡΩΤΟΚΟΛΛΟ_ΠΔΕΔΕ', 'ΜΗ_ΕΓΚΡΙΣΗ_ΑΠΟ_ΠΡΟΪΣΤΑΜΕΝΟ']
            else:
                return ['ΓΙΑ_ΠΡΩΤΟΚΟΛΛΟ_ΚΕΔΑΣΥ', 'ΜΗ_ΕΓΚΡΙΣΗ_ΑΠΟ_ΠΡΟΪΣΤΑΜΕΝΟ']
        
        elif current_status == 'ΓΙΑ_ΠΡΩΤΟΚΟΛΛΟ_ΚΕΔΑΣΥ':
            return ['ΓΙΑ_ΠΡΩΤΟΚΟΛΛΟ_ΠΔΕΔΕ']
        
        elif current_status == 'ΓΙΑ_ΠΡΩΤΟΚΟΛΛΟ_ΠΔΕΔΕ':
            return ['ΠΡΟΣ_ΕΠΕΞΕΡΓΑΣΙΑ']
        
        elif current_status == 'ΠΡΟΣ_ΕΠΕΞΕΡΓΑΣΙΑ':
            return ['ΕΠΕΞΕΡΓΑΣΙΑ']
        
        elif current_status == 'ΕΠΕΞΕΡΓΑΣΙΑ':
            return ['ΑΝΑΜΟΝΗ_ΔΙΚΑΙΟΛΟΓΗΤΙΚΩΝ', 'ΑΠΟΡΡΙΨΗ_ΑΠΟ_ΤΜΗΜΑ_ΑΔΕΙΩΝ', 'ΣΗΔΕ_ΠΡΟΣ_ΥΠΟΓΡΑΦΕΣ', 'ΥΓΕΙΟΝΟΜΙΚΗ_ΕΠΙΤΡΟΠΗ']
        
        elif current_status == 'ΑΝΑΜΟΝΗ_ΔΙΚΑΙΟΛΟΓΗΤΙΚΩΝ':
            return ['ΠΡΟΣ_ΕΠΕΞΕΡΓΑΣΙΑ']
        
        elif current_status == 'ΥΓΕΙΟΝΟΜΙΚΗ_ΕΠΙΤΡΟΠΗ':
            return ['ΠΡΟΣ_ΕΠΕΞΕΡΓΑΣΙΑ', 'ΑΠΟΡΡΙΨΗ_ΑΠΟ_ΤΜΗΜΑ_ΑΔΕΙΩΝ']
        
        elif current_status == 'ΣΗΔΕ_ΠΡΟΣ_ΥΠΟΓΡΑΦΕΣ':
            return ['ΟΛΟΚΛΗΡΩΜΕΝΗ', 'ΑΠΟΡΡΙΨΗ_ΑΠΟ_ΤΜΗΜΑ_ΑΔΕΙΩΝ']
        
        elif current_status == 'ΟΛΟΚΛΗΡΩΜΕΝΗ':
            return ['ΑΝΑΚΛΗΣΗ_ΟΛΟΚΛΗΡΩΜΕΝΗΣ_ΑΔΕΙΑΣ']
        
        return []

    def check_sick_leave_health_committee(self):
        """Ελέγχει αν χρειάζεται υγειονομική επιτροπή για αναρρωτικές"""
        if self.leave_type.id_adeias != 'ANARROTIKI':
            return False
        
        # Υπολογισμός συνολικών αναρρωτικών ημερών του έτους
        current_year = timezone.now().year
        total_sick_days = LeaveRequest.objects.filter(
            employee=self.employee,
            leave_type__id_adeias='ANARROTIKI',
            created_at__year=current_year,
            status__is_final_status=True
        ).aggregate(
            total=models.Sum('working_days')
        )['total'] or 0
        
        # Συμπεριλαμβάνουμε και την τρέχουσα αίτηση
        total_sick_days += self.working_days
        
        return total_sick_days > 8

    def check_leave_balance(self):
        """Ελέγχει το υπόλοιπο αδειών"""
        if self.leave_type.id_adeias != 'KANONIKI':
            return True  # Μόνο για κανονικές άδειες
        
        current_balance = self.employee.get_leave_balance()
        return current_balance >= self.working_days


class LeaveRequestPeriod(models.Model):
    """Διαστήματα αδειών (μια αίτηση μπορεί να έχει πολλά διαστήματα)"""
    leave_request = models.ForeignKey(
        LeaveRequest, 
        on_delete=models.CASCADE, 
        related_name='periods',
        verbose_name="Αίτηση άδειας"
    )
    start_date = models.DateField(verbose_name="Από")
    end_date = models.DateField(verbose_name="Έως")
    total_days = models.PositiveIntegerField(verbose_name="Συνολικές ημέρες")
    working_days = models.PositiveIntegerField(default=0, verbose_name="Εργάσιμες ημέρες")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Διάστημα Άδειας"
        verbose_name_plural = "Διαστήματα Αδειών"
        indexes = [
            models.Index(fields=['leave_request']),
            models.Index(fields=['start_date', 'end_date']),
        ]

    def __str__(self):
        return f"{self.start_date.strftime('%d/%m/%Y')} - {self.end_date.strftime('%d/%m/%Y')}"

    def clean(self):
        """Validation"""
        if self.end_date < self.start_date:
            raise ValidationError("Η ημερομηνία λήξης δεν μπορεί να είναι πριν την έναρξη")
        
        # Έλεγχος επικάλυψης με άλλα periods του ίδιου υπαλλήλου
        if self.leave_request_id:
            overlapping = LeaveRequestPeriod.objects.filter(
                leave_request__employee=self.leave_request.employee,
                start_date__lte=self.end_date,
                end_date__gte=self.start_date,
                leave_request__status__is_final_status=False
            ).exclude(pk=self.pk)
            
            if overlapping.exists():
                raise ValidationError("Υπάρχει επικάλυψη με άλλη αίτηση άδειας")

    def save(self, *args, **kwargs):
        """Override save για υπολογισμούς"""
        self.total_days = (self.end_date - self.start_date).days + 1
        super().save(*args, **kwargs)


class BloodDonationTracking(models.Model):
    """Παρακολούθηση αιμοδοσιών"""
    employee = models.ForeignKey(
        'accounts.Employee',
        on_delete=models.CASCADE,
        verbose_name="Υπάλληλος"
    )
    leave_request = models.ForeignKey(
        LeaveRequest,
        on_delete=models.CASCADE,
        verbose_name="Αίτηση άδειας"
    )
    
    # Στοιχεία αιμοδοσίας
    donation_date = models.DateField(verbose_name="Ημερομηνία αιμοδοσίας")
    was_successful = models.BooleanField(null=True, verbose_name="Επιτυχής αιμοδοσία")
    hospital_name = models.CharField(max_length=200, blank=True, verbose_name="Νοσοκομείο")
    certificate_number = models.CharField(max_length=100, blank=True, verbose_name="Αρ. βεβαίωσης")
    
    # Υπόλοιπο ημερών
    additional_days_granted = models.PositiveIntegerField(
        default=0,
        verbose_name="Επιπλέον ημέρες που χορηγήθηκαν"
    )
    additional_days_used = models.PositiveIntegerField(
        default=0,
        verbose_name="Επιπλέον ημέρες που χρησιμοποιήθηκαν"
    )
    
    # Metadata
    year = models.PositiveIntegerField(verbose_name="Έτος")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Παρακολούθηση Αιμοδοσίας"
        verbose_name_plural = "Παρακολούθηση Αιμοδοσιών"
        indexes = [
            models.Index(fields=['employee']),
            models.Index(fields=['year']),
        ]

    def __str__(self):
        return f"{self.employee} - Αιμοδοσία {self.donation_date.strftime('%d/%m/%Y')}"

    def clean(self):
        """Validation"""
        if self.additional_days_granted not in [0, 2]:
            raise ValidationError("Οι επιπλέον ημέρες μπορούν να είναι 0 ή 2")

    def save(self, *args, **kwargs):
        """Override save"""
        if not self.year:
            self.year = self.donation_date.year
        
        # Αν η αιμοδοσία ήταν επιτυχής, δίνουμε 2 επιπλέον ημέρες
        if self.was_successful and self.additional_days_granted == 0:
            self.additional_days_granted = 2
        elif not self.was_successful:
            self.additional_days_granted = 0
        
        super().save(*args, **kwargs)

    @classmethod
    def get_available_blood_donation_days(cls, employee, year=None):
        """Επιστρέφει διαθέσιμες ημέρες αιμοδοσίας"""
        if not year:
            year = timezone.now().year
        
        tracking = cls.objects.filter(employee=employee, year=year)
        total_granted = tracking.aggregate(
            total=models.Sum('additional_days_granted')
        )['total'] or 0
        
        total_used = tracking.aggregate(
            total=models.Sum('additional_days_used')
        )['total'] or 0
        
        return total_granted - total_used
```

---

## 4. ATTACHMENTS APP - ΣΥΝΗΜΜΕΝΑ

### attachments/models.py

```python
from django.db import models
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
import os
import hashlib
import uuid

def upload_to_path(instance, filename):