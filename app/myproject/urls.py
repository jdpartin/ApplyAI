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

    # Modal Form Views
    path('templates/frontend/modals/user_info_modal/', views.user_info_modal, name='user_info_modal'),
    path('templates/frontend/modals/education_modal/', views.education_modal, name='education_modal'),
    path('templates/frontend/modals/work_experience_modal/', views.work_experience_modal, name='work_experience_modal'),
    path('templates/frontend/modals/skill_modal/', views.skill_modal, name='skill_modal'),
    path('templates/frontend/modals/project_modal/', views.project_modal, name='project_modal'),
    path('templates/frontend/modals/certification_modal/', views.certification_modal, name='certification_modal'),

    # Delete Views
    path('education-delete/', views.education_delete, name='education_delete'),
    path('work-experience-delete/', views.work_experience_delete, name='work_experience_delete'),
    path('skill-delete/', views.skill_delete, name='skill_delete'),
    path('project-delete/', views.project_delete, name='project_delete'),
    path('certification-delete/', views.certification_delete, name='certification_delete'),

    # JSON Data Views
    path('user-info-json/', views.user_info_data, name='user_info_json'),
    path('education-json/', views.education_data, name='education_json'),
    path('work-experience-json/', views.work_experience_data, name='work_experience_json'),
    path('skill-json/', views.skill_data, name='skill_json'),
    path('project-json/', views.project_data, name='project_json'),
    path('certification-json/', views.certification_data, name='certification_json'),

    # Chat bubble
    path('chat-bubble/', views.chat_bubble_view, name='chat_bubble'),
]
