# Generated by Django 5.1.7 on 2025-03-15 10:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_idcard'),
    ]

    operations = [
        migrations.AddField(
            model_name='idcard',
            name='first_time',
            field=models.BooleanField(default=True),
        ),
    ]
