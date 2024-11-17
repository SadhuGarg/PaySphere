from django.urls import path
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.user_logout, name='logout'),
    path('add_employee/', views.add_employee, name='add_employee'),  # New path for adding employee
    path('edit_employee/<int:employee_id>/', views.edit_employee, name='edit_employee'),  # New URL for editing an employee
    path('delete_employee/<int:employee_id>/', views.delete_employee, name='delete_employee'),  # URL for deleting employee

]
