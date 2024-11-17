# from django import forms
# from django.contrib.auth.models import User
# from django.contrib.auth.forms import UserCreationForm

# class UserRegistrationForm(UserCreationForm):
#     email = forms.EmailField(required=True)

#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password1', 'password2']


# from django import forms
# from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.models import User
# from .models import Employee


# class UserRegistrationForm(UserCreationForm):
#     email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
#         'class': 'form-control',
#         'placeholder': 'Enter your email address'
#     }))
#     username = forms.CharField(widget=forms.TextInput(attrs={
#         'class': 'form-control',
#         'placeholder': 'Enter your username'
#     }))
#     password1 = forms.CharField(widget=forms.PasswordInput(attrs={
#         'class': 'form-control',
#         'placeholder': 'Enter a strong password'
#     }))
#     password2 = forms.CharField(widget=forms.PasswordInput(attrs={
#         'class': 'form-control',
#         'placeholder': 'Confirm your password'
#     }))

#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password1', 'password2']


# # Employee Form (for adding employee details)
# class EmployeeForm(forms.ModelForm):
#     class Meta:
#         model = Employee
#         fields = ['first_name', 'last_name', 'email', 'phone_number', 'position']
#         widgets = {
#             'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
#             'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
#             'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
#             'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
#             'position': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Position'})
#         }




from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Employee


class UserRegistrationForm(UserCreationForm):
    # Additional fields
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your first name'
    }))
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your last name'
    }))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your email address'
    }))
    phone_number = forms.CharField(max_length=15, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your phone number'
    }))
    secret_code = forms.CharField(max_length=20, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter the secret code'
    }))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'secret_code', 'username', 'password1', 'password2']

    # Optional: You can add custom validation for secret_code if needed
    def clean_secret_code(self):
        secret_code = self.cleaned_data.get('secret_code')
        # Assuming you want to validate the secret code (you can modify this logic as needed)
        if secret_code != 'pay123roll':
            raise forms.ValidationError('Invalid secret code provided.')
        return secret_code


# Employee Form (for adding employee details)
# class EmployeeForm(forms.ModelForm):
#     class Meta:
#         model = Employee
#         fields = ['first_name', 'last_name', 'email', 'phone_number', 'position']
#         widgets = {
#             'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
#             'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
#             'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
#             'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
#             'position': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Position'})
#         }


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'position', 'joining_date', 'salary']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'position': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Position'}),
            'joining_date': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Joining Date', 'type': 'date'}),
            'salary': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Salary'}),
        }