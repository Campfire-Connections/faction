# Generated by Django 5.0.6 on 2024-09-21 01:00

import django.db.models.deletion
import django.views.generic.edit
import core.mixins.forms
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("faction", "0007_remove_attendee_slug_remove_leader_slug"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="CreateView",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("slug", models.SlugField(blank=True, max_length=255, unique=True)),
                ("seo_title", models.CharField(blank=True, max_length=70, null=True)),
                (
                    "seo_description",
                    models.CharField(blank=True, max_length=160, null=True),
                ),
                (
                    "seo_keywords",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=(
                core.mixins.forms.SuccessMessageMixin,
                core.mixins.forms.FormValidationMixin,
                models.Model,
                django.views.generic.edit.CreateView,
            ),
        ),
        migrations.CreateModel(
            name="DeleteView",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("is_deleted", models.BooleanField(default=False)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={
                "abstract": False,
            },
            bases=(
                models.Model,
                core.mixins.forms.SuccessMessageMixin,
                django.views.generic.edit.DeleteView,
            ),
        ),
        migrations.CreateModel(
            name="UpdateView",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "change_message",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=(
                models.Model,
                core.mixins.forms.SuccessMessageMixin,
                core.mixins.forms.FormValidationMixin,
                django.views.generic.edit.UpdateView,
            ),
        ),
        migrations.AddField(
            model_name="attendee",
            name="last_activity_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="last_activity_%(class)s_set",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="faction",
            name="last_activity_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="last_activity_%(class)s_set",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="leader",
            name="last_activity_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="last_activity_%(class)s_set",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="faction",
            name="name",
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
