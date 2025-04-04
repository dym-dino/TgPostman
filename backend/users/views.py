"""
User views

This file contains views for user registration, login, and API key management.
"""

# --------------------------------------------------------------------------------
# IMPORTS

from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import RegisterForm
from .models import User
from .serializers import UserRegisterSerializer, ApiKeySerializer


# --------------------------------------------------------------------------------
# VIEWS

class RegisterView(generics.CreateAPIView):
    """
    View for user registration. Allows any user to create an account.
    """
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]


class LoginAPIView(APIView):
    """
    View for logging in a user using username and password.
    Returns an API key if credentials are valid.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handle user login and return the API key if credentials are valid.

        :param request: The request object containing 'username' and 'password'
        :return: API key for authenticated user or error message
        """
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            return Response({'api_key': user.api_key})
        return Response({'error': 'Invalid credentials'}, status=400)


class ApiKeyView(generics.RetrieveAPIView):
    """
    View to retrieve the API key of the authenticated user.
    """
    serializer_class = ApiKeySerializer

    def get_object(self):
        """
        Return the current user object.

        :return: The user associated with the current request
        """
        return self.request.user


# --------------------------------------------------------------------------------
# WEB VIEWS

def register_view(request):
    """
    View for user registration via a web form.
    """
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def dashboard_view(request):
    """
    View for rendering the user dashboard page.
    Accessible only by authenticated users.
    """
    return render(request, 'dashboard.html', {'user': request.user})
