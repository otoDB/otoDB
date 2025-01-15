from django.db import models


class TagCategory(models.IntegerChoices):
    GENERAL   = 0, "General"
    LANGUAGE  = 1, "Language"
    SOURCE    = 2, "Source"
    CREATOR   = 3, "Creator"
    META      = 4, "Meta"

class Rating(models.IntegerChoices):
    GENERAL      = 0, "General"
    SENSITIVE    = 1, "Sensitive"
    EXPLICIT     = 2, "Explicit"

class Status(models.IntegerChoices):
    PENDING = 0, "Pending"
    APPROVED = 1, "Approved"
    UNAPPROVED = 2, "Unapproved"

class WorkOrigin(models.IntegerChoices):
    AUTHOR   = 0, "Author"
    REUPLOAD = 1, "Reupload"

class WorkStatus(models.IntegerChoices):
    AVAILABLE = 0, "Available"
    DOWN      = 1, "Down"

RoleFlags = (
    ('OTHER',    'Other'),
    ('AUDIO',    'Audio'),
    ('VISUALS',  'Visuals'),
    ('DIRECTOR', 'Director'),
    ('HOST',     'Host'),
    ('MUSIC',    'Music'),
    ('ARTIST',   'Art'),
    ('THANKS',   'Special Thanks'),
)

class Platform(models.IntegerChoices):
    YOUTUBE    = 1, "YouTube"
    NICONICO   = 2, "Niconico"
    BILIBILI   = 3, "Bilibili"
    SOUNDCLOUD = 4, "SoundCloud"

    def from_str(s):
        for choice, string in Platform.choices:
            if string.lower() == s.lower():
                return choice
        return None
