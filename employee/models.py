from django.db import models

# Create your models here.
# class Employee(models.Model):
#     first_name = models.CharField(max_length=100)
#     last_name = models.CharField(max_length=100)
#     email = models.EmailField(unique=True)
#     phone_number = models.CharField(max_length=15)
#     position = models.CharField(max_length=100)

#     def __str__(self):
#         return f"{self.first_name} {self.last_name}"

# from django.db import models

# class Employee(models.Model):
#     first_name = models.CharField(max_length=100)
#     last_name = models.CharField(max_length=100)
#     email = models.EmailField(unique=True)
#     phone_number = models.CharField(max_length=15)
#     position = models.CharField(max_length=100)
#     joining_date = models.DateField()  # Joining date field
#     salary = models.DecimalField(max_digits=10, decimal_places=2)  # Salary field

#     def __str__(self):
#         return f"{self.first_name} {self.last_name}"
from django.db import models
from django.utils import timezone  # for current date

class Employee(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    position = models.CharField(max_length=100)
    
    # Add the joining_date field with default to the current date
    joining_date = models.DateField(default=timezone.now)
    salary = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"