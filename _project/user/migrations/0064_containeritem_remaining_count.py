# Generated by Django 3.2.23 on 2024-01-14 18:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0063_remove_containeritem_remaining_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='containeritem',
            name='remaining_count',
            field=models.PositiveIntegerField(editable=False, null=True),
        ),
    ]