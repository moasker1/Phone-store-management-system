# Generated by Django 3.2.23 on 2024-04-06 07:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0130_auto_20240406_0923'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sale',
            name='item',
        ),
    ]