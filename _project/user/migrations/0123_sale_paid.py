# Generated by Django 3.2 on 2024-03-08 14:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0122_sale_remain'),
    ]

    operations = [
        migrations.AddField(
            model_name='sale',
            name='paid',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]