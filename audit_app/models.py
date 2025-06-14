"""
Audit app models - Logs και History tracking
"""

from django.db import models
from django.utils import timezone

class LeaveActionLog(models.Model):
    """Logs ενεργειών για αιτήσεις αδειών"""
    
    ACTION_CHOICES = [
        ('CREATE', 'Δημιουργία'),
        ('STATUS_CHANGE', 'Αλλαγή κατάστασης'),
        ('APPROVAL', 'Έγκριση'),
        ('REJECTION', 'Απόρριψη'),
        ('CANCELLATION', 'Ανάκληση'),
        ('EDIT', 'Επεξεργασία'),
        ('VIEW', 'Προβολή'),
        ('DOWNLOAD', 'Λήψη'),
        ('ATTACHMENT_ADD', 'Προσθήκη συνημμένου'),
        ('ATTACHMENT_DELETE', 'Διαγραφή συνημμένου'),
        ('PROTOCOL_ADD', 'Προσθήκη πρωτοκόλλου'),
        ('HEALTH_COMMITTEE', 'Υγειονομική επιτροπή'),
    ]
    
    leave_request = models.ForeignKey(
        'leave_app.LeaveRequest', 
        on_delete=models.CASCADE,
        verbose_name="Αίτηση άδειας"
    )
    
    # Αλλαγή κατάστασης
    previous_status = models.ForeignKey(
        'leave_app.LeaveStatus',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='previous_status_logs',
        verbose_name="Προηγούμενη κατάσταση"
    )
    new_status = models.ForeignKey(
        'leave_app.LeaveStatus',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='new_status_logs',
        verbose_name="Νέα κατάσταση"
    )
    
    # Ποιος έκανε την ενέργεια
    user = models.ForeignKey(
        'users.Employee', 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name="Χρήστης"
    )
    action = models.CharField(
        max_length=20, 
        choices=ACTION_CHOICES,
        verbose_name="Ενέργεια"
    )
    
    # Λεπτομέρειες
    notes = models.TextField(blank=True, verbose_name="Σημειώσεις")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP Address")
    user_agent = models.TextField(blank=True, verbose_name="User Agent")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ημερομηνία")

    class Meta:
        verbose_name = "Log Ενέργειας Άδειας"
        verbose_name_plural = "Logs Ενεργειών Αδειών"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['leave_request']),
            models.Index(fields=['user']),
            models.Index(fields=['created_at']),
            models.Index(fields=['action']),
        ]

    def __str__(self):
        return f"{self.leave_request} - {self.get_action_display()} από {self.user} ({self.created_at.strftime('%d/%m/%Y %H:%M')})"

    @classmethod
    def log_action(cls, leave_request, user, action, notes=None, previous_status=None, new_status=None, request=None):
        """Βοηθητική μέθοδος για καταγραφή ενέργειας"""
        ip_address = None
        user_agent = None
        
        if request:
            ip_address = cls.get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        return cls.objects.create(
            leave_request=leave_request,
            user=user,
            action=action,
            notes=notes,
            previous_status=previous_status,
            new_status=new_status,
            ip_address=ip_address,
            user_agent=user_agent
        )

    @staticmethod
    def get_client_ip(request):
        """Παίρνει το IP του client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class EmployeeHistory(models.Model):
    """Ιστορικό αλλαγών υπαλλήλων"""
    
    FIELD_CHOICES = [
        ('specialty', 'Ειδικότητα'),
        ('employee_type', 'Τύπος υπαλλήλου'),
        ('current_service', 'Υπηρεσία'),
        ('department', 'Τμήμα'),
        ('role_description', 'Περιγραφή ρόλου'),
        ('regular_leave_days', 'Ημέρες κανονικής άδειας'),
        ('carryover_leave_days', 'Μεταφερόμενες ημέρες'),
        ('self_declaration_sick_days_remaining', 'Υπόλοιπο ημερών με υπ. δήλωση'),
        ('is_active', 'Ενεργότητα'),
        ('can_request_leave', 'Δικαίωμα αίτησης άδειας'),
        ('personal_email', 'Προσωπικό email'),
        ('phone1', 'Τηλέφωνο 1'),
        ('phone2', 'Τηλέφωνο 2'),
        ('schedule', 'Ωράριο'),
    ]
    
    employee = models.ForeignKey(
        'users.Employee', 
        on_delete=models.CASCADE,
        verbose_name="Υπάλληλος"
    )
    
    # Τι άλλαξε
    field_name = models.CharField(
        max_length=50, 
        choices=FIELD_CHOICES,
        verbose_name="Πεδίο"
    )
    previous_value = models.TextField(blank=True, verbose_name="Προηγούμενη τιμή")
    new_value = models.TextField(blank=True, verbose_name="Νέα τιμή")
    
    # Ποιος έκανε την αλλαγή
    changed_by = models.ForeignKey(
        'users.Employee', 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='employee_changes_made',
        verbose_name="Άλλαξε από"
    )
    change_reason = models.TextField(blank=True, verbose_name="Λόγος αλλαγής")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ημερομηνία αλλαγής")

    class Meta:
        verbose_name = "Ιστορικό Υπαλλήλου"
        verbose_name_plural = "Ιστορικά Υπαλλήλων"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['employee']),
            models.Index(fields=['field_name']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.employee} - {self.get_field_name_display()} ({self.created_at.strftime('%d/%m/%Y')})"

    @classmethod
    def log_change(cls, employee, field_name, previous_value, new_value, changed_by, reason=None):
        """Καταγραφή αλλαγής"""
        return cls.objects.create(
            employee=employee,
            field_name=field_name,
            previous_value=str(previous_value) if previous_value else '',
            new_value=str(new_value) if new_value else '',
            changed_by=changed_by,
            change_reason=reason or ''
        )


class SystemLog(models.Model):
    """Logs συστήματος"""
    
    LEVEL_CHOICES = [
        ('DEBUG', 'Debug'),
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('CRITICAL', 'Critical'),
    ]
    
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, verbose_name="Επίπεδο")
    message = models.TextField(verbose_name="Μήνυμα")
    module = models.CharField(max_length=100, blank=True, verbose_name="Module")
    function_name = models.CharField(max_length=100, blank=True, verbose_name="Function")
    user = models.ForeignKey(
        'users.Employee', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Χρήστης"
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP Address")
    extra_data = models.JSONField(default=dict, blank=True, verbose_name="Επιπλέον δεδομένα")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ημερομηνία")

    class Meta:
        verbose_name = "Log Συστήματος"
        verbose_name_plural = "Logs Συστήματος"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['level']),
            models.Index(fields=['created_at']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"{self.get_level_display()}: {self.message[:50]} ({self.created_at.strftime('%d/%m/%Y %H:%M')})"

    @classmethod
    def log(cls, level, message, module=None, function=None, user=None, request=None, **extra_data):
        """Καταγραφή log"""
        ip_address = None
        if request:
            ip_address = LeaveActionLog.get_client_ip(request)
        
        return cls.objects.create(
            level=level,
            message=message,
            module=module,
            function_name=function,
            user=user,
            ip_address=ip_address,
            extra_data=extra_data
        )


class AccessLog(models.Model):
    """Logs πρόσβασης για GDPR compliance"""
    
    ACCESS_TYPE_CHOICES = [
        ('VIEW', 'Προβολή'),
        ('DOWNLOAD', 'Λήψη'),
        ('EDIT', 'Επεξεργασία'),
        ('DELETE', 'Διαγραφή'),
        ('EXPORT', 'Εξαγωγή'),
        ('PRINT', 'Εκτύπωση'),
    ]
    
    # Ποιος έκανε πρόσβαση
    employee = models.ForeignKey(
        'users.Employee', 
        on_delete=models.CASCADE,
        verbose_name="Χρήστης που έκανε πρόσβαση"
    )
    
    # Σε ποια δεδομένα έγινε πρόσβαση
    viewed_employee = models.ForeignKey(
        'users.Employee',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='access_logs_viewed',
        verbose_name="Υπάλληλος που προβλήθηκε"
    )
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
    
    # Τύπος πρόσβασης
    access_type = models.CharField(
        max_length=10, 
        choices=ACCESS_TYPE_CHOICES,
        verbose_name="Τύπος πρόσβασης"
    )
    url_path = models.CharField(max_length=500, blank=True, verbose_name="URL Path")
    
    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP Address")
    user_agent = models.TextField(blank=True, verbose_name="User Agent")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ημερομηνία πρόσβασης")

    class Meta:
        verbose_name = "Log Πρόσβασης"
        verbose_name_plural = "Logs Πρόσβασης"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['employee']),
            models.Index(fields=['viewed_employee']),
            models.Index(fields=['created_at']),
            models.Index(fields=['access_type']),
        ]

    def __str__(self):
        target = ""
        if self.viewed_employee:
            target = f"δεδομένα του {self.viewed_employee}"
        elif self.leave_request:
            target = f"άδεια {self.leave_request.id}"
        elif self.attachment:
            target = f"συνημμένο {self.attachment.id}"
            
        return f"{self.employee} - {self.get_access_type_display()} {target} ({self.created_at.strftime('%d/%m/%Y %H:%M')})"

    @classmethod
    def log_access(cls, employee, access_type, request=None, viewed_employee=None, leave_request=None, attachment=None):
        """Καταγραφή πρόσβασης"""
        ip_address = None
        user_agent = None
        url_path = None
        
        if request:
            ip_address = LeaveActionLog.get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            url_path = request.path
        
        return cls.objects.create(
            employee=employee,
            viewed_employee=viewed_employee,
            leave_request=leave_request,
            attachment=attachment,
            access_type=access_type,
            url_path=url_path,
            ip_address=ip_address,
            user_agent=user_agent
        )


class DataRetentionLog(models.Model):
    """Logs για διατήρηση και διαγραφή δεδομένων"""
    
    ACTION_CHOICES = [
        ('ARCHIVE', 'Αρχειοθέτηση'),
        ('DELETE', 'Διαγραφή'),
        ('ANONYMIZE', 'Ανωνυμοποίηση'),
        ('EXPORT', 'Εξαγωγή'),
    ]
    
    action = models.CharField(max_length=10, choices=ACTION_CHOICES, verbose_name="Ενέργεια")
    object_type = models.CharField(max_length=50, verbose_name="Τύπος αντικειμένου")
    object_id = models.PositiveIntegerField(verbose_name="ID αντικειμένου")
    object_description = models.TextField(verbose_name="Περιγραφή αντικειμένου")
    
    # Λόγος και χρήστης
    reason = models.TextField(verbose_name="Λόγος")
    performed_by = models.ForeignKey(
        'users.Employee',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Εκτελέστηκε από"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ημερομηνία")
    metadata = models.JSONField(default=dict, blank=True, verbose_name="Metadata")

    class Meta:
        verbose_name = "Log Διατήρησης Δεδομένων"
        verbose_name_plural = "Logs Διατήρησης Δεδομένων"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_action_display()}: {self.object_type} #{self.object_id} ({self.created_at.strftime('%d/%m/%Y')})"
