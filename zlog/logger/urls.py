from django.urls import path
from . import views

urlpatterns = [
    path('ping/', views.ping, name = 'ping'),
    path('forbidden/', views.not_authenticated, name = 'forbidden'),

    path('', views.home, name = 'homepage'),
    path('user/<str:hostname>/', views.user_overview, name = 'user overview'),
    path('user/', views.home_redirect, name = 'homepage redirect'),

    path('api/log/sysinfo', views.log_sysinfo_endpoint, name = 'log sysinfo'),
    path('api/log/gamesettings', views.log_gamesettings_endpoint, name = 'log game settings'),
    path('api/log/click', views.log_click_event_endpoint, name = 'log click event'),
    path('api/log/session', views.log_session_event_endpoint, name = 'log session event'),
    path('api/log/error', views.log_error_event_endpoint, name = 'log error event')
]