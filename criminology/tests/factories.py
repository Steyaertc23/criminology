"""
@file tests/factories.py

@brief Test factories for user model instances.

@details
This module provides factory classes for creating user instances used
in testing, including regular users and superusers. It uses Factory Boy
to generate test data consistently and efficiently.
"""

import factory
from django.contrib.auth import get_user_model

User = get_user_model()

class UserFactory(factory.django.DjangoModelFactory):
    """
    @brief Factory for creating regular user instances.

    @details
    Provides a user factory for tests using DjangoModelFactory.
    Generates unique usernames and emails, sets a default password,
    and sets `first_login` to True by default.
    """
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'defaultpass')
    first_login = True


class SuperUserFactory(UserFactory):
    """
    @brief Factory for creating superuser instances.

    @details
    Extends UserFactory but overrides the creation method to use the
    custom manager's `create_superuser` method, ensuring proper flags like
    `is_staff` and `is_superuser` are set.
    """
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """
        @brief Override _create method to call create_superuser.

        @details
        Ensures that superusers are created with correct privileges by
        delegating creation to the custom user model manager's create_superuser method.
        """
        return model_class.objects.create_superuser(*args, **kwargs)
