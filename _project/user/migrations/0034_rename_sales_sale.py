# Generated by Django 3.2.23 on 2024-01-07 20:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0033_sales'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Sales',
            new_name='Sale',
        ),
    ]
