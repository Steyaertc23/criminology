"""
@file user/models.py
@brief Custom user model and manager.

@details
Defines a `CustomUser` model extending Django's `AbstractUser`, adding:
- first login flag,
- security question and hashed answer,
- expiration date for automatic deactivation/deletion.

Also includes a custom user manager that enforces proper superuser creation.
"""

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password


class CustomUserManager(UserManager):
    """
    @brief Manager for CustomUser model.

    @details
    Overrides `create_superuser` to enforce is_staff and is_superuser flags.
    """

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        """
        @brief Creates and saves a superuser with the given username, email, and password.

        @details
        Enforces that is_staff and is_superuser are set to True,
        otherwise raises a ValueError.

        @param username: str - The username for the superuser.
        @param email: str | None - The optional email for the superuser.
        @param password: str - The password for the superuser.
        @param extra_fields: dict - Additional fields for customization.

        @raises ValueError: If is_staff or is_superuser are not True.

        @return CustomUser: The created superuser instance.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have is_superuser=True.")

        return super().create_superuser(username, email, password, **extra_fields)


class CustomUser(AbstractUser):
    """
    @brief Custom user model extending Django's built-in AbstractUser.

    @details
    Adds additional fields for account control and security:
    - first_login: Tracks whether user must change password on first login.
    - security_question / security_answer: For account recovery.
    - expiration_date: Used to mark account as expired after a certain date.
    """

    first_login = models.BooleanField(default=True)
    security_question = models.CharField(max_length=255, blank=True, null=True)
    security_answer = models.CharField(max_length=255, blank=True, null=True)
    expiration_date = models.DateField(blank=True, null=True)

    objects = CustomUserManager()

    def is_expired(self):
        """
        @brief Returns whether the user account is expired.

        @return bool: True if `expiration_date` is set and in the past; False otherwise.
        """
        return self.expiration_date and timezone.now().date() > self.expiration_date

    def set_security_answer(self, raw_answer):
        """
        @brief Hashes and sets the user's security answer.

        @param raw_answer: str - The plain-text security answer to hash.
        """
        self.security_answer = make_password(raw_answer)

    def check_security_answer(self, raw_answer):
        """
        @brief Verifies a raw answer against the hashed stored answer.

        @param raw_answer: str - The input answer to validate.
        @return bool: True if the answer is correct; False otherwise.
        """
        return check_password(raw_answer, self.security_answer)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
