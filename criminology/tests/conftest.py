"""
@file tests/conftest.py
@brief Pytest fixtures for user and superuser setup, including authenticated clients.

@details
Provides reusable fixtures for:
- Creating regular users and superusers using factory patterns.
- Returning user factories for flexible user creation.
- Authenticated client instances logged in as regular users or superusers,
  facilitating tests requiring user authentication and admin privileges.
"""

import pytest
from tests.factories import SuperUserFactory, UserFactory

@pytest.fixture
def user(db):
    """
    @brief Regular user fixture using UserFactory.
    """
    return UserFactory.create()

@pytest.fixture
def user_factory(db):
    """
    @brief UserFactory fixture for creating users with custom attributes.
    """
    return UserFactory

@pytest.fixture
def superuser(db):
    """
    @brief Superuser fixture using SuperUserFactory.
    """
    return SuperUserFactory.create()

@pytest.fixture
def admin_user(superuser):
    """
    @brief Alias for superuser to use in admin tests.
    """
    return superuser

@pytest.fixture
def logged_in_client(client, user):
    """
    @brief Logs in a regular user and returns the authenticated client.
    """
    client.login(username=user.username, password="password123")
    return client

@pytest.fixture
def logged_in_admin_client(client, superuser):
    """
    @brief Logs in a superuser and returns the authenticated client.
    """
    client.login(username=superuser.username, password="adminpass")
    return client
