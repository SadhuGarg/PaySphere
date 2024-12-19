# Generated by Django 5.1.3 on 2024-12-19 13:28

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0009_paymentschedule_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentschedule',
            name='deductions',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10),
        ),
        migrations.AddField(
            model_name='paymentschedule',
            name='final_salary',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10),
        ),
    ]
