from django.urls import path
from . import views

urlpatterns = [
    path('test/', views.test, name = 'test'),

    path('', views.home, name = 'homepage'),
    path('<str:hostname>/', views.user_overview, name = 'user overview'),

    path('api/log/click', views.log_click_event_endpoint, name = 'log click event'),
    path('api/log/session', views.log_session_event_endpoint, name = "log session event")
]