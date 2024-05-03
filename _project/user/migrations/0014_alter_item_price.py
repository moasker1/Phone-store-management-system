# Generated by Django 3.2.23 on 2024-01-05 17:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0013_remove_supplier_total'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
    ]