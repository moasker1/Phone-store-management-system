# Generated by Django 3.2.23 on 2024-01-15 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0069_auto_20240115_1859'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='temp_rest',
            field=models.DecimalField(blank=True, decimal_places=2, editable=False, max_digits=15, null=True),
        ),
    ]
