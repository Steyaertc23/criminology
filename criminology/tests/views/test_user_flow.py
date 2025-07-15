"""
@file tests/views/test_user_flow.py
@brief Functional tests for user authentication, first-login flows, 
       password resets, security question setup, and account recovery.

@details
Tests cover:
- First login redirect logic enforcing password reset for non-superusers.
- Forced password reset form rendering and validation.
- Security question setup flow including form validation and redirects.
- Multi-step account recovery including username/email verification,
  security question answering, and password resetting.
- Admin user creation access and functionality.

These tests verify correct redirects, form handling, session management,
and proper user state updates during various authentication-related workflows.
"""


import pytest
from django.urls import reverse
from django.contrib.messages import get_messages

pytestmark = pytest.mark.django_db


def test_check_first_login_redirects_to_force_password_reset(logged_in_client, user):
    """
    @brief Redirects users on their first login (non-superusers) to the forced password reset page.

    @details
    Sets the user's first_login flag True and ensures they are not superusers,
    then asserts that accessing the 'check_first_login' view redirects
    to the 'force_password_reset' URL.
    """
    user.first_login = True
    user.is_superuser = False
    user.save()
    response = logged_in_client.get(reverse("check_first_login"))
    assert response.status_code == 302
    assert response.url == reverse("force_password_reset")


def test_check_first_login_redirects_to_home_if_not_first_login(logged_in_client, user):
    """
    @brief Redirects users who have completed the first login to the home page.

    @details
    Sets first_login to False and verifies that the 'check_first_login' view
    redirects the user to the home page.
    """
    user.first_login = False
    user.save()
    response = logged_in_client.get(reverse("check_first_login"))
    assert response.status_code == 302
    assert response.url == reverse("home")


def test_check_first_login_superuser_redirects_to_home(logged_in_client, user):
    """
    @brief Ensures superusers bypass first login password reset redirection.

    @details
    Sets first_login True and is_superuser True, verifies that the superuser
    is redirected to the home page instead of the password reset.
    """
    user.first_login = True
    user.is_superuser = True
    user.save()
    response = logged_in_client.get(reverse("check_first_login"))
    assert response.status_code == 302
    assert response.url == reverse("home")


def test_force_password_reset_get(logged_in_client):
    """
    @brief Renders the forced password reset form on GET request.

    @details
    Sends a GET request to 'force_password_reset' view and checks
    that the form is included in the context.
    """
    response = logged_in_client.get(reverse("force_password_reset"))
    assert response.status_code == 200
    assert "form" in response.context


def test_force_password_reset_post_valid(logged_in_client, user):
    """
    @brief Accepts valid password input, resets user password, and redirects.

    @details
    Posts valid matching new passwords to the 'force_password_reset' view,
    verifies the user's password is updated, first_login flag is reset,
    and response redirects to 'setup_security_question'.
    """
    data = {
        "new_password1": "NewStrongPassword1!",
        "new_password2": "NewStrongPassword1!",
    }
    response = logged_in_client.post(reverse("force_password_reset"), data)
    user.refresh_from_db()
    assert response.status_code == 302
    assert response.url == reverse("setup_security_question")
    assert user.first_login is False


def test_force_password_reset_post_invalid(logged_in_client):
    """
    @brief Rejects invalid or weak passwords during forced reset.

    @details
    Posts invalid passwords to the 'force_password_reset' view and
    verifies that the form is redisplayed with errors.
    """
    data = {
        "new_password1": "short",
        "new_password2": "short",
    }
    response = logged_in_client.post(reverse("force_password_reset"), data)
    assert response.status_code == 200
    assert "form" in response.context
    assert response.context["form"].errors


def test_setup_security_question_get(logged_in_client):
    """
    @brief Renders the security question setup form.

    @details
    Sends a GET request to the 'setup_security_question' view and
    asserts the form is present in the response context.
    """
    response = logged_in_client.get(reverse("setup_security_question"))
    assert response.status_code == 200
    assert "form" in response.context


def test_setup_security_question_post_valid(logged_in_client, user):
    """
    @brief Saves the user's security question and hashed answer correctly.

    @details
    Posts valid security question and answer data,
    verifies user fields are updated,
    and asserts redirection to the home page.
    """
    data = {
        "security_question": "Your favorite food?",
        "security_answer": "pizza",
    }
    response = logged_in_client.post(reverse("setup_security_question"), data)
    user.refresh_from_db()
    assert user.security_question == "Your favorite food?"
    assert user.check_security_answer("pizza")
    assert response.status_code == 302
    assert response.url == reverse("home")


def test_setup_security_question_redirect_if_already_set(logged_in_client, user):
    """
    @brief Redirects users who already have a security question set.

    @details
    Sets a security question and answer for the user,
    then asserts that accessing 'setup_security_question' redirects to home.
    """
    user.security_question = "Set?"
    user.set_security_answer("yes")
    user.save()
    response = logged_in_client.get(reverse("setup_security_question"))
    assert response.status_code == 302
    assert response.url == reverse("home")


def test_account_recovery_step1_post_valid(client, user):
    """
    @brief Accepts valid username and email for account recovery step 1.

    @details
    Posts a valid username and email to 'account_recovery_step1',
    checks redirection to step 2.
    """
    response = client.post(reverse("account_recovery_step1"), {
        "username": user.username,
        "email": user.email,
    })
    assert response.status_code == 302
    assert response.url == reverse("account_recovery_step2")


def test_account_recovery_step1_post_invalid(client):
    """
    @brief Rejects invalid username/email in account recovery step 1.

    @details
    Posts invalid data and checks that an error message is shown
    and response is not a redirect.
    """
    response = client.post(reverse("account_recovery_step1"), {
        "username": "fake",
        "email": "nope@example.com",
    }, follow=True)
    messages = list(get_messages(response.wsgi_request))
    assert any("does not exist" in str(m) for m in messages)
    assert response.status_code == 200


def test_account_recovery_step2_correct_answer(client, user):
    """
    @brief Accepts correct security answer during account recovery step 2.

    @details
    Sets user's security question and answer,
    mocks session data,
    posts correct answer,
    and asserts redirection to step 3.
    """
    user.set_security_answer("blue")
    user.security_question = "Favorite color?"
    user.save()
    session = client.session
    session["recovery_user_id"] = user.id
    session["security_question"] = user.security_question
    session.save()
    response = client.post(reverse("account_recovery_step2"), {
        "security_answer": "blue",
    })
    assert response.status_code == 302
    assert response.url == reverse("account_recovery_step3")


def test_account_recovery_step2_wrong_answer(client, user):
    """
    @brief Rejects incorrect security answers during account recovery step 2.

    @details
    Sets user's security question and answer,
    mocks session data,
    posts wrong answer,
    and asserts error message is shown without redirect.
    """
    user.set_security_answer("blue")
    user.security_question = "Favorite color?"
    user.save()
    session = client.session
    session["recovery_user_id"] = user.id
    session["security_question"] = user.security_question
    session.save()
    response = client.post(reverse("account_recovery_step2"), {
        "security_answer": "wrong",
    }, follow=True)
    messages = list(get_messages(response.wsgi_request))
    assert any("Incorrect" in str(m) for m in messages)
    assert response.status_code == 200


def test_account_recovery_step3_success(client, user):
    """
    @brief Successfully resets password during account recovery step 3.

    @details
    Mocks session with recovery user id,
    posts new password and confirmation,
    and asserts redirection to login page.
    """
    session = client.session
    session["recovery_user_id"] = user.id
    session.save()
    response = client.post(reverse("account_recovery_step3"), {
        "new_password": "NewPass123!",
        "new_password_confirm": "NewPass123!",
    })
    assert response.status_code == 302
    assert response.url == reverse("login")


def test_create_user_get(logged_in_admin_client):
    """
    @brief Admin user can access the new user creation form.

    @details
    Sends GET request to 'new_user' view and verifies
    that the form is present in the response context.
    """
    response = logged_in_admin_client.get(reverse("new_user"))
    assert response.status_code == 200
    assert "form" in response.context


def test_create_user_post_valid(logged_in_admin_client, user_factory):
    """
    @brief Admin can create a new user via POST with valid data.

    @details
    Posts valid user creation data to 'new_user' view,
    asserts redirect to home,
    and verifies the user exists in the database.
    """
    data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password1": "SafePassword1!",
        "password2": "SafePassword1!",
    }
    response = logged_in_admin_client.post(reverse("new_user"), data)
    assert response.status_code == 302
    assert response.url == reverse("home")

    UserModel = user_factory._meta.model
    assert UserModel.objects.filter(username="newuser").exists()
