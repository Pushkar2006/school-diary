from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.user_register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.user_profile, name='profile'),
    path('registeradmin', views.admin_register, name='admin_register'),
    path('registerteacher', views.teacher_register, name="teacher_register"),
    path('', views.diary, name='diary'),
    path('add-student/', views.add_student_page, name="add_student_page"),
    path('add-student/<str:i>/', views.add_student, name="add_student"),
    path('add-grade/', views.create_grade_page, name='create_grade'),
    path('my-grade/', views.my_grade, name='my_grade'),
    
    # URLs for password reset system
    path('reset_password/', auth_views.PasswordResetView.as_view(template_name="password_reset/reset.html"), name="reset_password"),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name="password_reset/done.html"), name="password_reset_done"),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="password_reset/confirm.html"), name="password_reset_confirm"),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name="password_reset/complete.html"), name="password_reset_complete"),
]

"""
ALL NAMES HERE

register
login
logout
profile
admin_register
teacher_register
diary

reset_password
password_reset_done
password_reset_complete
password_reset_confirm

"""