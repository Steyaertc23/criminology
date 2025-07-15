"""
@file users/forms.py
@brief Custom Django forms for user creation, updates, password reset, and security question setup.

@details
Includes:
- Custom user creation and change forms with additional fields.
- Security question form for account recovery setup.
- Password reset form that bypasses old password requirement.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import password_validation
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    """
    @brief Form for creating a new user with additional fields.

    @details
    Extends Django's UserCreationForm to include:
    - email,
    - first name,
    - last name,
    - expiration date.
    """

    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=False, max_length=30)
    last_name = forms.CharField(required=False, max_length=30)
    expiration_date = forms.DateField(
        required=False, help_text="Optional: auto-delete user after this date."
    )

    class Meta:
        model = CustomUser
        fields = [
            "email",
            "first_name",
            "last_name",
            "expiration_date",
        ]

    def save(self, commit=True):
        """
        @brief Saves the new user instance with provided fields.

        @param commit: bool - Whether to save the user to the database.
        @return CustomUser: The created user instance.
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.username = user.email.split("@")[0]
        user.first_name = self.cleaned_data.get("first_name", "")
        user.last_name = self.cleaned_data.get("last_name", "")
        user.expiration_date = self.cleaned_data.get("expiration_date")
        if commit:
            user.save()
        return user


class CustomStaffUserCreationForm(UserCreationForm):
    """
    @brief Form for creating a new staff user.

    @details
    Extends Django's UserCreationForm to include:
    - email,
    - first name,
    - last name,
    - expiration date.
    """

    username = forms.CharField(required=False, max_length=10)
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=False, max_length=30)
    last_name = forms.CharField(required=False, max_length=30)

    class Meta:
        model = CustomUser
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
        ]

    def save(self, commit=True):
        """
        @brief Saves the new staff user instance with provided fields.

        @param commit: bool - Whether to save the user to the database.
        @return CustomUser: The created user instance.
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.username = (
            self.cleaned_data["username"]
            if self.cleaned_data["username"]
            else user.email.split("@")[0]
        )
        user.first_name = self.cleaned_data.get("first_name", "")
        user.last_name = self.cleaned_data.get("last_name", "")
        user.is_staff = True
        if commit:
            user.save()
        return user


class CustomUserChangeForm(UserChangeForm):
    """
    @brief Form for updating an existing user.

    @details
    Extends Django's UserChangeForm to allow changes to:
    - basic fields,
    - security question,
    - expiration date,
    - permissions.
    """

    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=False, max_length=30)
    last_name = forms.CharField(required=False, max_length=30)
    security_question = forms.CharField(required=False, max_length=255)
    expiration_date = forms.DateField(
        required=False, help_text="Optional: auto-delete user after this date."
    )

    class Meta:
        model = CustomUser
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "security_question",
            "expiration_date",
            "is_active",
            "is_staff",
            "is_superuser",
            "groups",
            "user_permissions",
        ]

    def save(self, commit=True):
        """
        @brief Saves the updated user instance with provided fields.

        @param commit: bool - Whether to save the user to the database.
        @return CustomUser: The updated user instance.
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data.get("first_name", "")
        user.last_name = self.cleaned_data.get("last_name", "")
        user.security_question = self.cleaned_data.get("security_question", "")
        user.expiration_date = self.cleaned_data.get("expiration_date")
        if commit:
            user.save()
        return user


class SecurityQuestionForm(forms.ModelForm):
    """
    @brief Form for setting or updating user's security question and hashed answer.

    @details
    Collects a security question and securely stores a hashed version of the answer.
    """

    security_answer = forms.CharField(
        widget=forms.PasswordInput,
        max_length=255,
        help_text="Answer will be stored securely.",
    )

    class Meta:
        model = CustomUser
        fields = ["security_question", "security_answer"]

    def save(self, commit=True):
        """
        @brief Hashes the security answer before saving.

        @param commit: bool - Whether to save the user to the database.
        @return CustomUser: The updated user instance with hashed answer.
        """
        user = super().save(commit=False)
        user.set_security_answer(self.cleaned_data["security_answer"])
        if commit:
            user.save()
        return user


class PasswordResetNoOldForm(forms.ModelForm):
    """
    @brief Form to reset password without requiring the old password.

    @details
    Presents two fields for password entry and validates them
    using Django’s built-in password validators.
    """

    new_password1 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput,
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label="Confirm new password",
        widget=forms.PasswordInput,
        strip=False,
    )

    class Meta:
        model = CustomUser
        fields = []

    def clean_new_password2(self):
        """
        @brief Validates that the two new passwords match and comply with password policies.

        @raises ValidationError: If passwords do not match or fail validation.
        @return str: The validated password.
        """
        password1 = self.cleaned_data.get("new_password1")
        password2 = self.cleaned_data.get("new_password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("The two password fields didn’t match.")
        password_validation.validate_password(password2, self.instance)
        return password2

    def save(self, commit=True):
        """
        @brief Sets the new password and saves the user instance.

        @param commit: bool - Whether to save the user to the database.
        @return CustomUser: The user instance with updated password.
        """
        password = self.cleaned_data["new_password1"]
        user = self.instance
        user.set_password(password)
        if commit:
            user.save()
        return user
