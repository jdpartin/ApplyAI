from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def home(request):
    return render(request, 'frontend/index.html')

def sign_in(request):
    return render(request, 'frontend/sign-in.html')

def sign_up(request):
    return render(request, 'frontend/sign-up.html')