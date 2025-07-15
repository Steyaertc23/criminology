"""
@file user/views.py
@brief Views related to user account management, including login flows, security questions, and account recovery.
@details
This module defines views for handling user authentication flows such as:
- Forced password reset on first login
- Security question setup
- Multi-step account recovery
- Admin-based user creation
Includes validation logic, session handling, and security checks.
"""

import csv
import io
import secrets
import string
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django_ratelimit.decorators import ratelimit
from django.contrib.auth.hashers import check_password
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect


from .forms import (
    CustomUserCreationForm,
    SecurityQuestionForm,
    PasswordResetNoOldForm,
)

User = get_user_model()


@login_required
def check_first_login(request):
    """
    @brief Redirect users on first login to force password reset.
    @details
    If the user is not a superuser and has the `first_login` flag set to True,
    they are redirected to the forced password reset page.
    Otherwise, the user is redirected to the home page.
    """
    user = request.user
    if getattr(user, "first_login", False) and not getattr(user, "is_superuser", False):
        return redirect("force_password_reset")
    return redirect("home")


@login_required
def force_password_reset(request):
    """
    @brief Force user to reset password without requiring the old password.
    @details
    Displays a password reset form that skips the old password field.
    On successful POST:
    - Updates the user’s password.
    - Keeps the user logged in using `update_session_auth_hash`.
    - Marks `first_login` as False.
    - Redirects the user to the security question setup view.
    Otherwise, redisplays the form with validation errors.
    """
    if request.method == "POST":
        form = PasswordResetNoOldForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            user.first_login = False
            user.save()
            messages.success(request, "Password changed successfully.")
            return redirect("setup_security_question")
    else:
        form = PasswordResetNoOldForm(instance=request.user)
    return render(request, "user/force_password_reset.html", {"form": form})


@login_required
def setup_security_question(request):
    """
    @brief Allow user to set up their security question and answer.
    @details
    - If the user already has both `security_question` and `security_answer` set,
      they are redirected to the home page.
    - Otherwise, displays a form to set both fields.
    - On successful submission, saves the hashed answer and redirects home.
    """
    user = request.user
    if user.security_question and user.security_answer:
        return redirect("home")

    if request.method == "POST":
        form = SecurityQuestionForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Security question set successfully.")
            return redirect("home")
    else:
        form = SecurityQuestionForm(instance=user)
    return render(request, "user/setup_security_question.html", {"form": form})


@ratelimit(key="ip", rate="5/m", block=True)
def account_recovery_step1(request):
    """
    @brief Account recovery step 1: verify username and email.
    @details
    - Accepts POST with username and email.
    - If a matching user is found, stores user ID and security question in the session.
    - Sets session expiry to 10 minutes.
    - Redirects to step 2.
    - On failure, shows error and redisplays form.
    """
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")

        try:
            user = User.objects.get(username=username, email=email)
            request.session["recovery_user_id"] = user.id
            request.session["security_question"] = user.security_question
            request.session.set_expiry(600)  # 10 minutes
            return redirect("account_recovery_step2")
        except User.DoesNotExist:
            messages.error(request, "User with that username and email does not exist.")
    return render(request, "users/account_recovery_step1.html")


@ratelimit(key="ip", rate="5/m", block=True)
def account_recovery_step2(request):
    """
    @brief Account recovery step 2: validate security answer.
    @details
    - Retrieves stored user ID and security question from session.
    - If data is missing, the session has likely expired and user is redirected to step 1.
    - On POST, checks the submitted answer against the hashed one.
    - Redirects to step 3 on success; shows error on failure.
    """
    user_id = request.session.get("recovery_user_id")
    question = request.session.get("security_question")

    if not user_id or not question:
        messages.error(request, "Session expired or invalid. Please start over.")
        return redirect("account_recovery_step1")

    if request.method == "POST":
        answer = request.POST.get("security_answer")

        try:
            user = User.objects.get(id=user_id)
            if check_password(answer.strip(), user.security_answer):
                return redirect("account_recovery_step3")
            else:
                messages.error(request, "Incorrect security answer.")
        except User.DoesNotExist:
            messages.error(request, "User does not exist.")
            return redirect("account_recovery_step1")

    return render(request, "users/account_recovery_step2.html", {"question": question})


@ratelimit(key="ip", rate="5/m", block=True)
def account_recovery_step3(request):
    """
    @brief Account recovery step 3: reset password.
    @details
    - Allows the user to set a new password.
    - Checks password confirmation and strength using Django validators.
    - If valid, updates the password, clears the session, and redirects to login.
    - Otherwise, shows appropriate validation errors.
    """
    user_id = request.session.get("recovery_user_id")

    if not user_id:
        messages.error(request, "Session expired or invalid. Please start over.")
        return redirect("account_recovery_step1")

    if request.method == "POST":
        new_password = request.POST.get("new_password")
        new_password_confirm = request.POST.get("new_password_confirm")

        if new_password != new_password_confirm:
            messages.error(request, "Passwords do not match.")
            return render(request, "users/account_recovery_step3.html")

        try:
            user = User.objects.get(id=user_id)

            try:
                validate_password(new_password, user)
            except ValidationError as e:
                messages.error(
                    request, f"Password validation error: {'; '.join(e.messages)}"
                )
                return render(request, "users/account_recovery_step3.html")

            user.set_password(new_password)
            user.save()

            request.session.flush()

            messages.success(request, "Password reset successful. You can now log in.")
            return redirect("login")
        except User.DoesNotExist:
            messages.error(request, "User does not exist.")
            return redirect("account_recovery_step1")

    return render(request, "users/account_recovery_step3.html")


is_admin = lambda u: u.is_staff


@login_required
@user_passes_test(is_admin)
def create_user(request):
    """
    @brief Admin view to create a new user.
    @details
    - Accessible only to staff users.
    - On GET: renders the user creation form.
    - On POST: validates and saves the new user.
    - Displays success or error messages accordingly.
    - Redirects to home on successful user creation.
    """
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "User created successfully!")
            return redirect("home")
        else:
            messages.error(request, "There was an error in creating the user.")
    else:
        form = CustomUserCreationForm()

    return render(request, "user/create_new_user.html", {"form": form})


def generate_temp_password(length=6):
    """Generate a random 6-character password using letters and digits."""
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

@login_required
@user_passes_test(lambda u: u.is_staff)
def mass_add_users(request):
    """
    @brief Bulk adds users with no staff privileges from a CSV file.
    @details
    Accepts a CSV file with headers: first_name,last_name,email,expiration_date.
    Generates usernames from the email prefix, sets a random 6-character password,
    and returns a downloadable CSV of usernames and temporary passwords.
    """
    if request.method == "POST" and request.FILES.get("csv_file"):
        csv_file = request.FILES["csv_file"]

        if not csv_file.name.endswith(".csv"):
            messages.error(request, "Please upload a valid .csv file.")
            return redirect("mass_add_users")

        try:
            decoded = csv_file.read().decode("utf-8")
            reader = csv.reader(io.StringIO(decoded))

            expected_header = ["first_name", "last_name", "email", "expiration_date"]
            header = next(reader, None)
            if not header or [h.strip().lower() for h in header] != expected_header:
                messages.error(
                    request,
                    f"Invalid CSV header. Expected: {','.join(expected_header)}",
                )
                return redirect("mass_add_users")

            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["first_name", "last_name", "email","username", "temporary_password"])

            with transaction.atomic():
                for row_num, row in enumerate(reader, start=2):
                    if len(row) != 4:
                        messages.warning(
                            request, f"Skipping row {row_num}: wrong number of fields."
                        )
                        continue

                    first_name, last_name, email, expiration_date = row
                    username = email.split("@")[0]
                    temp_password = generate_temp_password()

                    User.objects.create_user(
                        username=username,
                        email=email,
                        first_name=first_name,
                        last_name=last_name,
                        expiration_date=expiration_date,
                        password=temp_password,
                        first_login=True,
                    )

                    writer.writerow([first_name, last_name, email, username, temp_password])

            output.seek(0)
            response = HttpResponse(output, content_type="text/csv")
            response["Content-Disposition"] = 'attachment; filename="new_user_credentials.csv"'
            return response

        except Exception as e:
            messages.error(request, f"Error processing file: {e}")
            return redirect("mass_add_users")

    return render(request, "user/create_new_users.html")
