from django.urls import path
from . import views

urlpatterns = [
    path('test/', views.test, name = 'test'),
    path('api/log/click', views.log_click_event_endpoint, name = 'log click event')
]