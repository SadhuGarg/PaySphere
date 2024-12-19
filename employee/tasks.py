# from apscheduler.schedulers.background import BackgroundScheduler
# from datetime import datetime
# from django.db.models import F
# from .models import EmployeeDetail, EmployeeSalary, Leave, SalaryDetail

# def credit_salary_task():
#     """Task to credit salaries automatically based on leaves and monthly salary."""
#     employees = EmployeeDetail.objects.all()

#     for employee in employees:
#         # Fetch salary details
#         salary_detail = SalaryDetail.objects.filter(employee=employee).first()
#         if not salary_detail:
#             continue  # Skip if no salary detail

#         monthly_salary = salary_detail.monthlySalary
#         joining_date = employee.joining_date

#         # Ensure this runs only on the joining day of the month
#         if datetime.now().day != joining_date.day:
#             continue

#         # Calculate total leaves in the current month
#         current_month = datetime.now().month
#         current_year = datetime.now().year
#         total_leaves = Leave.objects.filter(
#             employee=employee,
#             requestedStartDate__month=current_month,
#             requestedStartDate__year=current_year,
#             status='Approved',
#         ).count()

#         # Calculate deductions and final salary
#         deduction_per_day = monthly_salary / 30
#         total_deduction = deduction_per_day * total_leaves
#         final_salary = monthly_salary - total_deduction

#         # Record salary in the EmployeeSalary model
#         EmployeeSalary.objects.create(
#             employee=employee,
#             month=current_month,
#             year=current_year,
#             salary=final_salary,
#             deductions=total_deduction,
#             paymentDate=datetime.now(),
#         )



from celery import shared_task
from .models import PaymentSchedule, EmployeeSalary, SalaryDetail
from django.utils.timezone import now

@shared_task
def process_scheduled_payments():
    today = now().date()
    schedules = PaymentSchedule.objects.filter(schedule_date=today, payment_status='Pending')

    for schedule in schedules:
        salary = EmployeeSalary.objects.filter(employee=schedule.employee).first()
        if salary:
            # Mark salary as credited
            salary.salary_credited = 'Yes'
            salary.save()

        # Update schedule status
        schedule.payment_status = 'Paid'
        schedule.save()

from celery import shared_task
from datetime import datetime
from .models import EmployeePaymentDate, EmployeeSalary, Leave, EmployeeDetail
from decimal import Decimal

@shared_task
def generate_salaries_for_today():
    today = datetime.today().date()
    
    # Find employees whose payment date matches today's date
    employees_with_payment_date = EmployeePaymentDate.objects.filter(payment_date=today)
    
    for record in employees_with_payment_date:
        employee = record.employee
        salary_detail = SalaryDetail.objects.filter(employee=employee).first()
        monthly_salary = salary_detail.monthlySalary if salary_detail else Decimal('0.00')

        month = today.month
        year = today.year

        # Fetch approved leaves for this employee for the current month and year
        total_leaves = Leave.objects.filter(
            employee=employee,
            startDate__month=month,
            startDate__year=year,
            status='Approved'
        ).count()

        # Calculate deductions and final salary
        deduction_per_day = monthly_salary / Decimal(30) if monthly_salary else Decimal('0.00')
        total_deductions = deduction_per_day * Decimal(total_leaves)
        final_salary = monthly_salary - total_deductions

        # Save the generated salary record
        EmployeeSalary.objects.create(
            employee=employee,
            month=month,
            year=year,
            salary=final_salary,
            deductions=total_deductions,
            paymentDate=today,
            salary_credited=False
        )
