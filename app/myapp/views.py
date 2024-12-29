from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def home(request):
    return render(request, 'frontend/index.html')

# path in urls is sign-in
def sign_in(request):
    return render(request, 'frontend/sign-in.html')

# path in urls is sign-up
def sign_up(request):
    return render(request, 'frontend/sign-up.html')