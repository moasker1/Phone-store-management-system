# Generated by Django 3.2.23 on 2024-01-07 18:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0030_container_con_weight'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='container',
            name='con_weight',
        ),
    ]