from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm,EmployeeForm
from .models import Employee

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Save user after validation (secret_code check is done in the form)
            form.save()
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'employee/register.html', {'form': form})


# # Register view
# def register(request):
#     if request.method == 'POST':
#         form = UserRegistrationForm(request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Registration successful!')
#             return redirect('login')
#     else:
#         form = UserRegistrationForm()
#     return render(request, 'employee/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')  # Redirects to the dashboard if login is successful
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'employee/login.html')


# @login_required
# def dashboard(request):
#     # return render(request, 'employee/dashboard.html', {'user': request.user})
#     return render(request, 'employee/dashboard.html')

# Dashboard view
@login_required
def dashboard(request):
    employees = Employee.objects.all()  # Fetch all employees to display on the dashboard
    return render(request, 'employee/dashboard.html', {'employees': employees})

# Logout view
def user_logout(request):
    logout(request)
    return redirect('login')


# Add Employee view
@login_required
def add_employee(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()  # Save the employee to the database
            messages.success(request, 'Employee added successfully!')
            return redirect('dashboard')  # Redirect back to the dashboard after adding the employee
    else:
        form = EmployeeForm()
    return render(request, 'employee/add_employee.html', {'form': form})


# Delete Employee view
@login_required
def delete_employee(request, employee_id):
    employee = get_object_or_404(Employee, pk=employee_id)
    employee.delete()
    messages.success(request, f'Employee {employee.first_name} {employee.last_name} has been deleted successfully.')
    return redirect('dashboard')

@login_required
def edit_employee(request, employee_id):
    # Get the employee object or return 404 if not found
    employee = get_object_or_404(Employee, id=employee_id)
    
    if request.method == 'POST':
        # Populate the form with POST data and the existing instance
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()  # Save the updated employee details
            messages.success(request, f'Employee {employee.first_name} updated successfully!')
            return redirect('dashboard')  # Redirect to the dashboard
    else:
        # Create a form instance pre-filled with the employee's details
        form = EmployeeForm(instance=employee)
    
    return render(request, 'employee/add_employee.html', {'form': form})