from django import forms
from .models import *

class LeaveForm(forms.ModelForm):
    class Meta:
        model = Leave
        fields = ['leaveType', 'requestedStartDate', 'requestedEndDate', 'reason']

    def clean(self):
        cleaned_data = super().clean()
        requestedStartDate = cleaned_data.get('requestedStartDate')
        requestedEndDate = cleaned_data.get('requestedEndDate')

        if requestedStartDate and requestedEndDate:
            if requestedEndDate < requestedStartDate:
                raise forms.ValidationError("End date cannot be before the start date.")
        return cleaned_data

class EmployeeDetailForm(forms.ModelForm):
    class Meta:
        model = EmployeeDetail
        fields = ['emp_code', 'emp_dept', 'designation', 'contact', 'gender', 'joining_date']
        
class ApproveLeaveForm(forms.ModelForm):
    startDate = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    endDate = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)

    class Meta:
        model = Leave
        fields = ['startDate', 'endDate']

class SalaryDetailForm(forms.ModelForm):
    class Meta:
        model = SalaryDetail
        fields = ['employee', 'monthlySalary', 'annualSalary']  # Fields to display in the form



class GenerateSalaryForm(forms.Form):
    employee = forms.ModelChoiceField(queryset=EmployeeDetail.objects.all(), required=True)
    month = forms.IntegerField(min_value=1, max_value=12, required=True)
    year = forms.IntegerField(min_value=2000, required=True)
    salary = forms.DecimalField(max_digits=10, decimal_places=2, required=True)
    deductions = forms.DecimalField(max_digits=10, decimal_places=2, required=False, initial=0)
    paymentDate = forms.DateField(required=True)

    # Optionally, add validation for the form
    def clean(self):
        cleaned_data = super().clean()
        # You can add any custom validation if needed
        return cleaned_data
    
class ApproveLeaveForm(forms.ModelForm):
    startDate = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    endDate = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)

    class Meta:
        model = Leave
        fields = ['startDate', 'endDate']
        
    def save(self, commit=True):
        leave = super().save(commit=False)
        leave.status = 'Approved'  # Set status to approved when this form is saved
        leave.save()  # This triggers the email notification for approval
        return leave



class EmployeePaymentDateForm(forms.ModelForm):
    class Meta:
        model = EmployeePaymentDate
        fields = ['employee', 'payment_date']
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),  # For date input field
        }