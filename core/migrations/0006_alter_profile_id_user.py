# Generated by Django 5.0.2 on 2024-04-17 20:57

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_alter_profile_id_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='id_user',
            field=models.IntegerField(default=core.models.default_id_user),
        ),
    ]
