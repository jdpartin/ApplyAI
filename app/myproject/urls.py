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

    # API endpoints for updating user info
    path('api/update-user-info/', views.update_user_info, name='update_user_info'),

    # API endpoints for education
    path('api/add-education/', views.add_education, name='add_education'),
    path('api/edit-education/<int:id>/', views.edit_education, name='edit_education'),
    path('api/delete-education/<int:id>/', views.delete_education, name='delete_education'),

    # API endpoints for work experience
    path('api/add-work-experience/', views.add_work_experience, name='add_work_experience'),
    path('api/edit-work-experience/<int:id>/', views.edit_work_experience, name='edit_work_experience'),
    path('api/delete-work-experience/<int:id>/', views.delete_work_experience, name='delete_work_experience'),

    # API endpoints for skills
    path('api/add-skill/', views.add_skill, name='add_skill'),
    path('api/edit-skill/<int:id>/', views.edit_skill, name='edit_skill'),
    path('api/delete-skill/<int:id>/', views.delete_skill, name='delete_skill'),

    # API endpoints for projects
    path('api/add-project/', views.add_project, name='add_project'),
    path('api/edit-project/<int:id>/', views.edit_project, name='edit_project'),
    path('api/delete-project/<int:id>/', views.delete_project, name='delete_project'),

    # API endpoints for certifications
    path('api/add-certification/', views.add_certification, name='add_certification'),
    path('api/edit-certification/<int:id>/', views.edit_certification, name='edit_certification'),
    path('api/delete-certification/<int:id>/', views.delete_certification, name='delete_certification'),
]
