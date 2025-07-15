"""
@file user/admin.py
@brief Django admin configuration for the CustomUser model.

@details
Extends Django's built-in UserAdmin to manage CustomUser instances with
additional custom fields such as `expiration_date`, `first_login`, and
`security_question`. Also includes color-coded display of expiration status.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserChangeForm


@admin.register(CustomUser)
class UserAdmin(BaseUserAdmin):
    """
    @brief Admin configuration for the CustomUser model.

    @details
    Extends Django's built-in UserAdmin to customize the admin interface
    for CustomUser. Adds display of additional fields such as expiration date,
    first login flag, and security question. Formats expiration date with color
    coding based on whether it's expired, current, or not set.
    """
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    list_display = (
        'username',
        'email',
        'is_staff',
        'first_login',
        'expiration_date',
    )
    list_filter = (
        'is_staff',
        'is_active',
        'is_superuser',
        'first_login',
    )

    @admin.display(description="Expires", ordering="expiration_date")
    def colored_expiration_date(self, obj):
        """
        @brief Displays expiration_date with color-coded HTML in admin list view.

        @details
        Colors the expiration date text in red if expired, green if valid,
        or gray if unset. Helps visually identify expired accounts quickly.

        @param obj CustomUser instance.
        @return str HTML-formatted string showing the date with color.
        """
        if not obj.expiration_date:
            return format_html('<span style="color: gray;">None</span>')
        elif obj.is_expired():
            return format_html(f'<span style="color: red;">{obj.expiration_date}</span>')
        else:
            return format_html(f'<span style="color: green;">{obj.expiration_date}</span>')

    search_fields = (
        'username',
        'email',
        'first_name',
        'last_name',
    )
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        (_('Personal Info'), {'fields': ('first_name', 'last_name')}),
        (_('Security Info'), {'fields': ('security_question', 'security_answer')}),
        (_('Account Flags'), {'fields': ('first_login',)}),
        (_('Permissions'), {
            'fields': (
                'is_active',
                'is_staff',
                'groups',
                'user_permissions',
            )
        }),
        (_('Important Dates'), {'fields': ('last_login', 'date_joined', 'expiration_date')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'email',
                'first_name',
                'last_name',
                'password1',
                'password2',
                'expiration_date',
                'first_login',
                'is_active',
                'is_staff',
                'groups',
                'user_permissions',
            ),
        }),
    )
