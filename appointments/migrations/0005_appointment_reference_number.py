# Generated by Django 5.0.6 on 2024-05-18 10:53

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0004_remove_appointment_start_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='reference_number',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
