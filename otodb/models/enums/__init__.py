from django.db import models
from enum import IntEnum

# NOTE: Should match up with fixtures/otodb/category.yaml
class TagCategory(IntEnum):
    GENERAL   = 1
    LANGUAGE  = 2
    SOURCE    = 3
    CREATOR   = 4
    META      = 5
    CHARACTER = 6

class Rating(models.IntegerChoices):
    NONE         = 0, "None"
    GENERAL      = 1, "General"
    SENSITIVE    = 2, "Sensitive"
    QUESTIONABLE = 3, "Questionable"
    EXPLICIT     = 4, "Explicit"

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
