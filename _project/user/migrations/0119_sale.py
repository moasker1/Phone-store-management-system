# Generated by Django 3.2.23 on 2024-03-04 21:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0118_auto_20240304_2343'),
    ]

    operations = [
        migrations.CreateModel(
            name='sale',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='user.client')),
            ],
        ),
    ]
