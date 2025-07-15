"""
@file criminals/apps.py
@brief Application configuration for the criminals app.

@details
This file defines app-level settings and metadata used by Django to
initialize and manage the "criminals" app, including the default
auto field type and the app's registered name.
"""

from django.apps import AppConfig


class CriminalsConfig(AppConfig):
    """
    @brief Configuration class for the 'criminals' app.

    @details
    Informs Django about app-level configurations including the
    default primary key field type and the registered app name.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'criminals'
