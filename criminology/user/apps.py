"""
@file user/apps.py
@brief Django app configuration module for the 'user' app.

@details
Defines the app configuration class for Django to recognize the 'user' application.
Sets default auto primary key field type and registers the app name.
"""

from django.apps import AppConfig


class UserConfig(AppConfig):
    """
    @brief Django app configuration for the 'user' app.

    @details
    This configuration:
    - Specifies the default primary key type (`BigAutoField`),
    - Sets the app's importable Python path as 'user'.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "user"
