"""
@file tests/admin/test_user_admin.py
@brief Tests for CustomUser admin views and CRUD operations.

@details
Verifies superuser access to user list, add, and change views in admin.
Includes tests for creating and updating users through the admin interface.
"""

import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_admin_user_changelist_access(client, superuser):
    """
    @brief Tests that the superuser can access the CustomUser changelist in admin.
    @details
    Logs in as a superuser and requests the admin page listing all users.
    Verifies the page loads successfully with status code 200.
    """
    client.force_login(superuser)
    url = reverse("admin:user_customuser_changelist")
    response = client.get(url)
    assert response.status_code == 200
    assert b"Select user to change" in response.content


def test_admin_user_add_view_access(client, superuser):
    """
    @brief Tests that the superuser can access the add new CustomUser form in admin.
    @details
    Logs in as a superuser and requests the admin page for creating a new user.
    Verifies the page loads with status code 200 and the form is present.
    """
    client.force_login(superuser)
    url = reverse("admin:user_customuser_add")
    response = client.get(url)
    assert response.status_code == 200
    assert b"Add user" in response.content or b"Add custom user" in response.content


def test_admin_user_change_view_access(client, superuser, user):
    """
    @brief Tests that the superuser can access the change form for an existing user.
    @details
    Uses the 'user' fixture, logs in as a superuser, and requests the admin page to edit that user.
    Verifies the page loads successfully and contains the username in the form.
    """
    client.force_login(superuser)
    url = reverse("admin:user_customuser_change", args=[user.pk])
    response = client.get(url)
    assert response.status_code == 200
    assert user.username.encode() in response.content


def test_admin_user_add_post(client, superuser):
    """
    @brief Tests creating a new user through the admin add user form.
    @details
    Logs in as superuser, posts valid user data to the admin add user URL.
    Checks for a redirect on success and that the user was created.
    """
    client.force_login(superuser)
    url = reverse("admin:user_customuser_add")
    data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "first_name": "New",
        "last_name": "User",
        "password1": "StrongPass123!",
        "password2": "StrongPass123!",
        "expiration_date": "",
        "first_login": True,
        "is_active": True,
        "is_staff": False,
    }
    response = client.post(url, data)
    # Successful add redirects to changelist
    assert response.status_code == 302

    from django.contrib.auth import get_user_model
    User = get_user_model()
    assert User.objects.filter(username="newuser").exists()


def test_admin_user_change_post(client, superuser, user):
    """
    @brief Tests updating an existing user via the admin change form.
    @details
    Uses the 'user' fixture, logs in as superuser, posts updated data to the change URL.
    Checks for a redirect and verifies the updated field is saved.
    """
    client.force_login(superuser)
    url = reverse("admin:user_customuser_change", args=[user.pk])
    data = {
        "username": user.username,
        "email": "newemail@example.com",
        "first_name": "",
        "last_name": "",
        "security_question": "",
        "expiration_date": "",
        "is_active": True,
        "is_staff": False,
        "is_superuser": False,
        "groups": [],
        "user_permissions": [],
    }
    response = client.post(url, data)
    assert response.status_code == 302
    user.refresh_from_db()
    assert user.email == "newemail@example.com"
