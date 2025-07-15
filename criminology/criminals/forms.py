"""
@file criminals/forms.py
@brief Form classes for the criminals app.

@details
Defines Django forms for collecting and validating input related to
criminal records and their associated offenses. Includes model-bound
forms as well as custom forms with dynamic fields.
"""

from django import forms
from .models import Criminal, CriminalOffense


class CriminalForm(forms.ModelForm):
    """
    @brief Form for creating or updating a Criminal instance.

    @details
    Model-bound form for collecting basic criminal identity information,
    including first name and last name.
    """
    class Meta:
        model = Criminal
        fields = ["first_name", "last_name"]


class CriminalOffenseForm(forms.Form):
    """
    @brief Form to collect offense information related to a criminal.

    @details
    This is a standalone form (not model-bound) that gathers details about
    an offense to be linked to a criminal. Fields include the individual's
    name, the offense's description, jurisdiction (federal or Virginia),
    offense type, and offense class. The `offense_class` field is populated
    dynamically using JavaScript based on the selected jurisdiction.
    """
    OFFENSE_CHOICES = [
        ("federal", "Federal"),
        ("virginia", "Virginia"),
    ]

    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    description = forms.CharField(widget=forms.Textarea)
    offense_source = forms.ChoiceField(choices=OFFENSE_CHOICES)
    offense_type = forms.ChoiceField(choices=CriminalOffense.OFFENSE_TYPES)
    offense_class = forms.ChoiceField(choices=[])  # JS-populated dynamically

    class Meta:
        fields = [
            "first_name",
            "last_name",
            "offense_type",
            "offense_class",
            "description",
            "offense_source",
        ]
