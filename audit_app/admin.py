from django.contrib import admin
from .models import LeaveActionLog, EmployeeHistory, SystemLog, AccessLog

admin.site.register(LeaveActionLog)
admin.site.register(EmployeeHistory)
admin.site.register(SystemLog)
admin.site.register(AccessLog)
