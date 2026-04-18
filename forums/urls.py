from django.urls import path
from . import views

app_name = 'forums'

urlpatterns = [
    path('', views.forum_list, name='forum_list'),
    path('<int:forum_id>/', views.thread_list, name='thread_list'),
    path('thread/<int:thread_id>/', views.thread_detail, name='thread_detail'),
    path('<int:forum_id>/new/', views.create_thread, name='create_thread'),
    path('thread/<int:thread_id>/reply/', views.create_reply, name='create_reply'),
]
