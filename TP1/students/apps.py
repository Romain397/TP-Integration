"""Configuration for the student directory app."""

from django.apps import AppConfig


class StudentsConfig(AppConfig):
    """Configure student directory defaults."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "students"
