# Generated by Django 3.2.23 on 2024-01-08 21:37

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0041_payment_rest'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
