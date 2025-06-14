from django.contrib import admin
from .models import LeaveType, LeaveStatus, LeaveRequest, LeaveRequestPeriod, BloodDonationTracking

admin.site.register(LeaveType)
admin.site.register(LeaveStatus)
admin.site.register(LeaveRequest)
admin.site.register(LeaveRequestPeriod)
admin.site.register(BloodDonationTracking)
