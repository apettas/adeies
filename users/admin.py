from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Employee, Role, UserRole

@admin.register(CustomUser)
class CandidateUserAdmin(UserAdmin):
    """Admin για Υποψήφιους Χρήστες (CustomUser)"""
    list_display = ['email', 'username', 'first_name', 'last_name', 'is_employee', 'is_staff', 'is_active']
    list_filter = ['is_employee', 'is_staff', 'is_active', 'date_joined']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['email']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Επιπλέον Πληροφορίες', {'fields': ('is_employee',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )

@admin.register(Employee)
class VerifiedEmployeeAdmin(admin.ModelAdmin):
    """Admin για Πιστοποιημένους Χρήστες (Employee)"""
    list_display = ['get_full_name', 'sch_email', 'current_service', 'department', 'is_active']
    list_filter = ['current_service', 'department', 'employee_type', 'specialty', 'is_active']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'sch_email']
    raw_id_fields = ['user', 'current_service', 'department', 'employee_type', 'specialty']
    
    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_full_name.short_description = 'Ονοματεπώνυμο'

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """Admin για Role"""
    list_display = ['name', 'is_system_role', 'is_active']
    list_filter = ['is_system_role', 'is_active']
    search_fields = ['name', 'description']

@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    """Admin για UserRole"""
    list_display = ['employee', 'role', 'assigned_at', 'is_active']
    list_filter = ['role', 'is_active', 'assigned_at']
    search_fields = ['employee__user__email', 'role__name']
    raw_id_fields = ['employee', 'role']
