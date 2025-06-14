"""
Attachments app models - Συνημμένα αρχεία
"""

from django.db import models
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
import os
import hashlib
import uuid

def upload_to_path(instance, filename):
    """Δημιουργία μοναδικού path για upload"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join('leave_attachments', str(instance.leave_request.employee.id), filename)

class LeaveAttachment(models.Model):
    """Συνημμένα αρχεία αιτήσεων άδειας"""
    
    ATTACHMENT_TYPE_CHOICES = [
        ('SUPPORTING_DOCUMENT', 'Δικαιολογητικό έγγραφο'),
        ('APPLICATION_PDF', 'PDF αίτησης'),
        ('DECISION_PDF', 'PDF απόφασης'),
        ('PROTOCOL_PDF', 'PDF με πρωτόκολλο'),
        ('SELF_DECLARATION', 'Υπεύθυνη δήλωση'),
        ('MEDICAL_CERTIFICATE', 'Ιατρική βεβαίωση'),
        ('BLOOD_DONATION_CERTIFICATE', 'Βεβαίωση αιμοδοσίας'),
    ]
    
    leave_request = models.ForeignKey(
        'leave_app.LeaveRequest', 
        on_delete=models.CASCADE, 
        related_name='attachments',
        verbose_name="Αίτηση άδειας"
    )
    
    # Αρχείο
    file = models.FileField(
        upload_to=upload_to_path,
        validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg'])],
        verbose_name="Αρχείο"
    )
    original_file_name = models.CharField(max_length=255, verbose_name="Αρχικό όνομα αρχείου")
    file_size = models.PositiveIntegerField(verbose_name="Μέγεθος αρχείου (bytes)")
    file_type = models.CharField(max_length=10, verbose_name="Τύπος αρχείου")
    file_hash = models.CharField(max_length=64, blank=True, verbose_name="Hash αρχείου")
    
    # Περιγραφή (υποχρεωτική)
    description = models.TextField(verbose_name="Περιγραφή συνημμένου")
    
    # Τύπος συνημμένου
    attachment_type = models.CharField(
        max_length=50, 
        choices=ATTACHMENT_TYPE_CHOICES,
        default='SUPPORTING_DOCUMENT',
        verbose_name="Τύπος συνημμένου"
    )
    
    # Ασφάλεια
    is_sensitive = models.BooleanField(
        default=False, 
        verbose_name="Ευαίσθητο αρχείο",
        help_text="Για αναρρωτικές άδειες"
    )
    uploaded_by = models.ForeignKey(
        'users.Employee', 
        on_delete=models.PROTECT, 
        verbose_name="Ανέβασε"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Δημιουργήθηκε")

    class Meta:
        verbose_name = "Συνημμένο Αρχείο"
        verbose_name_plural = "Συνημμένα Αρχεία"
        indexes = [
            models.Index(fields=['leave_request']),
            models.Index(fields=['attachment_type']),
        ]

    def __str__(self):
        return f"{self.original_file_name} - {self.leave_request}"

    def clean(self):
        """Validation"""
        # Έλεγχος μεγέθους αρχείου (5MB)
        if self.file and self.file.size > 5242880:
            raise ValidationError("Το αρχείο δεν μπορεί να υπερβαίνει τα 5MB")

    def save(self, *args, **kwargs):
        """Override save"""
        if self.file:
            self.file_size = self.file.size
            self.file_type = self.file.name.split('.')[-1].upper()
            self.original_file_name = self.file.name
            
            # Υπολογισμός hash
            if self.file:
                self.file_hash = self.calculate_file_hash()
            
            # Αν είναι αναρρωτική άδεια, σημείωσε ως sensitive
            if self.leave_request.leave_type.id_adeias == 'ANARROTIKI':
                self.is_sensitive = True
                
        super().save(*args, **kwargs)

    def calculate_file_hash(self):
        """Υπολογισμός SHA-256 hash του αρχείου"""
        hash_sha256 = hashlib.sha256()
        for chunk in self.file.chunks():
            hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

    def can_be_viewed_by(self, user):
        """Έλεγχος αν ο χρήστης μπορεί να δει το αρχείο"""
        employee = user.get_employee()
        if not employee:
            return False
            
        # Ο ιδιοκτήτης μπορεί πάντα να δει
        if employee == self.leave_request.employee:
            return True
            
        # Χειριστές αδειών μπορούν πάντα να δουν
        if employee.userrole_set.filter(role__name='Χειριστής αδειών', is_active=True).exists():
            return True
            
        # Για sensitive αρχεία (αναρρωτικές), μόνο ο ιδιοκτήτης και χειριστές αδειών
        if self.is_sensitive:
            return False
            
        # Προϊστάμενοι μπορούν να δουν μη-sensitive αρχεία των υπαλλήλων τους
        if self.leave_request.employee.department.get_effective_manager() == employee:
            return True
            
        return False
