import datetime

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse

from .models import *

BAD_REQUEST = JsonResponse({'reponse': "400 Bad request"}, status = 400)
OK = JsonResponse({'reponse': "200 OK"}, status = 200)

def get_user(hostname):
    user, created = User.objects.get_or_create()

    return user

def tobool(string):
    if string == "1":
        return True
    else:
        return False

# Create your views here.
def test(request):
    return HttpResponse("200 OK")

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