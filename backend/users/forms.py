"""
User registration form

This file contains the form for user registration using a custom User model.
"""

# --------------------------------------------------------------------------------
# IMPORTS

from django.contrib.auth.forms import UserCreationForm
from .models import User


# --------------------------------------------------------------------------------
# FORM DEFINITION

class RegisterForm(UserCreationForm):
    """
    Custom form for user registration.
    Extends the default UserCreationForm to use the custom User model.
    """

    class Meta:
        model = User
        fields = ('username',)
