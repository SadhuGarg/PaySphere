from email.utils import parsedate
from django.shortcuts import render,redirect,get_object_or_404

import employee
from .models import *
from django.contrib.auth import authenticate,login,logout
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .form import *
from datetime import datetime
from django.http import JsonResponse
from django.db.models import Sum
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from django.http import HttpResponse
from django.utils.dateparse import parse_date
from datetime import date
from celery import shared_task
from datetime import datetime



def index(request):
    return render(request,'index.html')


@login_required
def registration(request):
    error = ""
    if request.method== "POST":
        fn = request.POST['firstname']
        ln = request.POST['lastname']
        ec = request.POST['empcode']
        em = request.POST['email']
        pwd = request.POST['pwd']
        try:
            user =User.objects.create_user(first_name=fn,last_name =ln,username=em,password=pwd)
            EmployeeDetail.objects.create(user=user,emp_code=ec)
            error="no"
        except:
            error = "yes"
    return render(request,'registration.html',locals())


def emp_login(request):
    error =""
    if request.method == 'POST':
        u= request.POST['emailid']
        p= request.POST['password']
        user = authenticate(username = u,password = p)
        if user:
            login(request,user)
            error ="no"
        else:
            error = "yes"
    return render(request,'emp_login.html',locals())

@login_required
def emp_home(request):
    return render(request,'emp_home.html')



@login_required
def emp_leave (request):
    if request.method == "POST":
        # Retrieve form data
        leave_type = request.POST['leave_type']
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        reason = request.POST.get('reason', '')  # Optional field
        
        # Get the logged-in employee details
        employee = EmployeeDetail.objects.get(user=request.user)
        
        # Create a Leave record with status as Pending
        leave = Leave(
            employee=employee,
            leaveType=leave_type,
            requestedStartDate=start_date,
            requestedEndDate=end_date,
            reason=reason,
            status='Pending'  # Set initial status as Pending
        )
        
        leave.save()  # Save the leave application

        # Redirect to leave history after applying
        return redirect('emp_leave_history')

    return render(request, 'emp_leave.html')  # Show the leave application form

@login_required
def emp_leave_history(request):
    try:
        # Get the EmployeeDetail instance for the logged-in user
        employee_detail = EmployeeDetail.objects.get(user=request.user)
    except EmployeeDetail.DoesNotExist:
        # Handle the case where the employee detail doesn't exist for the logged-in user
        employee_detail = None

    if employee_detail:
        # Fetch the employee's applied leaves
        applied_leaves = Leave.objects.filter(employee=employee_detail)  # Now filtering by employee_detail
    else:
        applied_leaves = []

    context = {
        'applied_leaves': applied_leaves
    }

    return render(request, 'emp_leave_history.html', context)


@login_required
def emp_profile(request):
    try:
        # Assuming 'user' is the ForeignKey in EmployeeDetail pointing to the User model
        employee = EmployeeDetail.objects.get(user=request.user)
    except EmployeeDetail.DoesNotExist:
        employee = None  # Handle case where employee details are not found
    
    context = {
        'employee': employee  # Pass the single employee object
    }
    return render(request, 'emp_profile.html', context)


def admin_login(request):
    error =""
    if request.method == 'POST':
        u= request.POST['username']
        p= request.POST['pwd']
        user = authenticate(username = u,password = p)
        if user.is_staff:
            login(request,user)
            error ="no"
        else:
            error = "yes"
    return render(request,'admin_login.html',locals())


@login_required
def admin_home(request):
    if not request.user.is_staff:
        return redirect('admin_login')  # Redirect if user is not an admin

    employees = EmployeeDetail.objects.all()  # Get all employees from the database
    return render(request, 'admin_home.html', {'employees': employees})



@login_required
def edit_employee(request, employee_id):
    # Fetch the employee details by employee_id
    employee = get_object_or_404(EmployeeDetail, employee_id=employee_id)

    if request.method == 'POST':
        # Create a form instance with the submitted data
        form = EmployeeDetailForm(request.POST, instance=employee)
        if form.is_valid():
            # Save the form data to update the employee details
            form.save()
            messages.success(request, "Employee details updated successfully.")
            return redirect('admin_home')  # Redirect back to the admin home page after saving
    else:
        # Pre-fill the form with the current employee details
        form = EmployeeDetailForm(instance=employee)

    return render(request, 'edit_employee.html', {'form': form, 'employee': employee})



@login_required
def delete_employee(request, employee_id):
    if not request.user.is_staff:
        return redirect('admin_login')  # Redirect if user is not admin
    
    # Fetch the employee using employee_id (primary key in the EmployeeDetail model)
    employee = get_object_or_404(EmployeeDetail, employee_id=employee_id)
    
    # Delete the employee record
    user = employee.user  # Get the associated User

    employee.delete()
    user.delete()  # Delete the associated User record


    # Show a success message and redirect back to the admin home page
    messages.success(request, 'Employee deleted successfully.')
    return redirect('admin_home')  # Redirect to the admin home page after deletion



def create_emp(request):
    error = ""
    if request.method== "POST":
        fn = request.POST['firstname']
        ln = request.POST['lastname']
        ec = request.POST['empcode']
        em = request.POST['email']
        pwd = request.POST['pwd']
        try:
            user =User.objects.create_user(first_name=fn,last_name =ln,username=em,password=pwd)
            EmployeeDetail.objects.create(user=user,emp_code=ec)
            error="no"
        except:
            error = "yes"
    # return render(request,'registration.html',locals())
    return render(request,'create_emp.html',locals())


@login_required
def Logout(request):
    logout(request)
    return redirect('emp_login')  



def leave_requests(request):
    if not request.user.is_staff:
        return redirect('admin_login')  # Redirect if user is not admin
    
    leave_requests = Leave.objects.all().order_by('-requestedStartDate')  # Ensure all leaves are fetched
    
    return render(request, 'leave_requests.html', {'leave_requests': leave_requests})




@login_required
def approve_leave(request, leaveId):
    if not request.user.is_staff:
        return redirect('admin_login')  # Redirect if user is not admin

    leave = get_object_or_404(Leave, leaveId=leaveId)

    if request.method == 'POST':
        form = ApproveLeaveForm(request.POST, instance=leave)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.status = 'Approved'
            leave.daysApproved = (leave.endDate - leave.startDate).days + 1
            leave.save()
            messages.success(request, f"Leave request for {leave.employee.user.first_name} has been approved with custom dates.")
            return redirect('leave_requests')
    else:
        form = ApproveLeaveForm(instance=leave)

    return render(request, 'approve_leave.html', {'form': form, 'leave': leave})


@login_required
def reject_leave(request, leaveId):
    if not request.user.is_staff:
        return redirect('admin_login')  # Redirect if user is not admin

    # Use leaveId instead of id
    leave = get_object_or_404(Leave, leaveId=leaveId)
    leave.status = 'Rejected'
    leave.save()
    
    messages.error(request, f"Leave request for {leave.employee.user.first_name} has been rejected.")
    return redirect('leave_requests')

@login_required
def add_salary_detail(request):
    if not request.user.is_staff:
        return redirect('admin_login')  # Redirect if the user is not admin
    
    if request.method == 'POST':
        form = SalaryDetailForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Salary details have been successfully added.")
            return redirect('add_salary_detail')  # Redirect to the same page after saving
    else:
        form = SalaryDetailForm()

    return render(request, 'add_salary_detail.html', {'form': form})




from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from decimal import Decimal

@login_required
def admin_emp_salary(request, employee_id):
    if not request.user.is_staff:
        return redirect('admin_login')  # Redirect if the user is not an admin

    # Fetch employee details
    employee = get_object_or_404(EmployeeDetail, employee_id=employee_id)
    salary_detail = SalaryDetail.objects.filter(employee=employee).first()  # Fetch salary details
    monthly_salary = salary_detail.monthlySalary if salary_detail else Decimal('0.00')

    if request.method == 'POST':
        # If this is an API call to calculate salary based on selected payment date
        if request.headers.get('Content-Type') == 'application/json':
            try:
                body = json.loads(request.body)
                payment_date = body.get('payment_date')
                selected_date = datetime.strptime(payment_date, '%Y-%m-%d')
                month = selected_date.month
                year = selected_date.year

                # Calculate total leaves for the selected month and year
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

                return JsonResponse({
                    'deductions': round(total_deductions, 2),
                    'final_salary': round(final_salary, 2)
                })
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=400)

        # If this is a form submission to generate salary
        form = GenerateSalaryForm(request.POST)
        if form.is_valid():
            payment_date = form.cleaned_data['paymentDate']
            month = payment_date.month
            year = payment_date.year

            # Calculate total leaves for the selected month and year
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

            # Save salary record
            EmployeeSalary.objects.create(
                employee=employee,
                month=month,
                year=year,
                salary=final_salary,
                deductions=total_deductions,
                paymentDate=payment_date,
                salary_credited=False
            )

            messages.success(request, f"Salary for {employee.user.username} has been successfully generated.")
            return redirect('admin_emp_salary', employee_id=employee.employee_id)

    else:
        # Pre-fill the form with default data if needed
        form = GenerateSalaryForm()

    return render(request, 'admin_emp_salary.html', {
        'form': form,
        'employee': employee,
        'monthly_salary': monthly_salary,
    })



from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from datetime import datetime
from decimal import Decimal
import json



@login_required
def generate_salary(request, employee_id):
    if not request.user.is_staff:
        return redirect('admin_login')  # Redirect non-admin users to login

    # Fetch the employee details
    employee = get_object_or_404(EmployeeDetail, employee_id=employee_id)
    salary_detail = SalaryDetail.objects.filter(employee=employee).first()
    monthly_salary = salary_detail.monthlySalary if salary_detail else Decimal('0.00')

    # Fetch the payment date from the EmployeePaymentDate model
    payment_date_record = EmployeePaymentDate.objects.filter(employee=employee).first()
    if not payment_date_record:
        messages.error(request, "No payment date set for this employee.")
        return redirect('admin_emp_salary', employee_id=employee_id)
    
    payment_date = payment_date_record.payment_date

    if request.method == 'POST':
        try:
            # Parse form or JSON payload
            if request.headers.get('Content-Type') == 'application/json':
                payload = json.loads(request.body)
                payment_date = payload.get('payment_date')
            else:
                payment_date = request.POST.get('paymentDate')

            if not payment_date:
                raise ValueError("Payment date is required.")

            # Convert payment_date to a datetime object
            selected_date = datetime.strptime(payment_date, '%Y-%m-%d')
            month = selected_date.month
            year = selected_date.year

            # Fetch leaves for the selected month and year
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

            # Save salary record in EmployeeSalary model
            salary_record = EmployeeSalary.objects.create(
                employee=employee,
                month=month,
                year=year,
                salary=final_salary,
                deductions=total_deductions,
                paymentDate=selected_date,
                salary_credited=False
            )

            # Success response for JSON or form submission
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({
                    'message': 'Salary generated successfully.',
                    'salary_record': {
                        'employee': employee_id,
                        'month': month,
                        'year': year,
                        'salary': round(final_salary, 2),
                        'deductions': round(total_deductions, 2),
                        'payment_date': payment_date
                    }
                })

            messages.success(request, f"Salary for {employee.user.username} has been successfully generated.")
            return redirect('admin_emp_salary', employee_id=employee_id)

        except Exception as e:
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({'error': str(e)}, status=400)
            messages.error(request, f"Error generating salary: {str(e)}")
            return redirect('admin_emp_salary', employee_id=employee_id)

    return render(request, 'admin_emp_salary.html', {
        'employee': employee,
        'monthly_salary': monthly_salary,
    })




@login_required
def get_salary_detail(request, employee_id):
    if not request.user.is_staff:
        return redirect('admin_login')  # Redirect if user is not admin
    
    salary_detail = SalaryDetail.objects.filter(employee_id=employee_id).first()
    
    if salary_detail:
        return JsonResponse({
            'monthlySalary': salary_detail.monthlySalary,
        })
    else:
        return JsonResponse({
            'monthlySalary': 0,  # Default value if no salary detail found
        })


@login_required
def admin_salary_page(request):
    if not request.user.is_staff:
        return redirect('admin_login')  # Redirect if user is not admin

    # Fetch all employees
    employees = EmployeeDetail.objects.all().select_related('user')
    employee_data = []

    # Current month and year
    current_date = datetime.now()
    current_month = current_date.month
    current_year = current_date.year

    for employee in employees:
        # Fetch salary details for the employee
        salary_detail = SalaryDetail.objects.filter(employee=employee).first()
        monthly_salary = salary_detail.monthlySalary if salary_detail else Decimal('0.00')

        # Calculate leaves for the current month
        total_leaves = Leave.objects.filter(
            employee=employee,
            startDate__month=current_month,
            startDate__year=current_year,
            status='Approved'
        ).count()

        # Calculate deductions and final salary
        deduction_per_day = monthly_salary / Decimal(30) if monthly_salary else Decimal('0.00')
        total_deduction = deduction_per_day * Decimal(total_leaves)
        final_salary = monthly_salary - total_deduction

        # Check if salary is already credited (you can adjust this logic)
        salary_credited = EmployeeSalary.objects.filter(
            employee=employee,
            month=current_month,
            year=current_year
        ).exists()

        # Append the employee data
        employee_data.append({
            'employee': employee,
            'monthly_salary': round(monthly_salary, 2),
            'total_leaves': total_leaves,
            'total_deduction': round(total_deduction, 2),
            'final_salary': round(final_salary, 2),
            'salary_credited': 'Yes' if salary_credited else 'No',
            'month': current_month,
            'year': current_year,
        })

    return render(request, 'admin_salary_page.html', {'employee_data': employee_data})



@login_required
def emp_salary(request):
    try:
        # Get the EmployeeDetail for the logged-in user
        employee = request.user.employeedetail
    except EmployeeDetail.DoesNotExist:
        # Handle case where no EmployeeDetail exists for the user
        return render(request, 'emp_salary.html', {'salary_data': None})

    # Fetch the latest salary detail for this employee from EmployeeSalary model
    salary_record = EmployeeSalary.objects.filter(employee=employee).order_by('-paymentDate').first()

    if salary_record:
        salary_data = {
            'month': salary_record.month,
            'year': salary_record.year,
            'monthly_salary': salary_record.salary + salary_record.deductions,  # Adding deductions back to get monthly salary
            'total_leaves': (salary_record.deductions / (salary_record.salary / 30)) if salary_record.salary > 0 else 0,
            'total_deduction': salary_record.deductions,
            'final_salary': salary_record.salary,
        }
    else:
        salary_data = None

    return render(request, 'emp_salary.html', {'salary_data': salary_data})



def credit_salary(request, employee_id):
    # Fetch the employee by employee_id
    try:
        employee = EmployeeDetail.objects.get(employee_id=employee_id)
    except EmployeeDetail.DoesNotExist:
        return redirect('schedule_payment')  # Redirect if employee not found

    # Now handle salary crediting (update payment status)
    payment_schedule = PaymentSchedule.objects.filter(employee=employee, payment_status='Pending').first()

    if payment_schedule:
        payment_schedule.payment_status = 'Paid'
        payment_schedule.save()

        # Optionally, show a success message
        messages.success(request, f"Salary credited for {employee.user.username}.")
    else:
        messages.warning(request, f"No pending salary found for {employee.user.username}.")

    return redirect('schedule_payment')  # Redirect back to schedule payment page

def schedule_payment_view(request):
    # Fetch all PaymentSchedule data with related employee details
    schedule_data = PaymentSchedule.objects.select_related('employee', 'employee__user').all()

    # Fetch all employees to populate the dropdown for scheduling
    employees = EmployeeDetail.objects.all()

    context = {
        'schedule_data': schedule_data,  # To pass the schedule data to the template
        'employees': employees,  # To pass the list of employees to the template
    }

    return render(request, 'schedule_payment.html', context)

def schedule_payment(request):
    if not request.user.is_staff:
        return redirect('admin_login')  # Redirect if user is not an admin

    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        schedule_date = request.POST.get('schedule_date')

        # Fetch the employee using the 'employee_id'
        employee = get_object_or_404(EmployeeDetail, employee_id=employee_id)

        try:
            # Try to get the existing payment schedule for this employee and date
            existing_schedule = PaymentSchedule.objects.get(employee=employee, schedule_date=schedule_date)
            # If it exists, delete it
            existing_schedule.delete()
            messages.info(request, f"Old payment schedule for {employee.user.username} on {schedule_date} deleted.")
        except PaymentSchedule.DoesNotExist:
            # If no existing schedule found, we can skip deletion
            pass

        # Create a new payment schedule entry
        schedule = PaymentSchedule(employee=employee, schedule_date=schedule_date)
        schedule.calculate_final_salary()
        schedule.save()

        messages.success(request, f"New payment schedule for {employee.user.username} on {schedule_date} created.")

    # Fetch all employees with salary details
    employees = EmployeeDetail.objects.all()
    schedules = PaymentSchedule.objects.select_related('employee').all()

    # Fetch salary and leave data for display
    employee_data = []
    for employee in employees:
        salary_data = EmployeeSalary.objects.filter(employee=employee).first()

        if salary_data:
            monthly_salary = salary_data.salary
            total_leaves = Leave.objects.filter(employee=employee).count()
            daily_deduction = monthly_salary / 30 if monthly_salary else 0
            total_deduction = daily_deduction * total_leaves
            final_salary = round(monthly_salary - total_deduction, 2)

            employee_data.append({
                'employee': employee,
                'monthly_salary': monthly_salary,
                'total_leaves': total_leaves,
                'total_deduction': round(total_deduction, 2),
                'final_salary': final_salary,
                'salary_credited': salary_data.salary_credited,
                'month': salary_data.month,
                'year': salary_data.year,
            })
        else:
            employee_data.append({
                'employee': employee,
                'monthly_salary': 0,
                'total_leaves': 0,
                'total_deduction': 0,
                'final_salary': 0,
                'salary_credited': False,
                'month': 'N/A',
                'year': 'N/A',
            })

    context = {
        'employees': employees,
        'schedules': schedules,
        'employee_data': employee_data,
    }

    return render(request, 'schedule_payment.html', context)


@shared_task
def process_scheduled_payments():
    schedules = PaymentSchedule.objects.filter(
        payment_status='Pending',
        schedule_date=date.today()
    )

    for schedule in schedules:
        schedule.payment_status = 'Successfully Paid'
        schedule.save()

        # Send email notification
        employee = schedule.employee
        subject = f"Salary Credited for {employee.user.first_name} {employee.user.last_name}"
        message = (
            f"Dear {employee.user.first_name},\n\n"
            f"Your salary for the scheduled date {schedule.schedule_date} "
            f"has been successfully credited.\n\n"
            f"Thank you for your hard work!\n\n"
            f"Regards,\nHR Team"
        )
        recipient_list = [employee.user.email]
        from_email = '77rohangarg@gmail.com'

        send_mail(subject, message, from_email, recipient_list)



from django.shortcuts import render, redirect
from .form import EmployeePaymentDateForm
from .models import EmployeePaymentDate
@login_required
def add_payment_date(request):
    if not request.user.is_staff:
        return redirect('admin_login')  # Redirect if the user is not an admin

    if request.method == 'POST':
        form = EmployeePaymentDateForm(request.POST)
        if form.is_valid():
            form.save()  # Save the payment date record
            return redirect('add_payment_date')  # Reload the page after saving

    else:
        form = EmployeePaymentDateForm()

    # Get the list of employees to populate the dropdown
    employee_list = EmployeeDetail.objects.all()
    
    # Get all the payment dates to display in the table
    payment_dates = EmployeePaymentDate.objects.all()

    return render(request, 'add_payment_date.html', {
        'form': form,
        'employee_list': employee_list,
        'payment_dates': payment_dates
    })

@login_required
def view_payment_dates(request):
    if not request.user.is_staff:
        return redirect('admin_login')  # Redirect if the user is not an admin

    payment_dates = EmployeePaymentDate.objects.all()

    return render(request, 'view_payment_dates.html', {'payment_dates': payment_dates})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import EmployeePaymentDate

@login_required
def delete_payment_date(request, payment_id):
    if not request.user.is_staff:
        return redirect('admin_login')  # Redirect if the user is not an admin

    # Get the payment date object
    payment = get_object_or_404(EmployeePaymentDate, id=payment_id)

    # Delete the payment date
    payment.delete()

    # Show success message
    messages.success(request, "Payment date has been successfully deleted.")

    # Redirect back to the add_payment_date page to refresh the table
    return redirect('add_payment_date')












# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required
# from .models import EmployeeDetail, Leave

# @login_required
# def employee_dashboard(request):
#     # Get the logged-in user
#     user = request.user
    
#     try:
#         # Get employee details for the logged-in user
#         employee = EmployeeDetail.objects.get(user=user)
        
#         # Get the leaves for the employee
#         current_leaves = Leave.objects.filter(employee=employee).order_by('-requestedStartDate')  # Ordered by latest
        
#     except EmployeeDetail.DoesNotExist:
#         employee = None
#         current_leaves = None

#     context = {
#         'employee': employee,
#         'current_leaves': current_leaves,
#     }
    
#     return render(request, 'employee_dashboard.html', context)





from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import EmployeeDetail, Leave
from collections import Counter

@login_required
def employee_dashboard(request):
    user = request.user
    try:
        employee = EmployeeDetail.objects.get(user=user)
        current_leaves = Leave.objects.filter(employee=employee).order_by('-requestedStartDate')
        
        # Aggregate leave data by type
        leave_counts = Counter(leave.leaveType for leave in current_leaves)
        
        leave_data = {
            'labels': list(leave_counts.keys()),
            'data': list(leave_counts.values()),
        }
    except EmployeeDetail.DoesNotExist:
        employee = None
        current_leaves = None
        leave_data = {'labels': [], 'data': []}

    context = {
        'employee': employee,
        'current_leaves': current_leaves,
        'leave_data': leave_data,
    }
    return render(request, 'employee_dashboard.html', context)


