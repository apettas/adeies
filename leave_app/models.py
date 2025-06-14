"""
Leave app models - Διαχείριση αδειών
"""

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
        'users.Employee', 
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
        'users.Employee',
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
        'users.Employee',
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
        'users.Employee',
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
        from calendar_app.models import PublicHoliday
        
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
                if service_type == 'ΠΕΡΙΦΕΡΕΙΑΚΗ ΔΙΕΥΘΥΝΣΗ':
                    return ['ΓΙΑ_ΠΡΩΤΟΚΟΛΛΟ_ΠΔΕΔΕ']
                else:
                    return ['ΓΙΑ_ΠΡΩΤΟΚΟΛΛΟ_ΚΕΔΑΣΥ']
            else:
                return ['ΕΓΚΡΙΣΗ_ΑΠΟ_ΠΡΟΪΣΤΑΜΕΝΟ']
        
        elif current_status == 'ΕΓΚΡΙΣΗ_ΑΠΟ_ΠΡΟΪΣΤΑΜΕΝΟ':
            if service_type == 'ΠΕΡΙΦΕΡΕΙΑΚΗ ΔΙΕΥΘΥΝΣΗ':
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
        'users.Employee',
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
