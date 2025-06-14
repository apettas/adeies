"""
Reports app models - Αναφορές και Στατιστικά
"""

from django.db import models

class ReportTemplate(models.Model):
    """Πρότυπα αναφορών"""
    
    REPORT_TYPE_CHOICES = [
        ('LEAVE_SUMMARY', 'Περίληψη αδειών'),
        ('EMPLOYEE_LEAVE_BALANCE', 'Υπόλοιπα αδειών υπαλλήλων'),
        ('DEPARTMENT_STATISTICS', 'Στατιστικά τμήματος'),
        ('MONTHLY_REPORT', 'Μηνιαία αναφορά'),
        ('ANNUAL_REPORT', 'Ετήσια αναφορά'),
        ('LEAVE_CALENDAR', 'Ημερολόγιο αδειών'),
        ('ATTENDANCE_REPORT', 'Αναφορά παρουσιολογίου'),
        ('PENDING_APPROVALS', 'Εκκρεμείς εγκρίσεις'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="Όνομα προτύπου")
    report_type = models.CharField(
        max_length=30, 
        choices=REPORT_TYPE_CHOICES,
        verbose_name="Τύπος αναφοράς"
    )
    description = models.TextField(blank=True, verbose_name="Περιγραφή")
    
    # Configuration
    parameters = models.JSONField(default=dict, verbose_name="Παράμετροι")
    columns = models.JSONField(default=list, verbose_name="Στήλες")
    filters = models.JSONField(default=dict, verbose_name="Φίλτρα")
    
    # Permissions
    is_public = models.BooleanField(default=False, verbose_name="Δημόσια")
    allowed_roles = models.ManyToManyField(
        'users.Role',
        blank=True,
        verbose_name="Επιτρεπόμενοι ρόλοι"
    )
    
    # Metadata
    created_by = models.ForeignKey(
        'users.Employee',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Δημιουργήθηκε από"
    )
    is_active = models.BooleanField(default=True, verbose_name="Ενεργό")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Πρότυπο Αναφοράς"
        verbose_name_plural = "Πρότυπα Αναφορών"
        ordering = ['name']

    def __str__(self):
        return self.name


class ReportExecution(models.Model):
    """Εκτελέσεις αναφορών"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Εκκρεμεί'),
        ('RUNNING', 'Εκτελείται'),
        ('COMPLETED', 'Ολοκληρώθηκε'),
        ('FAILED', 'Απέτυχε'),
    ]
    
    FORMAT_CHOICES = [
        ('PDF', 'PDF'),
        ('EXCEL', 'Excel'),
        ('CSV', 'CSV'),
        ('HTML', 'HTML'),
    ]
    
    template = models.ForeignKey(
        ReportTemplate,
        on_delete=models.CASCADE,
        verbose_name="Πρότυπο"
    )
    executed_by = models.ForeignKey(
        'users.Employee',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Εκτελέστηκε από"
    )
    
    # Parameters
    parameters = models.JSONField(default=dict, verbose_name="Παράμετροι εκτέλεσης")
    output_format = models.CharField(
        max_length=10,
        choices=FORMAT_CHOICES,
        default='PDF',
        verbose_name="Μορφή εξαγωγής"
    )
    
    # Status
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDING',
        verbose_name="Κατάσταση"
    )
    progress = models.PositiveIntegerField(default=0, verbose_name="Πρόοδος (%)")
    
    # Results
    file_path = models.CharField(max_length=500, blank=True, verbose_name="Διαδρομή αρχείου")
    file_size = models.PositiveIntegerField(null=True, blank=True, verbose_name="Μέγεθος αρχείου")
    row_count = models.PositiveIntegerField(null=True, blank=True, verbose_name="Αριθμός γραμμών")
    
    # Timing
    started_at = models.DateTimeField(null=True, blank=True, verbose_name="Ξεκίνησε στις")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Ολοκληρώθηκε στις")
    error_message = models.TextField(blank=True, verbose_name="Μήνυμα σφάλματος")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Δημιουργήθηκε")

    class Meta:
        verbose_name = "Εκτέλεση Αναφοράς"
        verbose_name_plural = "Εκτελέσεις Αναφορών"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.template.name} - {self.get_status_display()} ({self.created_at.strftime('%d/%m/%Y %H:%M')})"

    def start_execution(self):
        """Έναρξη εκτέλεσης"""
        from django.utils import timezone
        self.status = 'RUNNING'
        self.started_at = timezone.now()
        self.save()

    def complete_execution(self, file_path, file_size, row_count):
        """Ολοκλήρωση εκτέλεσης"""
        from django.utils import timezone
        self.status = 'COMPLETED'
        self.completed_at = timezone.now()
        self.file_path = file_path
        self.file_size = file_size
        self.row_count = row_count
        self.progress = 100
        self.save()

    def fail_execution(self, error_message):
        """Αποτυχία εκτέλεσης"""
        from django.utils import timezone
        self.status = 'FAILED'
        self.completed_at = timezone.now()
        self.error_message = error_message
        self.save()


class ScheduledReport(models.Model):
    """Προγραμματισμένες αναφορές"""
    
    FREQUENCY_CHOICES = [
        ('DAILY', 'Καθημερινά'),
        ('WEEKLY', 'Εβδομαδιαία'),
        ('MONTHLY', 'Μηνιαία'),
        ('QUARTERLY', 'Τριμηνιαία'),
        ('YEARLY', 'Ετήσια'),
    ]
    
    template = models.ForeignKey(
        ReportTemplate,
        on_delete=models.CASCADE,
        verbose_name="Πρότυπο αναφοράς"
    )
    name = models.CharField(max_length=200, verbose_name="Όνομα προγραμματισμού")
    
    # Schedule
    frequency = models.CharField(
        max_length=10,
        choices=FREQUENCY_CHOICES,
        verbose_name="Συχνότητα"
    )
    day_of_week = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="0=Δευτέρα, 6=Κυριακή",
        verbose_name="Ημέρα εβδομάδας"
    )
    day_of_month = models.PositiveIntegerField(
        null=True, 
        blank=True,
        verbose_name="Ημέρα μήνα"
    )
    hour = models.PositiveIntegerField(default=8, verbose_name="Ώρα εκτέλεσης")
    
    # Recipients
    recipients = models.ManyToManyField(
        'users.Employee',
        verbose_name="Παραλήπτες",
        related_name="scheduled_reports_as_recipient"
    )
    
    # Configuration
    parameters = models.JSONField(default=dict, verbose_name="Παράμετροι")
    output_format = models.CharField(
        max_length=10,
        choices=ReportExecution.FORMAT_CHOICES,
        default='PDF',
        verbose_name="Μορφή εξαγωγής"
    )
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name="Ενεργός")
    last_run = models.DateTimeField(null=True, blank=True, verbose_name="Τελευταία εκτέλεση")
    next_run = models.DateTimeField(null=True, blank=True, verbose_name="Επόμενη εκτέλεση")
    
    # Metadata
    created_by = models.ForeignKey(
        'users.Employee',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Δημιουργήθηκε από",
        related_name="created_scheduled_reports"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Προγραμματισμένη Αναφορά"
        verbose_name_plural = "Προγραμματισμένες Αναφορές"

    def __str__(self):
        return f"{self.name} ({self.get_frequency_display()})"

    def calculate_next_run(self):
        """Υπολογισμός επόμενης εκτέλεσης"""
        from datetime import datetime, timedelta
        from django.utils import timezone
        
        now = timezone.now()
        next_run = now.replace(hour=self.hour, minute=0, second=0, microsecond=0)
        
        if self.frequency == 'DAILY':
            if next_run <= now:
                next_run += timedelta(days=1)
        elif self.frequency == 'WEEKLY':
            days_ahead = self.day_of_week - next_run.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            next_run += timedelta(days=days_ahead)
        elif self.frequency == 'MONTHLY':
            if next_run.day != self.day_of_month or next_run <= now:
                if next_run.month == 12:
                    next_run = next_run.replace(year=next_run.year + 1, month=1, day=self.day_of_month)
                else:
                    next_run = next_run.replace(month=next_run.month + 1, day=self.day_of_month)
        
        self.next_run = next_run
        self.save()


class DashboardWidget(models.Model):
    """Widgets για dashboard"""
    
    WIDGET_TYPE_CHOICES = [
        ('STAT_CARD', 'Κάρτα στατιστικού'),
        ('CHART', 'Γράφημα'),
        ('TABLE', 'Πίνακας'),
        ('CALENDAR', 'Ημερολόγιο'),
        ('LIST', 'Λίστα'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="Όνομα widget")
    widget_type = models.CharField(
        max_length=20,
        choices=WIDGET_TYPE_CHOICES,
        verbose_name="Τύπος widget"
    )
    
    # Configuration
    data_source = models.CharField(max_length=100, verbose_name="Πηγή δεδομένων")
    configuration = models.JSONField(default=dict, verbose_name="Διαμόρφωση")
    
    # Layout
    position_x = models.PositiveIntegerField(default=0, verbose_name="Θέση X")
    position_y = models.PositiveIntegerField(default=0, verbose_name="Θέση Y")
    width = models.PositiveIntegerField(default=4, verbose_name="Πλάτος")
    height = models.PositiveIntegerField(default=3, verbose_name="Ύψος")
    
    # Permissions
    allowed_roles = models.ManyToManyField(
        'users.Role',
        blank=True,
        verbose_name="Επιτρεπόμενοι ρόλοι"
    )
    
    # Metadata
    is_active = models.BooleanField(default=True, verbose_name="Ενεργό")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Dashboard Widget"
        verbose_name_plural = "Dashboard Widgets"
        ordering = ['position_y', 'position_x']

    def __str__(self):
        return self.name
