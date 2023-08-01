import datetime
import json

from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .models import *

BAD_REQUEST = JsonResponse({'response': "400 Bad request"}, status = 400)
OK = JsonResponse({'response': "200 OK"}, status = 200)

def get_user(hostname):
    user, created = User.objects.get_or_create(device_hostname = hostname)

    return user

def get_button_definition(action_id):
    try:
        return ButtonDefinition.objects.get(action_id = action_id).action_string
    except ButtonDefinition.DoesNotExist:
        return "Unknown Button"

def tobool(value):
    if value == "1" or value == 1:
        return True
    else:
        return False
    
def create_dict(string):
    string = string.decode('UTF-8')
    return json.loads(string.replace("'", '"'))

def merge_dicts(dict1, dict2):
    return {**dict1, **dict2}


###### FRONTEND VIEWS
def ping(request):
    return OK

def not_authenticated(request):

    return render(request, 'logger/not_authenticated.html', {})

def home_redirect(request):

    return redirect(home)

def home(request):

    if not request.user.is_authenticated:
        return redirect(not_authenticated)

    users =  User.objects.all()
    context = {'users': [], 'user_count': users.count()}

    for item in users:
        context['users'].append(item)

    return render(request, 'logger/home.html', context)

def user_overview(request, hostname):

    if not request.user.is_authenticated:
        return redirect(not_authenticated)

    user = User.objects.get(device_hostname = hostname)

    context = {}
    user_events = Event.objects.filter(user = user)
    user_sysinfo = SystemInfo.objects.filter(user = user).first()

    if not user_sysinfo:
        context['user_info'] = {'first_seen': user.first_seen, 'hostname': hostname, 'os': None}

    else:
        context['user_info'] = {'first_seen': user.first_seen, 'hostname': hostname, 'os': user_sysinfo.operating_system, 'processor': user_sysinfo.processor, 'python_version': user_sysinfo.python_version, 'screen_resolution': user_sysinfo.screen_res, 'ram': round(user_sysinfo.physical_memory / 100000000)}
    
    context['events'] = []
    context['event_count'] = user_events.count()

    for event in user_events:
        if event.event_type == "CLICK":
            event_info = {'type': "CLICK", 'timestamp': event.local_timestamp, 'action_id': event.clickevent.action_id, 'action_desc': get_button_definition(event.clickevent.action_id)}
        elif event.event_type == "SESSION":
            event_info = {'type': "SESSION",
                          'timestamp': event.local_timestamp,
                          'session_type': event.gamesessionevent.session_event_type,
                          'gamemode': ['AI vs AI', 'Player vs AI', 'Multiplayer', 'Competitive'][event.gamesessionevent.game_mode],
                          'elapsed': event.gamesessionevent.game_time_elapsed,
                          'score1': event.gamesessionevent.player1_score,
                          'score2': event.gamesessionevent.player2_score,
                          'bounces': event.gamesessionevent.total_bounces,
                          'misses': event.gamesessionevent.serves_missed
                          }
        elif event.event_type == "ERROR":
            event_info = {'type': "ERROR", 'timestamp': event.local_timestamp, 'error_name': event.errorevent.error_name, 'error_string': event.errorevent.error_string}

        context['events'].append(event_info)

    user_settings = GameSettings.objects.filter(user = user).first() # if doesn't exist, set gameplay_settings in context to none
    if not user_settings:
        context['settings'] = None
    else:
        context['settings'] = dict(merge_dicts({'last_updated': user_settings.entry_created,
                                    'res': "FULLSCREEN" if user_settings.game_resolution == "0" else user_settings.game_resolution,
                                    'mtog': tobool(user_settings.music_toggle),
                                    'stog': tobool(user_settings.sound_toggle),
                                    'mvol': user_settings.music_volume,
                                    'svol': user_settings.sound_volume,
                                    }, user_settings.gameplay_settings))
    
    return render(request, 'logger/user_overview.html', context)

##### ENDPOINT VIEWS

@csrf_exempt
def log_sysinfo_endpoint(request):
    if request.method != "POST":
        return BAD_REQUEST

    try: # Try get data from the request
        data = create_dict(request.body)
        hostname = data['hostname']
        op_sys = data['os']
        proc = data['processor']
        pyver = data['pyver']
        screenres = data['screenres']
        ram = int(data['physicalmem'])
    except Exception as e: 
        return BAD_REQUEST
    
    user = get_user(hostname)
    
    sysinfo_obj = SystemInfo(user = user, operating_system = op_sys, processor = proc, python_version = pyver, screen_res = screenres, physical_memory = ram)
    sysinfo_obj.save()

    return OK
    
@csrf_exempt
def log_gamesettings_endpoint(request):
    if request.method != "POST":
        return BAD_REQUEST
    
    try:
        data = create_dict(request.body)
        hostname = data['hostname']
        res = data['res']
        mtog = tobool(data['mtog'])
        stog = tobool(data['stog'])
        mvol = float(data['mvol'])
        svol = float(data['svol'])
        gset = data['gset']
    except: 
        return BAD_REQUEST
    
    user = get_user(hostname)

    gset_json_untranslated = {}
    keys = ['cas_goal', 'cas_speed', 'powerups', 'ai_diff', 'comp_goal', 'comp_speed', 'serve_miss', 'ball_speedup']
    for i, value in enumerate(gset.split(',')):
        gset_json_untranslated[keys[i]] = tobool(value) if i == 7 else int(value)

    gameplay_setting_text_map = {
        "cas_goal": None,
        "cas_speed": ["Normal", "Fast"],
        "powerups":  ["OFF", "Few", "Normal", "Many", "Party"],
        "ai_diff": ["Easy", "Normal", "Hard"],
        "comp_goal": None,
        "comp_speed": ["Normal", "Fast"],
        "serve_miss": ["None", "Lose Point", "Lose Life"],
        "ball_speedup": {True: "ON", False: "OFF"}
    }

    gset_json_translated = {}
    for setting in gameplay_setting_text_map:
        if gameplay_setting_text_map[setting] is None:
            gset_json_translated[setting] = gset_json_untranslated[setting]
        else:
            gset_json_translated[setting] = gameplay_setting_text_map[setting][gset_json_untranslated[setting]]
    
    gamesettings_obj = GameSettings(
        user = user,
        game_resolution = res,
        music_toggle = mtog,
        sound_toggle = stog,
        music_volume = mvol,
        sound_volume = svol,
        gameplay_settings = gset_json_translated
    )
    gamesettings_obj.save()

    return OK

@csrf_exempt
def log_click_event_endpoint(request):
    if request.method != "POST":
        return BAD_REQUEST

    try:
        data = create_dict(request.body)
        hostname = data['hostname']
        local_timestamp = datetime.datetime.fromtimestamp(float(data['time']))
        action = int(data['action'])
    except:
        return BAD_REQUEST
    
    user = get_user(hostname)

    clickevent_obj = ClickEvent(user = user, local_timestamp = local_timestamp, event_type = "CLICK", action_id = action)
    clickevent_obj.save()

    return OK

@csrf_exempt
def log_session_event_endpoint(request):
    if request.method != "POST":
        return BAD_REQUEST

    try:
        data = create_dict(request.body)
        hostname = data['hostname']
        local_timestamp = datetime.datetime.fromtimestamp(float(data['time']))
        session_event_type = data['setype']
        mode = int(data['mode'])
        elapsed = int(data['elapsed'])
        score1 = int(data['s1'])
        score2 = int(data['s2'])
        bounces = int(data['bounces'])
        misses = int(data['misses'])
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
        total_bounces = bounces,
        serves_missed = misses
    )
    sessionevent_obj.save()

    return OK

@csrf_exempt
def log_error_event_endpoint(request):
    if request.method != "POST":
        return BAD_REQUEST

    try:
        data = create_dict(request.body)
        hostname = data['hostname']
        local_timestamp = datetime.datetime.fromtimestamp(float(data['time']))
        err_name = data['err_name']
        err = data['err']
    except: 
        return BAD_REQUEST
    
    user = get_user(hostname)

    errorevent_obj = ErrorEvent(user = user, local_timestamp = local_timestamp, event_type = "ERROR", error_name = err_name, error_string = err)
    errorevent_obj.save()

    return OK