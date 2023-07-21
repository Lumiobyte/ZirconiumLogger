from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register([ButtonDefinition, User, SystemInfo, GameSettings, Event, ClickEvent, GameSessionEvent, ErrorEvent])