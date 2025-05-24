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

class ProfileConnectionTypes(models.IntegerChoices):
    NICONICO  = 0, "Niconico"
    YOUTUBE   = 1, "YouTube"
    BILIBILI  = 2, "Bilibili"
    X         = 3, "X"
    BLUESKY   = 4, "Bluesky"

class SongConnectionTypes(models.IntegerChoices):
    VGMDB         = 0, "VGMdb"
    VOCADB        = 1, "VocaDB"
    DISCOGS       = 2, "Discogs"
    RATEYOURMUSIC = 3, "Rate Your Music"
    REMYWIKI      = 4, "RemyWiki"
    ZENIUS        = 5, "Zenius -I- vanisher.com"

class TagWorkConnectionTypes(models.IntegerChoices):
    OTOMADWIKI    = 1, "otomad.wiki"
    OTOMADFANDOM  = 2, "Otomad Wiki 2"

    NICOPEDIA     = 3, "Niconico Encyclopedia"
    KNOWYOURMEME  = 4, "KnowYourMeme"
    WIKIPEDIA     = 5, "Wikipedia"
    NAMUWIKI      = 6, "Namu Wiki"

    ANIKORE       = 7, "AniKore"
    BANGUMI       = 8, "Bangumi"
    ANIDB         = 9, "AniDB"
    MYANIMELIST   = 10, "MyAnimeList"
    # ANILIST       = 11, "AniList"
    # KITSU         = 12, "Kitsu"
    # ANIMEPLANET   = 13, "Anime-Planet"

    # LETTERBOXD    = 14, "Letterboxd"
    # IMDB          = 15, "IMDb"

    # VNDB          = 16, "vndb"
    # EROGAMESCAPE  = 17, "ErogameScape"

    WEBSITE       = 0, "Website"

class LanguageTypes(models.IntegerChoices):
    NOT_APPLICABLE     = 0, "N/A"
    ENGLISH            = 1, "en"
    JAPANESE           = 2, "ja"
    SIMPLIFIED_CHINESE = 3, "zh-cn"
    KOREAN             = 4, "ko"
