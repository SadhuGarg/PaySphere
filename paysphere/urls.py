"""
URL configuration for paysphere project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from employee.views import *
# from . import views



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index,name='index'),
    path('registration/', registration,name='registration'),
    path('emp_login/', emp_login,name='emp_login'),
    path('emp_home/', emp_home ,name='emp_home'),
    path('emp_salary/', emp_salary ,name='emp_salary'),

    path('emp_profile/', emp_profile ,name='emp_profile'),
    path('emp_leave/', emp_leave ,name='emp_leave'),
    path('emp_leave_history/', emp_leave_history ,name='emp_leave_history'),
    path('logout/', Logout, name='logout'),
    path('admin_login/', admin_login,name='admin_login'),
    path('admin_home/', admin_home ,name='admin_home'),
    path('create_emp/', create_emp ,name='create_emp'),
    # path('salary_detail/', salary_detail, name='salary_detail'),

    path('leave_requests/', leave_requests ,name='leave_requests'),
    path('edit_employee/', edit_employee ,name='edit_employee'),
    path('delete_employee/<int:employee_id>/', delete_employee, name='delete_employee'),
    path('edit_employee/<int:employee_id>/', edit_employee, name='edit_employee'),  # Add this path
    path('approve_leave/<int:leaveId>/', approve_leave, name='approve_leave'),
    path('reject_leave/<int:leaveId>/', reject_leave, name='reject_leave'), 
    path('approve_leave/<int:leaveId>/', approve_leave, name='approve_leave'),
    path('admin_emp_salary/<int:employee_id>/', admin_emp_salary, name='admin_emp_salary'),
    path('add_salary_detail/', add_salary_detail, name='add_salary_detail'),
    path('get_salary_detail/<int:employee_id>/', get_salary_detail, name='get_salary_detail'),
    path('admin_salary_page/', admin_salary_page, name='admin_salary_page'),
    path('schedule_payment/', schedule_payment, name='schedule_payment'),

    path('credit_salary/<int:employee_id>/', credit_salary, name='credit_salary'),
    path('api/calculate-salary/<int:employee_id>/', admin_emp_salary, name='calculate_salary'),
    path('generate-salary/<int:employee_id>/', generate_salary, name='generate_salary'),
    path('add-payment-date/', add_payment_date, name='add_payment_date'),
    path('delete_payment_date/<int:payment_id>/', delete_payment_date, name='delete_payment_date'),
    path('dashboard/', employee_dashboard, name='employee_dashboard'),


]
