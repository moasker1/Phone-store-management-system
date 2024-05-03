# Generated by Django 3.2.23 on 2024-04-06 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0133_remove_payment_client'),
    ]

    operations = [
        migrations.CreateModel(
            name='Daycome',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(blank=True, null=True)),
                ('income', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('loses', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('net_profit', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
            ],
        ),
    ]
