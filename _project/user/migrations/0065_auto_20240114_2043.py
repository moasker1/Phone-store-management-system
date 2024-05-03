# Generated by Django 3.2.23 on 2024-01-14 18:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0064_containeritem_remaining_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='container',
            name='expense',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='container',
            name='expense_notes',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='container',
            name='expense_type',
            field=models.CharField(default='مصروف', max_length=30),
        ),
    ]