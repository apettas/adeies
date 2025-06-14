"""
GDPR app models - GDPR compliance και Data Protection
"""

from django.db import models
import uuid

class GDPRConsent(models.Model):
    """Συναινέσεις GDPR των χρηστών"""
    employee = models.ForeignKey(
        'users.Employee', 
        on_delete=models.CASCADE,
        verbose_name="Υπάλληλος"
    )
    consent_text = models.TextField(verbose_name="Κείμενο συναίνεσης")
    consent_version = models.CharField(max_length=20, verbose_name="Έκδοση συναίνεσης")
    
    # Τεχνικά στοιχεία
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP Address")
    user_agent = models.TextField(blank=True, verbose_name="User Agent")
    
    # Metadata
    consented_at = models.DateTimeField(auto_now_add=True, verbose_name="Ημερομηνία συναίνεσης")

    class Meta:
        verbose_name = "Συναίνεση GDPR"
        verbose_name_plural = "Συναινέσεις GDPR"
        ordering = ['-consented_at']
        indexes = [
            models.Index(fields=['employee']),
            models.Index(fields=['consented_at']),
        ]

    def __str__(self):
        return f"{self.employee} - Συναίνεση v{self.consent_version} ({self.consented_at.strftime('%d/%m/%Y %H:%M')})"

    @classmethod
    def get_default_consent_text(cls):
        """Προεπιλεγμένο κείμενο συναίνεσης"""
        return """Αποδέχομαι την επεξεργασία των προσωπικών μου δεδομένων (όνομα, ΑΦΜ, υπηρεσία, συνημμένα, κ.λπ.) από την ΠΔΕΔΕ για τη διαχείριση της αίτησης άδειας, σύμφωνα με τον GDPR. Έχω ενημερωθεί για τα δικαιώματά μου (πρόσβαση, διόρθωση, διαγραφή) και την Πολιτική Απορρήτου."""

    @classmethod
    def record_consent(cls, employee, request=None, version="1.0"):
        """Καταγραφή συναίνεσης"""
        consent_text = cls.get_default_consent_text()
        
        ip_address = None
        user_agent = None
        if request:
            from audit_app.models import LeaveActionLog
            ip_address = LeaveActionLog.get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        return cls.objects.create(
            employee=employee,
            consent_text=consent_text,
            consent_version=version,
            ip_address=ip_address,
            user_agent=user_agent
        )

    @classmethod
    def has_valid_consent(cls, employee):
        """Ελέγχει αν ο χρήστης έχει έγκυρη συναίνεση"""
        return cls.objects.filter(employee=employee).exists()


class DocumentVerification(models.Model):
    """Επαλήθευση γνησιότητας εγγράφων"""
    
    DOCUMENT_TYPE_CHOICES = [
        ('APPLICATION', 'Αίτηση άδειας'),
        ('DECISION', 'Απόφαση άδειας'),
        ('PROTOCOL', 'Έγγραφο με πρωτόκολλο'),
        ('ATTACHMENT', 'Συνημμένο'),
    ]
    
    # Μοναδικός κωδικός επαλήθευσης
    document_uuid = models.UUIDField(
        default=uuid.uuid4, 
        unique=True, 
        verbose_name="Κωδικός επαλήθευσης"
    )
    
    # Σύνδεση με άδεια ή συνημμένο
    leave_request = models.ForeignKey(
        'leave_app.LeaveRequest',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Αίτηση άδειας"
    )
    attachment = models.ForeignKey(
        'attachments_app.LeaveAttachment',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Συνημμένο"
    )
    
    # Τύπος εγγράφου
    document_type = models.CharField(
        max_length=20, 
        choices=DOCUMENT_TYPE_CHOICES,
        verbose_name="Τύπος εγγράφου"
    )
    
    # Στοιχεία εγγράφου
    document_title = models.CharField(max_length=200, blank=True, verbose_name="Τίτλος εγγράφου")
    document_hash = models.CharField(max_length=64, blank=True, verbose_name="Hash εγγράφου")
    document_metadata = models.JSONField(default=dict, blank=True, verbose_name="Metadata εγγράφου")
    
    # Ποιος δημιούργησε
    created_by = models.ForeignKey(
        'users.Employee', 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name="Δημιουργήθηκε από"
    )
    
    # Verification info
    is_active = models.BooleanField(default=True, verbose_name="Ενεργό")
    verified_count = models.PositiveIntegerField(default=0, verbose_name="Φορές επαλήθευσης")
    last_verified_at = models.DateTimeField(null=True, blank=True, verbose_name="Τελευταία επαλήθευση")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Δημιουργήθηκε")

    class Meta:
        verbose_name = "Επαλήθευση Εγγράφου"
        verbose_name_plural = "Επαληθεύσεις Εγγράφων"
        indexes = [
            models.Index(fields=['document_uuid']),
            models.Index(fields=['leave_request']),
            models.Index(fields=['document_type']),
        ]

    def __str__(self):
        return f"{self.get_document_type_display()} - {self.document_uuid}"

    def verify(self):
        """Σημειώνει μια επαλήθευση"""
        from django.utils import timezone
        self.verified_count += 1
        self.last_verified_at = timezone.now()
        self.save()

    @classmethod
    def create_for_leave_request(cls, leave_request, document_type, created_by, title=None):
        """Δημιουργία verification για αίτηση άδειας"""
        return cls.objects.create(
            leave_request=leave_request,
            document_type=document_type,
            document_title=title or f"{document_type} για {leave_request}",
            created_by=created_by
        )

    @classmethod
    def create_for_attachment(cls, attachment, created_by):
        """Δημιουργία verification για συνημμένο"""
        return cls.objects.create(
            attachment=attachment,
            document_type='ATTACHMENT',
            document_title=attachment.description,
            document_hash=attachment.file_hash,
            created_by=created_by
        )

    @classmethod
    def verify_document(cls, verification_uuid):
        """Επαλήθευση εγγράφου με UUID"""
        try:
            verification = cls.objects.get(
                document_uuid=verification_uuid,
                is_active=True
            )
            verification.verify()
            return verification
        except cls.DoesNotExist:
            return None


class DataProcessingActivity(models.Model):
    """Καταγραφή δραστηριοτήτων επεξεργασίας δεδομένων"""
    
    ACTIVITY_TYPE_CHOICES = [
        ('COLLECTION', 'Συλλογή'),
        ('STORAGE', 'Αποθήκευση'),
        ('PROCESSING', 'Επεξεργασία'),
        ('SHARING', 'Κοινοποίηση'),
        ('DELETION', 'Διαγραφή'),
        ('ANONYMIZATION', 'Ανωνυμοποίηση'),
        ('EXPORT', 'Εξαγωγή'),
    ]
    
    PURPOSE_CHOICES = [
        ('LEAVE_MANAGEMENT', 'Διαχείριση αδειών'),
        ('ADMINISTRATIVE', 'Διοικητικοί σκοποί'),
        ('LEGAL_COMPLIANCE', 'Νομική συμμόρφωση'),
        ('AUDIT', 'Έλεγχος'),
        ('REPORTING', 'Αναφορές'),
        ('SUPPORT', 'Υποστήριξη'),
    ]
    
    # Στοιχεία δραστηριότητας
    activity_type = models.CharField(
        max_length=20, 
        choices=ACTIVITY_TYPE_CHOICES,
        verbose_name="Τύπος δραστηριότητας"
    )
    purpose = models.CharField(
        max_length=20, 
        choices=PURPOSE_CHOICES,
        verbose_name="Σκοπός επεξεργασίας"
    )
    
    # Δεδομένα που επεξεργάστηκαν
    data_subject = models.ForeignKey(
        'users.Employee',
        on_delete=models.CASCADE,
        verbose_name="Υποκείμενο δεδομένων"
    )
    data_categories = models.TextField(verbose_name="Κατηγορίες δεδομένων")
    
    # Ποιος επεξεργάστηκε
    processed_by = models.ForeignKey(
        'users.Employee',
        on_delete=models.SET_NULL,
        null=True,
        related_name='data_processing_activities',
        verbose_name="Επεξεργάστηκε από"
    )
    
    # Λεπτομέρειες
    description = models.TextField(verbose_name="Περιγραφή")
    legal_basis = models.CharField(max_length=200, verbose_name="Νομική βάση")
    retention_period = models.CharField(max_length=100, blank=True, verbose_name="Περίοδος διατήρησης")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ημερομηνία")
    metadata = models.JSONField(default=dict, blank=True, verbose_name="Επιπλέον στοιχεία")

    class Meta:
        verbose_name = "Δραστηριότητα Επεξεργασίας Δεδομένων"
        verbose_name_plural = "Δραστηριότητες Επεξεργασίας Δεδομένων"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_activity_type_display()} - {self.data_subject} ({self.created_at.strftime('%d/%m/%Y')})"

    @classmethod
    def log_activity(cls, activity_type, purpose, data_subject, data_categories, processed_by, description, legal_basis="Εκτέλεση καθήκοντος", **metadata):
        """Καταγραφή δραστηριότητας επεξεργασίας"""
        return cls.objects.create(
            activity_type=activity_type,
            purpose=purpose,
            data_subject=data_subject,
            data_categories=data_categories,
            processed_by=processed_by,
            description=description,
            legal_basis=legal_basis,
            metadata=metadata
        )


class DataSubjectRequest(models.Model):
    """Αιτήματα υποκειμένων δεδομένων (GDPR Rights)"""
    
    REQUEST_TYPE_CHOICES = [
        ('ACCESS', 'Δικαίωμα πρόσβασης (Άρθρο 15)'),
        ('RECTIFICATION', 'Δικαίωμα διόρθωσης (Άρθρο 16)'),
        ('ERASURE', 'Δικαίωμα διαγραφής (Άρθρο 17)'),
        ('RESTRICTION', 'Δικαίωμα περιορισμού (Άρθρο 18)'),
        ('PORTABILITY', 'Δικαίωμα φορητότητας (Άρθρο 20)'),
        ('OBJECTION', 'Δικαίωμα αντίρρησης (Άρθρο 21)'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Εκκρεμεί'),
        ('IN_PROGRESS', 'Υπό επεξεργασία'),
        ('COMPLETED', 'Ολοκληρώθηκε'),
        ('REJECTED', 'Απορρίφθηκε'),
    ]
    
    # Στοιχεία αιτήματος
    request_type = models.CharField(
        max_length=20, 
        choices=REQUEST_TYPE_CHOICES,
        verbose_name="Τύπος αιτήματος"
    )
    data_subject = models.ForeignKey(
        'users.Employee',
        on_delete=models.CASCADE,
        verbose_name="Υποκείμενο δεδομένων"
    )
    
    # Περιγραφή και κατάσταση
    description = models.TextField(verbose_name="Περιγραφή αιτήματος")
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES,
        default='PENDING',
        verbose_name="Κατάσταση"
    )
    
    # Επεξεργασία
    assigned_to = models.ForeignKey(
        'users.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_gdpr_requests',
        verbose_name="Ανατέθηκε σε"
    )
    response = models.TextField(blank=True, verbose_name="Απάντηση")
    
    # Χρονικά όρια
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ημερομηνία αιτήματος")
    due_date = models.DateTimeField(verbose_name="Καταληκτική ημερομηνία")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Ημερομηνία ολοκλήρωσης")

    class Meta:
        verbose_name = "Αίτημα Υποκειμένου Δεδομένων"
        verbose_name_plural = "Αιτήματα Υποκειμένων Δεδομένων"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_request_type_display()} - {self.data_subject} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        """Υπολογισμός due_date (30 ημέρες από δημιουργία)"""
        if not self.due_date:
            from datetime import timedelta
            from django.utils import timezone
            self.due_date = timezone.now() + timedelta(days=30)
        super().save(*args, **kwargs)

    def is_overdue(self):
        """Έλεγχος αν έχει λήξει η προθεσμία"""
        from django.utils import timezone
        return timezone.now() > self.due_date and self.status not in ['COMPLETED', 'REJECTED']

    def complete(self, response, completed_by):
        """Ολοκλήρωση αιτήματος"""
        from django.utils import timezone
        self.status = 'COMPLETED'
        self.response = response
        self.completed_at = timezone.now()
        self.save()
        
        # Log της ολοκλήρωσης
        DataProcessingActivity.log_activity(
            activity_type='PROCESSING',
            purpose='LEGAL_COMPLIANCE',
            data_subject=self.data_subject,
            data_categories='GDPR Request Response',
            processed_by=completed_by,
            description=f'Ολοκλήρωση αιτήματος GDPR: {self.get_request_type_display()}',
            request_id=self.id
        )
