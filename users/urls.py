"""
URLs για το frontend interface των χρηστών
"""

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

urlpatterns = [
    # Home & Auth
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # User Dashboard & Profile
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    
    # Leave Management
    path('leaves/', views.leave_list, name='leave_list'),
    path('leaves/new/', views.leave_create, name='leave_create'),
    path('leaves/<int:pk>/', views.leave_detail, name='leave_detail'),
    path('leaves/<int:pk>/delete/', views.leave_delete, name='leave_delete'),
    path('leaves/<int:pk>/test-delete/', views.test_simple_delete, name='test_simple_delete'),
    
    # For managers/supervisors
    path('approvals/', views.approval_list, name='approval_list'),
    path('approvals/<int:pk>/approve/', views.approve_leave, name='approve_leave'),
    path('approvals/<int:pk>/reject/', views.reject_leave, name='reject_leave'),
]