"""
Notifications app models - Ειδοποιήσεις και Email
"""

from django.db import models

class EmailNotification(models.Model):
    """Ειδοποιήσεις email"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Εκκρεμεί'),
        ('SENT', 'Στάλθηκε'),
        ('FAILED', 'Απέτυχε'),
        ('RETRYING', 'Επανάληψη'),
    ]
    
    employee = models.ForeignKey(
        'users.Employee', 
        on_delete=models.CASCADE,
        verbose_name="Παραλήπτης"
    )
    leave_request = models.ForeignKey(
        'leave_app.LeaveRequest',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Αίτηση άδειας"
    )
    
    # Email details
    subject = models.CharField(max_length=500, verbose_name="Θέμα")
    body = models.TextField(verbose_name="Κείμενο")
    to_email = models.EmailField(verbose_name="Προς email")
    cc_emails = models.TextField(blank=True, verbose_name="CC emails")
    
    # Status
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES,
        default='PENDING',
        verbose_name="Κατάσταση"
    )
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name="Στάλθηκε στις")
    error_message = models.TextField(blank=True, verbose_name="Μήνυμα σφάλματος")
    retry_count = models.PositiveIntegerField(default=0, verbose_name="Αριθμός επαναλήψεων")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Δημιουργήθηκε")

    class Meta:
        verbose_name = "Ειδοποίηση Email"
        verbose_name_plural = "Ειδοποιήσεις Email"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['employee']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.subject} - {self.employee} ({self.get_status_display()})"


class NotificationPreference(models.Model):
    """Προτιμήσεις ειδοποιήσεων ανά χρήστη"""
    
    NOTIFICATION_TYPES = [
        ('LEAVE_SUBMITTED', 'Υποβολή αίτησης άδειας'),
        ('LEAVE_APPROVED', 'Έγκριση άδειας'),
        ('LEAVE_REJECTED', 'Απόρριψη άδειας'),
        ('LEAVE_NEEDS_APPROVAL', 'Άδεια προς έγκριση'),
        ('LEAVE_DOCUMENTS_NEEDED', 'Απαιτούνται δικαιολογητικά'),
        ('LEAVE_COMPLETED', 'Ολοκλήρωση άδειας'),
        ('LEAVE_CANCELLED', 'Ανάκληση άδειας'),
    ]
    
    employee = models.ForeignKey(
        'users.Employee', 
        on_delete=models.CASCADE,
        verbose_name="Υπάλληλος"
    )
    notification_type = models.CharField(
        max_length=30, 
        choices=NOTIFICATION_TYPES,
        verbose_name="Τύπος ειδοποίησης"
    )
    is_enabled = models.BooleanField(default=True, verbose_name="Ενεργή")
    email_enabled = models.BooleanField(default=True, verbose_name="Email ενεργό")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Προτίμηση Ειδοποίησης"
        verbose_name_plural = "Προτιμήσεις Ειδοποιήσεων"
        unique_together = ('employee', 'notification_type')

    def __str__(self):
        return f"{self.employee} - {self.get_notification_type_display()}"


class InAppNotification(models.Model):
    """In-app ειδοποιήσεις"""
    
    PRIORITY_CHOICES = [
        ('LOW', 'Χαμηλή'),
        ('NORMAL', 'Κανονική'),
        ('HIGH', 'Υψηλή'),
        ('URGENT', 'Επείγουσα'),
    ]
    
    employee = models.ForeignKey(
        'users.Employee', 
        on_delete=models.CASCADE,
        verbose_name="Παραλήπτης"
    )
    title = models.CharField(max_length=200, verbose_name="Τίτλος")
    message = models.TextField(verbose_name="Μήνυμα")
    priority = models.CharField(
        max_length=10, 
        choices=PRIORITY_CHOICES,
        default='NORMAL',
        verbose_name="Προτεραιότητα"
    )
    
    # Status
    is_read = models.BooleanField(default=False, verbose_name="Διαβάστηκε")
    read_at = models.DateTimeField(null=True, blank=True, verbose_name="Διαβάστηκε στις")
    
    # Links
    action_url = models.URLField(blank=True, verbose_name="URL ενέργειας")
    leave_request = models.ForeignKey(
        'leave_app.LeaveRequest',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Αίτηση άδειας"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Δημιουργήθηκε")
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="Λήγει στις")

    class Meta:
        verbose_name = "In-App Ειδοποίηση"
        verbose_name_plural = "In-App Ειδοποιήσεις"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.employee}"

    def mark_as_read(self):
        """Σημείωση ως διαβασμένη"""
        from django.utils import timezone
        self.is_read = True
        self.read_at = timezone.now()
        self.save()
