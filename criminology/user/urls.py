"""
@file user/urls.py
@brief URL routing for user-related views.
@details
Maps user authentication and account management views to their corresponding routes.
Includes paths for:
- First login password reset
- Security question setup
- Multi-step account recovery
- Admin user creation
"""

from django.urls import path
from . import views

urlpatterns = [
    path(
        "check-login/",
        views.check_first_login,
        name="check_first_login",
    ),  # @brief Redirect users on first login to force password reset

    path(
        "force-reset/",
        views.force_password_reset,
        name="force_password_reset",
    ),  # @brief Force password reset without requiring old password

    path(
        "setup-security-question/",
        views.setup_security_question,
        name="setup_security_question",
    ),  # @brief Setup security question and answer for account recovery

    path(
        "recover-account/",
        views.account_recovery_step1,
        name="account_recovery_step1",
    ),  # @brief Account recovery step 1: verify username and email

    path(
        "recover-account/step-2/",
        views.account_recovery_step2,
        name="account_recovery_step2",
    ),  # @brief Account recovery step 2: validate security question answer

    path(
        "recover-account/step-3/",
        views.account_recovery_step3,
        name="account_recovery_step3",
    ),  # @brief Account recovery step 3: reset password

    path(
        "create/",
        views.create_user,
        name="new_user",
    ),  # @brief Admin view to create a new user
]
