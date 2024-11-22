# Generated by Django 5.0.6 on 2024-08-18 16:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("faction", "0005_attendeeprofile_address_leaderprofile_address"),
        ("organization", "0002_alter_organization_description_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="attendeeprofile",
            name="organization",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="organization.organization",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="leaderprofile",
            name="organization",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="organization.organization",
            ),
            preserve_default=False,
        ),
    ]
