from django.contrib import admin
from .models import PublicHoliday, HolidayOverlapCheck

admin.site.register(PublicHoliday)
admin.site.register(HolidayOverlapCheck)
