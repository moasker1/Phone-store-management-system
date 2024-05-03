# Generated by Django 3.2.23 on 2024-04-06 04:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0123_sale_paid'),
    ]

    operations = [
        migrations.CreateModel(
            name='Kind',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kind', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='user.kind')),
            ],
        ),
    ]