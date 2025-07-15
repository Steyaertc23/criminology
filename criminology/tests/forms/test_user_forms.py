"""
@file tests/forms/test_user_forms.py
@brief Tests for custom user-related forms including creation, update, security question, and password reset.

@details
Covers validation of required fields, matching passwords, hashing of security answers,
and successful save operations with correct data.
"""

import pytest
from django.utils import timezone
from datetime import timedelta
from user.forms import (
    CustomUserCreationForm,
    CustomUserChangeForm,
    SecurityQuestionForm,
    PasswordResetNoOldForm,
)

pytestmark = pytest.mark.django_db


def test_custom_user_creation_form_valid_data():
    """
    @brief Form with valid data saves user correctly.
    """
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "password1": "StrongPass123!",
        "password2": "StrongPass123!",
        "expiration_date": (timezone.now() + timedelta(days=10)).date(),
    }
    form = CustomUserCreationForm(data=data)
    assert form.is_valid(), form.errors
    user = form.save()
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.first_name == "Test"
    assert user.last_name == "User"
    assert user.expiration_date == data["expiration_date"]
    assert user.check_password("StrongPass123!")


def test_custom_user_creation_form_password_mismatch():
    """
    @brief Password1 and password2 must match.
    """
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password1": "StrongPass123!",
        "password2": "MismatchPass!",
    }
    form = CustomUserCreationForm(data=data)
    assert not form.is_valid()
    assert "password2" in form.errors


def test_custom_user_creation_form_email_required():
    """
    @brief Email field is required.
    """
    data = {
        "username": "testuser",
        "password1": "StrongPass123!",
        "password2": "StrongPass123!",
    }
    form = CustomUserCreationForm(data=data)
    assert not form.is_valid()
    assert "email" in form.errors


def test_custom_user_change_form_valid(user):
    """
    @brief Form updates user fields correctly.
    """
    data = {
        "username": user.username,
        "email": "updated@example.com",
        "first_name": "Updated",
        "last_name": "User",
        "security_question": "Favorite food?",
        "expiration_date": (timezone.now() + timedelta(days=5)).date(),
        "is_active": True,
        "is_staff": False,
        "is_superuser": False,
        "groups": user.groups.all(),
        "user_permissions": user.user_permissions.all(),
    }
    form = CustomUserChangeForm(data=data, instance=user)
    assert form.is_valid(), form.errors
    updated_user = form.save()
    assert updated_user.email == "updated@example.com"
    assert updated_user.first_name == "Updated"
    assert updated_user.security_question == "Favorite food?"
    assert updated_user.expiration_date == data["expiration_date"]


def test_custom_user_change_form_email_required(user):
    """
    @brief Email is required on change form.
    """
    data = {
        "username": user.username,
        "email": "",
    }
    form = CustomUserChangeForm(data=data, instance=user)
    assert not form.is_valid()
    assert "email" in form.errors


def test_security_question_form_valid(user):
    """
    @brief Saving hashes security answer correctly.
    """
    data = {
        "security_question": "What is your pet's name?",
        "security_answer": "fluffy",
    }
    form = SecurityQuestionForm(data=data, instance=user)
    assert form.is_valid(), form.errors
    saved_user = form.save()
    assert saved_user.security_question == data["security_question"]
    assert saved_user.security_answer != "fluffy"
    assert saved_user.check_security_answer("fluffy")


def test_security_question_form_requires_fields(user):
    """
    @brief Both question and answer are required.
    """
    # no data
    form = SecurityQuestionForm(data={}, instance=user)
    assert not form.is_valid()
    assert "security_question" in form.errors
    assert "security_answer" in form.errors

    # missing security_answer
    form = SecurityQuestionForm(
        data={"security_question": "Favorite color?"}, instance=user
    )
    assert not form.is_valid()
    assert "security_answer" in form.errors

    # missing security_question
    form = SecurityQuestionForm(data={"security_answer": "blue"}, instance=user)
    assert not form.is_valid()
    assert "security_question" in form.errors


def test_password_reset_no_old_form_valid(user):
    """
    @brief Valid matching passwords pass validation and update password.
    """
    data = {
        "new_password1": "NewStrongPass1!",
        "new_password2": "NewStrongPass1!",
    }
    form = PasswordResetNoOldForm(data=data, instance=user)
    assert form.is_valid(), form.errors
    user = form.save()
    assert user.check_password("NewStrongPass1!")


def test_password_reset_no_old_form_passwords_do_not_match(user):
    """
    @brief Validation error if new passwords do not match.
    """
    data = {
        "new_password1": "NewStrongPass1!",
        "new_password2": "MismatchPass!",
    }
    form = PasswordResetNoOldForm(data=data, instance=user)
    assert not form.is_valid()
    assert "new_password2" in form.errors
    assert "didn't match" in str(form.errors["new_password2"])


def test_password_reset_no_old_form_password_validation_failure(user):
    """
    @brief Weak passwords raise validation error.
    """
    data = {
        "new_password1": "123",
        "new_password2": "123",
    }
    form = PasswordResetNoOldForm(data=data, instance=user)
    is_valid = form.is_valid()
    assert not is_valid
    assert "new_password2" in form.errors
