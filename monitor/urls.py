from django.urls import path

from . import views


urlpatterns = [
    path('log/', views.create_log, name='create-log'),
    path('logs/', views.list_logs, name='list-logs'),
]
