"""
Users app models - Χρήστες και Ρόλοι
"""

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
import uuid


class CustomUserManager(BaseUserManager):
    """Custom user manager για το CustomUser model"""
    
    def create_user(self, email, password=None, **extra_fields):
        """Δημιουργία κανονικού χρήστη"""
        if not email:
            raise ValueError('Το email είναι υποχρεωτικό')
        
        email = self.normalize_email(email)
        # Θέτω το username ίσο με το email αν δεν δοθεί
        if 'username' not in extra_fields:
            extra_fields['username'] = email
            
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Δημιουργία superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
            
        return self.create_user(email, password, **extra_fields)


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
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Υποψήφιος Χρήστης"
        verbose_name_plural = "Υποψήφιοι Χρήστες"

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
    
    # Υπηρεσιακά στοιχεία - Foreign Keys (θα δημιουργηθούν στο core_app)
    specialty = models.ForeignKey('core_app.Specialty', on_delete=models.PROTECT, verbose_name="Ειδικότητα")
    employee_type = models.ForeignKey('core_app.EmployeeType', on_delete=models.PROTECT, verbose_name="Τύπος υπαλλήλου")
    current_service = models.ForeignKey('core_app.Service', on_delete=models.PROTECT, verbose_name="Τρέχουσα υπηρεσία")
    department = models.ForeignKey('core_app.Department', on_delete=models.PROTECT, verbose_name="Τμήμα")
    
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
        verbose_name = "Πιστοποιημένος Χρήστης"
        verbose_name_plural = "Πιστοποιημένοι Χρήστες"
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
        from leave_app.models import LeaveRequest
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
        from leave_app.models import LeaveRequest
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
