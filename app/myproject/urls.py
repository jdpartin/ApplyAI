from django.contrib import admin
from django.urls import path
from myapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('sign-in/', views.sign_in, name='sign_in'),
    path('sign-up/', views.sign_up, name='sign_up'),
    path('signupform/', views.signupform, name='signupform'),
    path('signinform/', views.signinform, name='signinform'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),

    # Form Views
    path('templates/frontend/modals/user_info_modal/', views.user_info_modal, name='user_info_modal'),
    path('templates/frontend/modals/education_modal/', views.education_modal, name='education_modal'),
    path('templates/frontend/modals/work_experience_modal/', views.work_experience_modal, name='work_experience_modal'),
    path('templates/frontend/modals/skill_modal/', views.skill_modal, name='skill_modal'),
    path('templates/frontend/modals/project_modal/', views.project_modal, name='project_modal'),
    path('templates/frontend/modals/certification_modal/', views.certification_modal, name='certification_modal'),
]
