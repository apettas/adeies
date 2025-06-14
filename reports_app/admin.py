from django.contrib import admin
from .models import ReportTemplate, ReportExecution, ScheduledReport, DashboardWidget

admin.site.register(ReportTemplate)
admin.site.register(ReportExecution)
admin.site.register(ScheduledReport)
admin.site.register(DashboardWidget)
