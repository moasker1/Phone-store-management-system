# Generated by Django 3.2.23 on 2024-02-14 19:45

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0115_auto_20240214_2102'),
    ]

    operations = [
        migrations.AddField(
            model_name='loan',
            name='date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='worker',
            name='date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
