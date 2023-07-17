import datetime

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse

from .models import *

BAD_REQUEST = JsonResponse({'reponse': "400 Bad request"}, status = 400)
OK = JsonResponse({'reponse': "200 OK"}, status = 200)

def get_user(hostname):
    user, created = User.objects.get_or_create(device_hostname = hostname)

    return user

def tobool(string):
    if string == "1":
        return True
    else:
        return False

###### FRONTEND VIEWS
def test(request):
    return HttpResponse("200 OK")

def home(request):

    response_string = "<ul>"

    for item in User.objects.all():
        response_string += f"<li><a href=\"/{item.device_hostname}\">{item.device_hostname} since {item.first_seen}</a></li>"
    
    response_string += "</ul>"

    return HttpResponse(response_string)

def user_overview(request, hostname):

    response_string = "<ul>"

    user = User.objects.get(device_hostname = hostname)
    if user is None: # DOES NOT WORK! It throws DoesNotExist if no entry is found
        response_string = f"{hostname} not found"
    else:
        user_events = Event.objects.filter(user = user)
        if len(user_events) == 0:
            response_string = f"{hostname} has no logged events"
        else:
            for event in user_events:
                response_string += f"<li>{event.event_type}</li>"
            response_string += "</ul>"

    
    return HttpResponse(response_string)

##### ENDPOINT VIEWS

def log_sysinfo_endpoint(request):
    if request.method != "GET":
        return BAD_REQUEST

    try: # Try get data from the request
        hostname = request.GET['hostname']
    except: 
        return BAD_REQUEST
    
    user = get_user(hostname)
    
    sysinfo_obj = SystemInfo(user = user)
    sysinfo_obj.save()

    return OK
    
def log_gamesettings_endpoint(request):
    if request.method != "GET":
        return BAD_REQUEST
    
    try:
        hostname = request.GET['hostname']
        res = request.GET['res']
        mtog = tobool(request.GET['mtog'])
        stog = tobool(request.GET['stog'])
        mvol = float(request.GET['mvol'])
        svol = float(request.GET['svol'])
        gset = request.GET['gset']
    except: 
        return BAD_REQUEST
    
    user = get_user(hostname)
    
    gamesettings_obj = GameSettings(
        user = user,
        game_resolution = res,
        music_toggle = mtog,
        sound_toggle = stog,
        music_volume = mvol,
        sound_volume = svol,
        gameplay_settings = gset
    )
    gamesettings_obj.save()

    return OK

def log_click_event_endpoint(request):
    if request.method != "GET":
        return BAD_REQUEST

    try:
        hostname = request.GET['hostname']
        local_timestamp = datetime.datetime.fromtimestamp(int(request.GET['time']))
        action = int(request.GET['action'])
    except: 
        return BAD_REQUEST
    
    user = get_user(hostname)

    clickevent_obj = ClickEvent(user = user, local_timestamp = local_timestamp, event_type = "CLICK", action_id = action)
    clickevent_obj.save()

    return OK

def log_session_event_endpoint(request):
    if request.method != "GET":
        return BAD_REQUEST

    try:
        hostname = request.GET['hostname']
        local_timestamp = datetime.datetime.fromtimestamp(int(request.GET['time']))
        session_event_type = request.GET['setype']
        mode = int(request.GET['mode'])
        elapsed = int(request.GET['elapsed'])
        score1 = int(request.GET['s1'])
        score2 = int(request.GET['s2'])
        bounces = int(request['bounces'])
    except: 
        return BAD_REQUEST
    
    user = get_user(hostname)

    sessionevent_obj = GameSessionEvent(
        user = user,
        local_timestamp = local_timestamp,
        event_type = "SESSION",
        session_event_type = session_event_type,
        game_mode = mode,
        game_time_elapsed = elapsed,
        player1_score = score1,
        player2_score = score2,
        total_bounces = bounces
    )
    sessionevent_obj.save()

    return OK

def log_error_event_endpoint(request):
    if request.method != "GET":
        return BAD_REQUEST

    try:
        hostname = request.GET['hostname']
        local_timestamp = datetime.datetime.fromtimestamp(int(request.GET['time']))
        err = request.GET['err']
    except: 
        return BAD_REQUEST
    
    user = get_user(hostname)

    errorevent_obj = ErrorEvent(user = user, local_timestamp = local_timestamp, event_type = "ERROR", error_string = err)
    errorevent_obj.save()

    return OK