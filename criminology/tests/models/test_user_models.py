"""
@file tests/models/test_user_models.py
@brief Unit tests for custom user model behaviors and security features.

@details
Includes tests for superuser creation constraints, user expiration logic,
security answer hashing and verification, and default field values.
Also tests expiration with mocked current time to ensure date-dependent logic.
"""

import pytest
from django.utils import timezone
from datetime import timedelta, datetime

pytestmark = pytest.mark.django_db


def test_create_superuser_defaults(superuser):
    """
    @brief Test default properties of a created superuser.

    @details Verifies that a superuser is created with is_staff=True and is_superuser=True
             and the correct username and password.
    """
    assert superuser.is_staff is True
    assert superuser.is_superuser is True
    assert superuser.username == "admin"
    assert superuser.check_password("securepass")


def test_create_superuser_invalid_is_staff(user_model):
    """
    @brief Ensure error is raised when is_staff=False for a superuser.

    @details Django should raise a ValueError if is_staff is not True for a superuser.
    """
    with pytest.raises(ValueError, match="Superuser must have is_staff=True."):
        user_model.objects.create_superuser(
            username="admin2",
            email="admin2@example.com",
            password="securepass",
            is_staff=False,
        )


def test_create_superuser_invalid_is_superuser(user_model):
    """
    @brief Ensure error is raised when is_superuser=False for a superuser.

    @details Django should raise a ValueError if is_superuser is not True for a superuser.
    """
    with pytest.raises(ValueError, match="Superuser must have is_superuser=True."):
        user_model.objects.create_superuser(
            username="admin3",
            email="admin3@example.com",
            password="securepass",
            is_superuser=False,
        )


def test_is_expired_true(user):
    """
    @brief User should be expired when expiration_date is in the past.
    """
    user.expiration_date = timezone.now().date() - timedelta(days=1)
    user.save()
    assert user.is_expired() is True


def test_is_expired_false(user):
    """
    @brief User should not be expired when expiration_date is in the future.
    """
    user.expiration_date = timezone.now().date() + timedelta(days=1)
    user.save()
    assert user.is_expired() is False


def test_is_expired_none(user):
    """
    @brief User with no expiration_date should not be considered expired.
    """
    user.expiration_date = None
    user.save()
    assert user.is_expired() is False


def test_set_and_check_security_answer(user):
    """
    @brief Test hashing and verifying a user's security answer.

    @details Ensures the security answer is hashed and can be validated correctly.
    """
    raw_answer = "my first pet"
    user.set_security_answer(raw_answer)
    user.save()

    assert user.security_answer != raw_answer
    assert user.check_security_answer("my first pet") is True
    assert user.check_security_answer("wrong answer") is False


def test_first_login_default(user):
    """
    @brief New users should default to first_login=True.
    """
    assert user.first_login is True, "first_login should default to True"


def test_is_expired_mocked_now(mocker, user_factory):
    """
    @brief Test expiration logic with mocked current date.

    @details Verifies expiration logic using a fixed datetime.
    """
    fixed_now = datetime(2025, 1, 1, tzinfo=timezone.utc)
    mocker.patch("django.utils.timezone.now", return_value=fixed_now)

    user_past = user_factory(expiration_date=fixed_now.date() - timedelta(days=1))
    assert user_past.is_expired() is True

    user_today = user_factory(expiration_date=fixed_now.date())
    assert user_today.is_expired() is False

    user_future = user_factory(expiration_date=fixed_now.date() + timedelta(days=1))
    assert user_future.is_expired() is False
