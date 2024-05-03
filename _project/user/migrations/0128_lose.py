# Generated by Django 3.2.23 on 2024-04-06 05:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0127_auto_20240406_0702'),
    ]

    operations = [
        migrations.CreateModel(
            name='Lose',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lose_type', models.CharField(blank=True, max_length=100, null=True)),
                ('lose_money', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
            ],
        ),
    ]
