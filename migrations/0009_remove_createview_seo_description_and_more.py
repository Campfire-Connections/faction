# Generated by Django 5.0.6 on 2024-09-28 12:03

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("faction", "0008_createview_deleteview_updateview_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="createview",
            name="seo_description",
        ),
        migrations.RemoveField(
            model_name="createview",
            name="seo_keywords",
        ),
        migrations.RemoveField(
            model_name="createview",
            name="seo_title",
        ),
    ]
