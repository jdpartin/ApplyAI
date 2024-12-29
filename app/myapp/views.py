from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import JsonResponse
import json
from django.urls import reverse


def home(request):
    return render(request, 'frontend/index.html')

# path in urls is sign-in
def sign_in(request):
    return render(request, 'frontend/sign-in.html')

# path in urls is sign-up
def sign_up(request):
    return render(request, 'frontend/sign-up.html')

def signupform(request):
    if request.method == 'POST':
        try:
            # Parse the JSON body
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            confirm_password = data.get('confirmPassword')

            # Check if all fields are provided
            if not email or not password or not confirm_password:
                return JsonResponse({'error': 'All fields are required.'}, status=400)

            # Check if passwords match
            if password != confirm_password:
                return JsonResponse({'error': 'Passwords do not match.'}, status=400)

            # Validate password strength using Django's built-in validation
            try:
                validate_password(password)
            except ValidationError as e:
                return JsonResponse({'error': list(e)}, status=400)

            # Check if the email already exists
            if User.objects.filter(email=email).exists():
                return JsonResponse({'error': 'Email is already registered.'}, status=400)

            # Create the user with email as username
            user = User.objects.create_user(
                username=email,  # Use email as username
                email=email,
                password=password
            )

            # Redirect after successful signup
            return JsonResponse({
                'success': 'User created successfully.',
                'redirect': reverse('sign_in')
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data.'}, status=400)

    return JsonResponse({'error': 'Invalid request method. Use POST.'}, status=405)
