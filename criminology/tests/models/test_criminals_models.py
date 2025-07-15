"""
@file tests/models/test_criminals_models.py
@brief Unit tests for Criminal, FederalOffense, VACodeOffense, and CriminalOffenseLink models.

@details
Tests string representations, source properties, and field behaviors
for all relevant models in the criminals app.
Includes validation of correct linking and field saving.
"""

import pytest
from datetime import date
from criminals.models import (
    Criminal,
    FederalOffense,
    VACodeOffense,
    CriminalOffenseLink,
)

pytestmark = pytest.mark.django_db


def test_criminal_str():
    """
    @brief String representation of Criminal model.
    @details
    Ensures the __str__ method returns the concatenation of first_name and last_name.
    """
    c = Criminal.objects.create(first_name="John", last_name="Doe")
    assert str(c) == "John Doe"


def test_federal_offense_str_and_source():
    """
    @brief FederalOffense string representation and source property.
    @details
    Validates __str__ returns class display and description.
    Checks the source property returns 'federal'.
    """
    f_offense = FederalOffense.objects.create(
        offense_type=FederalOffense.FELONY,
        description="Bank robbery",
        offense_class="A",
    )
    assert str(f_offense) == "Class A - Bank robbery"
    assert f_offense.source == "federal"


def test_vacode_offense_str_and_source():
    """
    @brief VACodeOffense string representation and source property.
    @details
    Validates __str__ returns class display and description.
    Checks the source property returns 'virginia'.
    """
    va_offense = VACodeOffense.objects.create(
        offense_type=VACodeOffense.MISDEMEANOR,
        description="Petty theft",
        offense_class="2",
    )
    assert str(va_offense) == "Class 2 - Petty theft"
    assert va_offense.source == "virginia"


def test_criminal_offense_link_str_with_federal_and_vacode():
    """
    @brief CriminalOffenseLink string representation.
    @details
    Tests __str__ method returns the correct string when linked with:
      - federal offense only,
      - vacode offense only,
      - neither offense.
    """
    criminal = Criminal.objects.create(first_name="Jane", last_name="Smith")
    federal = FederalOffense.objects.create(
        offense_type=FederalOffense.FELONY,
        description="Fraud",
        offense_class="B",
    )
    vacode = VACodeOffense.objects.create(
        offense_type=VACodeOffense.INFRACTION,
        description="Littering",
        offense_class="NA",
    )

    # Link with federal offense only
    link1 = CriminalOffenseLink.objects.create(
        criminal=criminal, federal_offense=federal
    )
    assert str(link1) == "Jane Smith - Class B - Fraud"

    # Link with vacode offense only
    link2 = CriminalOffenseLink.objects.create(criminal=criminal, vacode_offense=vacode)
    assert str(link2) == "Jane Smith - Class NA - Littering"

    # Link with neither offense
    link3 = CriminalOffenseLink.objects.create(criminal=criminal)
    assert str(link3) == "Jane Smith - No offense"


def test_criminal_offense_link_fields():
    """
    @brief CriminalOffenseLink model fields test.
    @details
    Verifies that optional fields date_charged and convicted are saved and retrieved correctly.
    """
    criminal = Criminal.objects.create(first_name="Jake", last_name="Long")
    federal = FederalOffense.objects.create(
        offense_type=FederalOffense.MISDEMEANOR,
        description="Public intoxication",
        offense_class="C",
    )
    link = CriminalOffenseLink.objects.create(
        criminal=criminal,
        federal_offense=federal,
        date_charged=date(2023, 1, 15),
        convicted=True,
    )
    assert link.date_charged == date(2023, 1, 15)
    assert link.convicted is True
