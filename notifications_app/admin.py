from django.contrib import admin
from .models import EmailNotification, NotificationPreference, InAppNotification

@admin.register(EmailNotification)
class EmailNotificationAdmin(admin.ModelAdmin):
    list_display = ['subject', 'status', 'sent_at']
    list_filter = ['status', 'sent_at']

@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'email_enabled']
    raw_id_fields = ['employee']

@admin.register(InAppNotification)
class InAppNotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
