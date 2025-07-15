"""
@file criminals/admin.py
@brief Django admin configuration for the 'criminals' app.

@details
Registers models for the admin interface and provides custom display
and filtering options for Criminals, Offenses, and their relationships.
"""

from django.contrib import admin
from .models import Criminal, CriminalOffenseLink, FederalOffense, VACodeOffense


@admin.register(Criminal)
class CriminalAdmin(admin.ModelAdmin):
    """
    @brief Admin configuration for the Criminal model.

    @details
    Displays basic personal information fields and provides
    search capability by first and last name in the Django admin.
    """
    list_display = ("first_name", "last_name", "date_of_birth")
    search_fields = ("first_name", "last_name")


@admin.register(CriminalOffenseLink)
class CriminalOffenseLinkAdmin(admin.ModelAdmin):
    """
    @brief Admin configuration for linking criminals to offenses.

    @details
    Shows related criminal and offense information, charge date,
    and conviction status. Allows filtering by conviction status.
    """
    list_display = ("criminal", "federal_offense", "vacode_offense", "date_charged", "convicted")
    list_filter = ("convicted",)


@admin.register(FederalOffense)
class FederalOffenseAdmin(admin.ModelAdmin):
    """
    @brief Admin interface for managing FederalOffense entries.

    @details
    Displays federal offense type, class, and description. Enables
    filtering by offense type and class for easier navigation.
    """
    list_display = ("offense_type", "offense_class", "description")
    list_filter = ("offense_type", "offense_class")


@admin.register(VACodeOffense)
class VACodeOffenseAdmin(admin.ModelAdmin):
    """
    @brief Admin interface for managing VACodeOffense entries.

    @details
    Displays Virginia Code offense type, class, and description. Enables
    filtering by offense type and class for streamlined admin views.
    """
    list_display = ("offense_type", "offense_class", "description")
    list_filter = ("offense_type", "offense_class")
