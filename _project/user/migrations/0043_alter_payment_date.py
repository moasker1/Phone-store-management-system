# Generated by Django 3.2.23 on 2024-01-08 21:40

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0042_alter_payment_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2024, 1, 8, 21, 40, 37, 208110, tzinfo=utc)),
        ),
    ]
