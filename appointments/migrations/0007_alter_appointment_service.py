# Generated by Django 5.0.6 on 2024-05-27 19:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0006_dentist_alter_appointment_dentist'),
        ('fee', '0002_alter_fee_service'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='service',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='fee.fee'),
        ),
    ]
