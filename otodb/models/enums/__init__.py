from enum import IntEnum

from django.db import models


# NOTE: Should match up with fixtures/category.yaml
class TagCategory(IntEnum):
    GENERAL   = 1
    LANGUAGE  = 2
    SOURCE    = 3
    CREATOR   = 4
    META      = 5

class Rating(models.IntegerChoices):
    NONE         = 0, "None"
    GENERAL      = 1, "General"
    SENSITIVE    = 2, "Sensitive"
    EXPLICIT     = 3, "Explicit"

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
