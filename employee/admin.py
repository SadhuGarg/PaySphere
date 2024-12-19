from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(EmployeeDetail)

admin.site.register(EmployeeSalary)

admin.site.register(Leave)


admin.site.register(SalaryDetail)


admin.site.register(PaymentSchedule)


admin.site.register(EmployeePaymentDate)