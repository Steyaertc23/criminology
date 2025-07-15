"""
@file tests/forms/test_criminals_forms.py
@brief Tests for CriminalForm and CriminalOffenseForm validation and behavior.

@details
Includes tests for valid data submission, missing required fields, 
and invalid choices on offense_source field.
"""

import pytest
from criminals.forms import CriminalForm, CriminalOffenseForm
from criminals.models import CriminalOffense

pytestmark = pytest.mark.django_db


def test_criminal_form_valid_data():
    """
    @brief Tests that CriminalForm is valid with correct data.
    """
    data = {
        "first_name": "John",
        "last_name": "Doe",
    }
    form = CriminalForm(data=data)
    assert form.is_valid()
    criminal = form.save()
    assert criminal.first_name == "John"
    assert criminal.last_name == "Doe"


def test_criminal_form_missing_fields():
    """
    @brief CriminalForm should be invalid if required fields are missing.
    """
    form = CriminalForm(data={})
    assert not form.is_valid()
    assert "first_name" in form.errors
    assert "last_name" in form.errors


def test_criminal_offense_form_valid_data():
    """
    @brief Tests that CriminalOffenseForm validates with complete valid input.
    """
    data = {
        "first_name": "Jane",
        "last_name": "Smith",
        "description": "Test offense description",
        "offense_source": "federal",
        "offense_type": CriminalOffense.FELONY,
        "offense_class": "A",
    }
    form = CriminalOffenseForm(data=data)
    assert form.is_valid()


def test_criminal_offense_form_invalid_offense_source():
    """
    @brief CriminalOffenseForm invalid if offense_source is not in choices.
    """
    data = {
        "first_name": "Jane",
        "last_name": "Smith",
        "description": "Test offense description",
        "offense_source": "invalid_source",
        "offense_type": CriminalOffense.FELONY,
        "offense_class": "A",
    }
    form = CriminalOffenseForm(data=data)
    assert not form.is_valid()
    assert "offense_source" in form.errors


def test_criminal_offense_form_missing_required_fields():
    """
    @brief CriminalOffenseForm should be invalid if required fields are missing.
    """
    form = CriminalOffenseForm(data={})
    assert not form.is_valid()
    assert "first_name" in form.errors
    assert "last_name" in form.errors
    assert "description" in form.errors
    assert "offense_source" in form.errors
    assert "offense_type" in form.errors
    assert "offense_class" in form.errors
