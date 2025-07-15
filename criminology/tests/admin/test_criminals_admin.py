"""
@file tests/admin/test_criminals_admin.py
@brief Tests for Django admin configuration of the 'criminals' app.

@details
Ensures that models are correctly registered with the Django admin,
and that the admin list views for each model render successfully
and display expected content.
"""

import pytest
from django.urls import reverse
from django.contrib.admin.sites import site
from criminals.models import (
    Criminal,
    CriminalOffenseLink,
    FederalOffense,
    VACodeOffense,
)

pytestmark = pytest.mark.django_db


def test_criminal_admin_registered():
    """
    @brief Criminal model is registered with admin site.
    """
    assert site.is_registered(Criminal)


def test_criminaloffenselink_admin_registered():
    """
    @brief CriminalOffenseLink model is registered with admin site.
    """
    assert site.is_registered(CriminalOffenseLink)


def test_federaloffense_admin_registered():
    """
    @brief FederalOffense model is registered with admin site.
    """
    assert site.is_registered(FederalOffense)


def test_vacodeoffense_admin_registered():
    """
    @brief VACodeOffense model is registered with admin site.
    """
    assert site.is_registered(VACodeOffense)


def test_criminal_admin_list_view(client, admin_user):
    """
    @brief Admin list view for Criminal loads successfully.
    """
    url = reverse("admin:criminals_criminal_changelist")
    client.force_login(admin_user)
    response = client.get(url)
    assert response.status_code == 200
    assert b"first name" in response.content.lower()
    assert b"last name" in response.content.lower()


def test_criminaloffenselink_admin_list_view(client, admin_user):
    """
    @brief Admin list view for CriminalOffenseLink loads successfully.
    """
    url = reverse("admin:criminals_criminaloffenselink_changelist")
    client.force_login(admin_user)
    response = client.get(url)
    assert response.status_code == 200
    assert b"criminal" in response.content.lower()
    assert b"convicted" in response.content.lower()


def test_federaloffense_admin_list_view(client, admin_user):
    """
    @brief Admin list view for FederalOffense loads successfully.
    """
    url = reverse("admin:criminals_federaloffense_changelist")
    client.force_login(admin_user)
    response = client.get(url)
    assert response.status_code == 200
    assert b"offense type" in response.content.lower()
    assert b"offense class" in response.content.lower()


def test_vacodeoffense_admin_list_view(client, admin_user):
    """
    @brief Admin list view for VACodeOffense loads successfully.
    """
    url = reverse("admin:criminals_vacodeoffense_changelist")
    client.force_login(admin_user)
    response = client.get(url)
    assert response.status_code == 200
    assert b"offense type" in response.content.lower()
    assert b"offense class" in response.content.lower()
