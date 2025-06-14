"""
Core app models - Βασικές οντότητες του συστήματος
"""

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

    @classmethod
    def get_default_cities(cls):
        """Δημιουργία προεπιλεγμένων πόλεων"""
        cities = [
            ('Πάτρα', 'Αχαΐα'),
            ('Μεσολόγγι', 'Αιτωλοακαρνανία'),
            ('Πύργος', 'Ηλεία'),
            ('Κλειτορία', 'Αχαΐα'),
            ('Κρέστενα', 'Ηλεία'),
        ]
        for name, prefecture in cities:
            cls.objects.get_or_create(name=name, defaults={'prefecture': prefecture})


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

    @classmethod
    def get_default_types(cls):
        """Δημιουργία προεπιλεγμένων τύπων υπηρεσιών"""
        types = [
            ('ΠΕΡΙΦΕΡΕΙΑΚΗ ΔΙΕΥΘΥΝΣΗ', 'ΠΔΕΔΕ', 1, False),
            ('ΚΕΔΑΣΥ', 'ΚΕΔΑΣΥ', 2, True),
            ('ΚΕΠΕΑ', 'ΚΕΠΕΑ', 2, True),
            ('ΣΔΕΥ', 'ΣΔΕΥ', 3, True),
        ]
        for name, abbr, level, requires_protocol in types:
            cls.objects.get_or_create(
                name=name,
                defaults={
                    'abbreviation': abbr,
                    'level': level,
                    'requires_kedasy_protocol': requires_protocol
                }
            )


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
        'users.Employee', 
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

    @classmethod
    def create_default_services(cls):
        """Δημιουργία προεπιλεγμένων υπηρεσιών"""
        # Πρώτα βεβαιωνόμαστε ότι υπάρχουν τα service types και cities
        ServiceType.get_default_types()
        City.get_default_cities()
        
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
        pdede, _ = cls.objects.get_or_create(
            name='ΠΔΕΔΕ',
            defaults={
                'full_name': 'Περιφερειακή Διεύθυνση Εκπαίδευσης Δυτικής Ελλάδας',
                'service_type': pdede_type,
                'city': patra
            }
        )
        
        # ΚΕΔΑΣΥ
        kedasy_data = [
            ('ΚΕΔΑΣΥ 1ο ΠΑΤΡΑΣ', patra),
            ('ΚΕΔΑΣΥ 2ο ΠΑΤΡΑΣ', patra),
            ('ΚΕΔΑΣΥ ΑΙΤ/ΝΙΑΣ', mesolongi),
            ('ΚΕΔΑΣΥ ΗΛΕΙΑΣ', pyrgos),
        ]
        
        kedasy_services = {}
        for name, city in kedasy_data:
            service, _ = cls.objects.get_or_create(
                name=name,
                defaults={
                    'service_type': kedasy_type,
                    'parent_service': pdede,
                    'city': city
                }
            )
            kedasy_services[name] = service
        
        # ΚΕΠΕΑ
        kepea_data = [
            ('ΚΕΠΕΑ ΑΧΑΙΑΣ', kleitoria),
            ('ΚΕΠΕΑ ΗΛΕΙΑΣ', krestena),
            ('ΚΕΠΕΑ ΑΙΤΝΙΑΣ', mesolongi),
        ]
        
        for name, city in kepea_data:
            cls.objects.get_or_create(
                name=name,
                defaults={
                    'service_type': kepea_type,
                    'parent_service': pdede,
                    'city': city
                }
            )


class Department(models.Model):
    """Τμήματα υπηρεσιών"""
    name = models.CharField(max_length=200, verbose_name="Όνομα τμήματος")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name="Υπηρεσία")
    manager = models.ForeignKey(
        'users.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Προϊστάμενος",
        related_name="managed_departments"
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
        'users.Employee',
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

    @classmethod
    def create_default_departments(cls):
        """Δημιουργία προεπιλεγμένων τμημάτων"""
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
                cls.objects.get_or_create(
                    name=dept_name,
                    service=pdede
                )
                
        except Service.DoesNotExist:
            pass  # Services haven't been created yet


class SystemSetting(models.Model):
    """Ρυθμίσεις συστήματος"""
    key = models.CharField(max_length=100, unique=True, verbose_name="Κλειδί")
    value = models.TextField(verbose_name="Τιμή")
    description = models.TextField(blank=True, verbose_name="Περιγραφή")
    is_system = models.BooleanField(default=False, verbose_name="Ρύθμιση συστήματος")
    updated_by = models.ForeignKey(
        'users.Employee',
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
