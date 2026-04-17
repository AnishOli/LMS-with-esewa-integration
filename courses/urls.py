from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('course/<slug:slug>/', views.course_detail, name='course_detail'),
    path('course/<slug:slug>/lesson/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('instructor/dashboard/', views.instructor_dashboard, name='instructor_dashboard'),
    path('instructor/course/create/', views.course_create, name='course_create'),
    path('instructor/course/<int:pk>/edit/', views.course_edit, name='course_edit'),
    path('instructor/course/<int:pk>/delete/', views.course_delete, name='course_delete'),
]
