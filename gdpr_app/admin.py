from django.contrib import admin
from .models import GDPRConsent, DocumentVerification, DataProcessingActivity, DataSubjectRequest

admin.site.register(GDPRConsent)
admin.site.register(DocumentVerification)
admin.site.register(DataProcessingActivity)
admin.site.register(DataSubjectRequest)
