# Generated by Django 3.2.23 on 2024-01-07 22:13

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0036_alter_sale_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sale',
            name='date',
            field=models.DateField(default=datetime.date(2024, 1, 7)),
        ),
    ]
