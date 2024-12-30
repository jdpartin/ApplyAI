from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import JsonResponse
import json
from django.urls import reverse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import redirect


def home(request):
    return render(request, 'frontend/index.html')


# path in urls is sign-in
def sign_in(request):
    return render(request, 'frontend/sign-in.html')

def signinform(request):
    if request.method == 'POST':
        try:
            # Parse the JSON body
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')

            # Check if both fields are provided
            if not email or not password:
                return JsonResponse({'error': 'Email and password are required.'}, status=400)

            # Authenticate the user
            user = authenticate(request, username=email, password=password)
            if user is not None:
                # Log the user in
                login(request, user)
                return JsonResponse({
                    'success': 'User signed in successfully.',
                    'redirect': reverse('dashboard')  # Redirect to the homepage
                }, status=200)
            else:
                return JsonResponse({'error': 'Invalid email or password.'}, status=401)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data.'}, status=400)

    return JsonResponse({'error': 'Invalid request method. Use POST.'}, status=405)


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



@login_required
def dashboard(request):
    user = request.user
    return render(request, 'frontend/dashboard.html', {'username': user.username})


def logout_view(request):
    """
    Logs out the user and redirects to the home page.
    """
    logout(request)
    return redirect('home')  # Replace 'home' with the name of your index route