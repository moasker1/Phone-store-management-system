# Generated by Django 3.2.23 on 2024-01-27 01:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0099_remove_sale_mortgage'),
    ]

    operations = [
        migrations.AddField(
            model_name='sale',
            name='dept',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=15),
        ),
    ]