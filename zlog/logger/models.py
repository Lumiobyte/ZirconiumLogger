from django.db import models

# Create your models here.
class User(models.Model):

    first_seen = models.DateTimeField(auto_now_add = True)
    device_hostname = models.CharField(max_length = 15, default = "?") # individual users are identified by their hostname 

    class Meta:
        ordering = ['first_seen']

    def __str__(self):
        return self.device_hostname


class SystemInfo(models.Model):

    user = models.ForeignKey(User, on_delete = models.CASCADE)
    entry_created = models.DateTimeField(auto_now_add = True)

    # tech specs
    # timezone + locale

    class Meta:
        ordering = ['-entry_created']


class GameSettings(models.Model):

    user = models.ForeignKey(User, on_delete = models.CASCADE)
    entry_created = models.DateTimeField(auto_now_add = True)

    game_resolution = models.CharField(max_length = 9)

    music_toggle = models.BooleanField()
    sound_toggle = models.BooleanField()
    music_volume = models.FloatField()
    sound_volume = models.FloatField()

    gameplay_settings = models.CharField(max_length = 19) # a string representing settings e.g. "100,2,3,1" meaning score goal 100, fast ball, many powerups, normal ai

    class Meta:
        ordering = ['-entry_created']


class Event(models.Model):

    user = models.ForeignKey(User, on_delete = models.CASCADE)
    entry_created = models.DateTimeField(auto_now_add = True)

    #ip_address = models.GenericIPAddressField(null = True)
    local_timestamp = models.DateTimeField(null = True)

    event_type = models.CharField(max_length = 10) # "CLICK", "SESSION", "ERROR"

    class Meta:
        ordering = ['-local_timestamp']


class ClickEvent(Event):

    action_id = models.IntegerField(default = 0)


class GameSessionEvent(Event):

    session_event_type = models.CharField(max_length = 6, default = "?") # PAUSE or FINISH depending on whether this is triggered by user pausing or game concluding

    game_mode = models.IntegerField()
    game_time_elapsed = models.PositiveBigIntegerField()

    player1_score = models.PositiveIntegerField()
    player2_score = models.PositiveIntegerField()

    total_bounces = models.PositiveIntegerField()

class ErrorEvent(Event):

    error_string = models.TextField()