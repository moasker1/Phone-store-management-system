# Generated by Django 3.2.23 on 2024-01-06 13:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0023_auto_20240106_1524'),
    ]

    operations = [
        migrations.AddField(
            model_name='supplier',
            name='type',
            field=models.CharField(default='عمولة', max_length=30),
        ),
    ]