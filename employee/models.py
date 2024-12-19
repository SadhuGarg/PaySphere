from datetime import datetime  # Correct import of datetime class
from django.db import models
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from decimal import Decimal


class EmployeeDetail(models.Model):
    employee_id = models.AutoField(primary_key=True)  # Auto-incrementing ID (renamed to employee_id for consistency)
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # One-to-one relationship with User model
    emp_code = models.CharField(max_length=50)  # Employee code
    emp_dept = models.CharField(max_length=50, null=True)  # Employee department
    designation = models.CharField(max_length=50, null=True)  # Job title or designation
    contact = models.CharField(max_length=50, null=True)  # Contact number
    gender = models.CharField(max_length=50, null=True)  # Gender
    joining_date = models.DateField(null=True)  # Date of joining the company
    
    def __str__(self):
        return self.user.username 


class EmployeeSalary(models.Model):
    salaryId = models.AutoField(primary_key=True)  
    employee = models.ForeignKey('EmployeeDetail', on_delete=models.CASCADE)  
    month = models.IntegerField()  
    year = models.IntegerField()  
    salary = models.DecimalField(max_digits=10, decimal_places=2)  
    deductions = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  
    paymentDate = models.DateField()  
    salary_credited = models.BooleanField(default=False)  # Field to indicate if salary is credited
    
    def __str__(self):
        return f"Salary for {self.employee} - {self.month} {self.year}"


class Leave(models.Model):
    leaveId = models.AutoField(primary_key=True)
    employee = models.ForeignKey('EmployeeDetail', on_delete=models.CASCADE)
    leaveType = models.CharField(max_length=50)
    
    requestedStartDate = models.DateField()
    requestedEndDate = models.DateField()
    
    startDate = models.DateField(null=True, blank=True)
    endDate = models.DateField(null=True, blank=True)
    
    daysRequested = models.PositiveIntegerField()
    daysApproved = models.PositiveIntegerField()
    
    status = models.CharField(
        max_length=20, 
        choices=[('Approved', 'Approved'), ('Pending', 'Pending'), ('Rejected', 'Rejected')],
        default='Pending'
    )
    
    reason = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"Leave for {self.employee} from {self.requestedStartDate} to {self.requestedEndDate} ({self.leaveType})"

    def save(self, *args, **kwargs):
        # Automatically calculate the number of requested and approved days before saving the instance
        if isinstance(self.requestedStartDate, str):
            self.requestedStartDate = datetime.strptime(self.requestedStartDate, '%Y-%m-%d').date()
        if isinstance(self.requestedEndDate, str):
            self.requestedEndDate = datetime.strptime(self.requestedEndDate, '%Y-%m-%d').date()

        self.daysRequested = (self.requestedEndDate - self.requestedStartDate).days + 1

        if self.startDate and self.endDate:
            self.daysApproved = (self.endDate - self.startDate).days + 1
        else:
            self.daysApproved = 0  # Default value when not approved yet

        # Check for status change before sending an email
        if not self.pk or self.status != Leave.objects.get(pk=self.pk).status:
            if self.status == 'Pending':
                self.send_leave_requested_email()
            elif self.status == 'Approved':
                self.send_leave_approved_email()
            elif self.status == 'Rejected':
                self.send_leave_rejected_email()

        super().save(*args, **kwargs)

    def send_leave_requested_email(self):
        subject = f"Leave Request from {self.employee.user.username}"
        message = f"Dear HR/Admin,\n\n{self.employee.user.username} has requested {self.leaveType} leave from {self.requestedStartDate} to {self.requestedEndDate}.\n\nReason: {self.reason}\n\nPlease review and approve/reject the request."
        recipient_list = ['sadhugarg14@gmail.com']  # Replace with your HR or Admin email address

        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)

    def send_leave_approved_email(self):
        subject = f"Your Leave Request has been Approved"
        message = f"Dear {self.employee.user.username},\n\nYour request for {self.leaveType} leave from {self.requestedStartDate} to {self.requestedEndDate} has been approved.\n\nEnjoy your leave!"
        # recipient_list = [self.employee.user.email]  # Make sure this exists in your model
        recipient_list = ['sadhugarg14@gmail.com']  # Make sure this exists in your model

        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)

    def send_leave_rejected_email(self):
        subject = f"Your Leave Request has been Rejected"
        message = f"Dear {self.employee.user.username},\n\nYour request for {self.leaveType} leave from {self.requestedStartDate} to {self.requestedEndDate} has been rejected.\n\nReason: {self.reason if self.reason else 'No reason provided.'}"
        # recipient_list = [self.employee.user.email]  # Make sure this exists in your model
        recipient_list = ['sadhugarg14@gmail.com']  # Make sure this exists in your model


        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)



class SalaryDetail(models.Model):
    salaryId = models.AutoField(primary_key=True)  # Auto-incremented salary ID
    employee = models.ForeignKey('EmployeeDetail', on_delete=models.CASCADE)  # Link to EmployeeDetail
    monthlySalary = models.DecimalField(max_digits=10, decimal_places=2)  # Monthly salary
    annualSalary = models.DecimalField(max_digits=15, decimal_places=2)  # Annual salary
    month = models.IntegerField(default=1)  # Add the month field
    year = models.IntegerField(default=2024) 
    created_at = models.DateField(auto_now_add=True)  # When the salary was added

    def __str__(self):
        return f"Salary for {self.employee} - {self.salaryId}"
        


class PaymentSchedule(models.Model):
    employee = models.ForeignKey('EmployeeDetail', on_delete=models.CASCADE)
    schedule_date = models.DateField()
    final_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    payment_status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('Paid', 'Paid'), ('Failed', 'Failed')],
        default='Pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for {self.employee.user.username} on {self.schedule_date} - {self.payment_status}"

    def calculate_final_salary(self):
        """
        Calculate the final salary for the employee and update the model.
        This method fetches the employee's salary details, applies deductions,
        and adds any bonuses (e.g., performance-based bonuses).
        """
        # Fetch the salary details for the employee
        salary_detail = EmployeeSalary.objects.filter(employee=self.employee).first()

        if salary_detail:
            # Ensure salary is a Decimal
            monthly_salary = Decimal(salary_detail.salary)

            # Calculate deductions (e.g., for leaves, taxes, etc.)
            deductions = self.calculate_deductions(monthly_salary)

            # Calculate bonuses (e.g., performance bonuses)
            bonuses = self.calculate_bonuses()

            # Final salary = Base salary - Deductions + Bonuses
            self.final_salary = monthly_salary - deductions + bonuses
        else:
            self.final_salary = Decimal('0.00')  # If no salary data found, set final salary to 0

        self.save()

    def calculate_deductions(self, monthly_salary):
        """
        Calculate deductions based on leaves and any other criteria (e.g., taxes).
        This method can be customized based on your business logic.
        """
        # Ensure monthly_salary is Decimal
        monthly_salary = Decimal(monthly_salary)

        # Calculate leave deduction
        total_leaves = Leave.objects.filter(employee=self.employee).count()  # Count total leaves for the employee
        daily_deduction = monthly_salary / Decimal('30') if monthly_salary else Decimal('0')  # Assume 30 days in a month for simplicity
        total_deduction = daily_deduction * Decimal(total_leaves)  # Deduction for total leaves

        # Calculate tax deductions
        tax_deduction = self.calculate_tax_deduction(monthly_salary)

        # Total deduction includes leave and tax deductions
        total_deduction += tax_deduction

        return total_deduction.quantize(Decimal('0.01'))  # Round to 2 decimal places

    def calculate_bonuses(self):
        """
        Calculate any bonuses (e.g., performance bonuses) that the employee may be eligible for.
        This method can be customized based on your business logic.
        """
        # Calculate performance bonus
        performance_bonus = self.calculate_performance_bonus()
        return performance_bonus.quantize(Decimal('0.01'))  # Round to 2 decimal places

    def calculate_performance_bonus(self):
        """
        Calculate performance bonus based on employee performance.
        For simplicity, we'll assume a fixed bonus percentage based on performance ratings.
        """
        # Example logic: Assume the employee gets a 5% bonus if they have a performance rating
        performance_rating = getattr(self.employee, 'performance_rating', 0)  # Access performance rating
        bonus_percentage = Decimal('0.05')  # Convert percentage to Decimal

        if performance_rating > 3:  # If performance rating is above 3, give a bonus
            salary_detail = EmployeeSalary.objects.filter(employee=self.employee).first()
            if salary_detail:
                # Ensure that salary is Decimal
                salary = Decimal(salary_detail.salary)
                return salary * bonus_percentage  # Both are Decimal now
        return Decimal('0.00')  # No bonus if the performance rating is not satisfactory

    def calculate_tax_deduction(self, monthly_salary):
        """
        Calculate tax deduction for the employee based on their monthly salary.
        Example tax logic (this is a simple example; it can be customized as needed):
        """
        monthly_salary = Decimal(monthly_salary)  # Ensure salary is Decimal

        if monthly_salary <= Decimal('3000'):
            return monthly_salary * Decimal('0.05')  # 5% tax for low-income earners
        elif monthly_salary <= Decimal('6000'):
            return monthly_salary * Decimal('0.10')  # 10% tax for mid-income earners
        else:
            return monthly_salary * Decimal('0.15')  # 15% tax for high-income earners




class EmployeePaymentDate(models.Model):
    employee = models.ForeignKey('EmployeeDetail', on_delete=models.CASCADE)  # Link to EmployeeDetail model
    payment_date = models.DateField()  # Store the payment date for the employee

    def __str__(self):
        return f"Payment Date for {self.employee.user.username} on {self.payment_date}"



