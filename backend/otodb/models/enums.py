from django.db import models


class WorkTagCategory(models.IntegerChoices):
    GENERAL   = 0, "General"
    LANGUAGE  = 1, "Language"
    SONG      = 2, "Song"
    SOURCE    = 3, "Source"
    CREATOR   = 4, "Creator"
    META      = 5, "Meta"

class SongTagCategory(models.IntegerChoices):
    GENERAL   = 0, "General"
    GENRE     = 1, "Genre"
    LANGUAGE  = 2, "Language"
    AUTHOR    = 3, "Author"
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

class WorkRelationTypes(models.IntegerChoices):
    SEQUEL      = 0, "Sequel"
    RESPECT     = 1, "Respect"
    COLLAB_PART = 2, "Collab Part"
    SAMPLE      = 3, "Sample"

class SongRelationTypes(models.IntegerChoices):
    REMIX    = 0, "Remix"
    REMASTER = 1, "Remaster"
    MEDLEY   = 2, "Medley"
    SEQUEL   = 3, "Sequel"
