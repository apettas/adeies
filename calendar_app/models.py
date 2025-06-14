"""
Calendar app models - Ημερολόγιο και Αργίες
"""

from django.db import models
from django.core.exceptions import ValidationError
from datetime import date, timedelta

class PublicHoliday(models.Model):
    """Δημόσιες αργίες"""
    name = models.CharField(max_length=200, verbose_name="Όνομα αργίας")
    date = models.DateField(verbose_name="Ημερομηνία")
    year = models.PositiveIntegerField(verbose_name="Έτος")
    is_fixed = models.BooleanField(default=True, verbose_name="Σταθερή αργία")
    is_national = models.BooleanField(default=True, verbose_name="Εθνική αργία")
    city = models.ForeignKey(
        'core_app.City', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        verbose_name="Πόλη (για τοπικές αργίες)"
    )
    is_active = models.BooleanField(default=True, verbose_name="Ενεργή")
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        'users.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Δημιουργήθηκε από"
    )

    class Meta:
        verbose_name = "Δημόσια Αργία"
        verbose_name_plural = "Δημόσιες Αργίες"
        unique_together = ('date', 'city')  # Αποτροπή διπλών εγγραφών
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['year']),
            models.Index(fields=['is_national']),
            models.Index(fields=['city']),
        ]

    def __str__(self):
        city_str = f" ({self.city})" if self.city else ""
        return f"{self.name} - {self.date.strftime('%d/%m/%Y')}{city_str}"

    def clean(self):
        """Validation"""
        if not self.year:
            self.year = self.date.year
            
        # Έλεγχος ότι εθνικές αργίες δεν έχουν city
        if self.is_national and self.city:
            raise ValidationError("Εθνικές αργίες δεν μπορούν να έχουν συγκεκριμένη πόλη")
            
        # Έλεγχος ότι τοπικές αργίες έχουν city
        if not self.is_national and not self.city:
            raise ValidationError("Τοπικές αργίες πρέπει να έχουν συγκεκριμένη πόλη")

    @classmethod
    def create_default_holidays(cls, year=None):
        """Δημιουργία προεπιλεγμένων αργιών για έτος"""
        if not year:
            year = date.today().year
            
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
            cls.objects.get_or_create(
                name=name,
                date=holiday_date,
                defaults={
                    'year': year,
                    'is_fixed': True,
                    'is_national': True
                }
            )
        
        # Τοπικές αργίες
        from core_app.models import City
        try:
            patra = City.objects.get(name='Πάτρα')
            cls.objects.get_or_create(
                name='Άγιος Ανδρέας',
                date=date(year, 11, 30),
                city=patra,
                defaults={
                    'year': year,
                    'is_fixed': True,
                    'is_national': False
                }
            )
        except City.DoesNotExist:
            pass

    @classmethod
    def get_holidays_for_period(cls, start_date, end_date, city=None):
        """Επιστρέφει τις αργίες για ένα διάστημα"""
        holidays = cls.objects.filter(
            date__range=[start_date, end_date],
            is_active=True
        )
        
        if city:
            holidays = holidays.filter(
                models.Q(is_national=True) | models.Q(city=city)
            )
        else:
            holidays = holidays.filter(is_national=True)
            
        return holidays

    @classmethod
    def is_holiday(cls, check_date, city=None):
        """Ελέγχει αν μια ημερομηνία είναι αργία"""
        holidays = cls.objects.filter(
            date=check_date,
            is_active=True
        )
        
        if city:
            holidays = holidays.filter(
                models.Q(is_national=True) | models.Q(city=city)
            )
        else:
            holidays = holidays.filter(is_national=True)
            
        return holidays.exists()


class HolidayOverlapCheck(models.Model):
    """Έλεγχος επικαλύψεων αργιών"""
    date = models.DateField(verbose_name="Ημερομηνία")
    city = models.ForeignKey(
        'core_app.City', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        verbose_name="Πόλη"
    )
    holiday_count = models.PositiveIntegerField(default=1, verbose_name="Αριθμός αργιών")
    last_updated = models.DateTimeField(auto_now=True, verbose_name="Τελευταία ενημέρωση")

    class Meta:
        verbose_name = "Έλεγχος Επικαλύψεων Αργιών"
        verbose_name_plural = "Έλεγχοι Επικαλύψεων Αργιών"
        unique_together = ('date', 'city')

    def __str__(self):
        city_str = f" ({self.city})" if self.city else ""
        return f"{self.date.strftime('%d/%m/%Y')}{city_str} - {self.holiday_count} αργίες"

    @classmethod
    def check_overlaps(cls, check_date, city=None):
        """Ελέγχει για επικαλύψεις και ενημερώνει τον πίνακα"""
        holiday_count = PublicHoliday.objects.filter(
            date=check_date,
            is_active=True
        ).filter(
            models.Q(is_national=True) | models.Q(city=city) if city else models.Q(is_national=True)
        ).count()
        
        if holiday_count > 0:
            overlap, created = cls.objects.get_or_create(
                date=check_date,
                city=city,
                defaults={'holiday_count': holiday_count}
            )
            if not created and overlap.holiday_count != holiday_count:
                overlap.holiday_count = holiday_count
                overlap.save()
                
        return holiday_count


class WorkingDayCalculator:
    """Utility class για υπολογισμό εργάσιμων ημερών"""
    
    @staticmethod
    def calculate_working_days(start_date, end_date, city=None):
        """Υπολογίζει τις εργάσιμες ημέρες μεταξύ δύο ημερομηνιών"""
        if start_date > end_date:
            return 0
            
        current_date = start_date
        working_days = 0
        
        while current_date <= end_date:
            # Έλεγχος αν είναι Σαββατοκύριακο (Σάββατο=5, Κυριακή=6)
            if current_date.weekday() < 5:
                # Έλεγχος για αργίες
                if not PublicHoliday.is_holiday(current_date, city):
                    working_days += 1
                    
            current_date += timedelta(days=1)
            
        return working_days

    @staticmethod
    def get_next_working_day(start_date, city=None):
        """Επιστρέφει την επόμενη εργάσιμη ημέρα"""
        current_date = start_date
        
        while True:
            # Έλεγχος αν είναι εργάσιμη ημέρα
            if current_date.weekday() < 5 and not PublicHoliday.is_holiday(current_date, city):
                return current_date
                
            current_date += timedelta(days=1)

    @staticmethod
    def is_working_day(check_date, city=None):
        """Ελέγχει αν μια ημερομηνία είναι εργάσιμη"""
        # Έλεγχος Σαββατοκυριάκου
        if check_date.weekday() >= 5:
            return False
            
        # Έλεγχος αργιών
        return not PublicHoliday.is_holiday(check_date, city)

    @staticmethod
    def get_working_days_in_month(year, month, city=None):
        """Επιστρέφει τις εργάσιμες ημέρες σε έναν μήνα"""
        from calendar import monthrange
        
        last_day = monthrange(year, month)[1]
        start_date = date(year, month, 1)
        end_date = date(year, month, last_day)
        
        return WorkingDayCalculator.calculate_working_days(start_date, end_date, city)

    @staticmethod
    def get_working_days_in_year(year, city=None):
        """Επιστρέφει τις εργάσιμες ημέρες σε έναν χρόνο"""
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        
        return WorkingDayCalculator.calculate_working_days(start_date, end_date, city)
