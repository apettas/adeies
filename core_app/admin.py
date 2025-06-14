from django.contrib import admin
from .models import (
    EmployeeType, Specialty, City, ServiceType, Service, Department, SystemSetting
)

@admin.register(EmployeeType)
class EmployeeTypeAdmin(admin.ModelAdmin):
    """Admin για EmployeeType"""
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name']

@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    """Admin για Specialty"""
    list_display = ['specialty_full', 'specialty_short', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['specialty_full', 'specialty_short']

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    """Admin για City"""
    list_display = ['name', 'prefecture', 'is_active']
    list_filter = ['prefecture', 'is_active']
    search_fields = ['name', 'prefecture']

@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    """Admin για ServiceType"""
    list_display = ['name', 'abbreviation', 'level', 'requires_kedasy_protocol', 'is_active']
    list_filter = ['level', 'requires_kedasy_protocol', 'is_active']
    search_fields = ['name', 'abbreviation']

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """Admin για Service"""
    list_display = ['name', 'service_type', 'parent_service', 'city', 'is_active']
    list_filter = ['service_type', 'city', 'is_active']
    search_fields = ['name', 'full_name']
    raw_id_fields = ['parent_service', 'manager']

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """Admin για Department"""
    list_display = ['name', 'service', 'is_virtual', 'is_active']
    list_filter = ['service', 'is_virtual', 'is_active']
    search_fields = ['name']
    raw_id_fields = ['service', 'manager', 'parent_department', 'sdeu_supervisor']

@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    """Admin για SystemSetting"""
    list_display = ['key', 'value', 'description', 'updated_at']
    list_filter = ['updated_at']
    search_fields = ['key', 'description']
    readonly_fields = ['updated_at']
