# Generated by Django 3.2.23 on 2024-01-15 00:02

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0066_auto_20240115_0155'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='container',
            name='expense',
        ),
        migrations.RemoveField(
            model_name='container',
            name='expense_notes',
        ),
        migrations.RemoveField(
            model_name='container',
            name='expense_type',
        ),
        migrations.AlterField(
            model_name='item',
            name='date',
            field=models.DateField(default=datetime.date(2024, 1, 15)),
        ),
        migrations.AlterField(
            model_name='sale',
            name='date',
            field=models.DateField(default=datetime.date(2024, 1, 15)),
        ),
        migrations.AlterField(
            model_name='seller',
            name='date',
            field=models.DateField(default=datetime.date(2024, 1, 15)),
        ),
        migrations.AlterField(
            model_name='supplier',
            name='date',
            field=models.DateField(default=datetime.date(2024, 1, 15)),
        ),
    ]
