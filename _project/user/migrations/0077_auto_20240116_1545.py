# Generated by Django 3.2.23 on 2024-01-16 13:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0076_auto_20240116_0246'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sale',
            name='container_item',
        ),
        migrations.AddField(
            model_name='sale',
            name='container_item',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='user.containeritem'),
        ),
    ]