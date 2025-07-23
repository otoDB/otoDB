from django.db import models


class WorkTagCategory(models.IntegerChoices):
    GENERAL   = 0, "General"
    EVENT     = 1, "Event"
    SONG      = 2, "Song"
    SOURCE    = 3, "Source"
    CREATOR   = 4, "Creator"
    META      = 5, "Meta"
    MEDIA     = 6, "Media"

class SongTagCategory(models.IntegerChoices):
    GENERAL   = 0, "General"
    GENRE     = 1, "Genre"
    AUTHOR    = 2, "Author"
    META      = 3, "Meta"

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

    @staticmethod
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
    WEBSITE   = 0, "Website"

    NICONICO  = 1, "Niconico"
    YOUTUBE   = 2, "YouTube"
    BILIBILI  = 3, "Bilibili"
    TWITTER   = 4, "Twitter"
    BLUESKY   = 5, "Bluesky"

class SongConnectionTypes(models.IntegerChoices):
    VGMDB         = 0, "VGMdb"
    VOCADB        = 1, "VocaDB"
    DISCOGS       = 2, "Discogs"
    MUSICBRAINZ   = 3, "MusicBrainz"
    RATEYOURMUSIC = 4, "Rate Your Music"
    DOJINMUSIC    = 5, "dojin-music.info"

    REMYWIKI      = 20, "RemyWiki"
    SILENTBLUE    = 21, "Silent Blue"
    ZENIUS        = 22, "Zenius -I- vanisher.com"

    NNDMEDLEYWIKI = 30, "NND Medley Wiki"

class TagWorkConnectionTypes(models.IntegerChoices):
    OTOMADWIKI    = 1, "otomad.wiki"
    OTOMADFANDOM  = 2, "Otomad Wiki 2"

    NICOPEDIA     = 20, "Niconico Encyclopedia"
    PIXIV_DICT    = 21, "Pixiv Dictionary"
    WIKIPEDIA     = 22, "Wikipedia"
    NAMUWIKI      = 23, "Namu Wiki"
    KNOWYOURMEME  = 24, "Know Your Meme"

class MediaConnectionTypes(models.IntegerChoices):
    ANIKORE       = 1, "AniKore"
    BANGUMI       = 2, "Bangumi"
    ANIDB         = 3, "AniDB"
    MYANIMELIST   = 4, "MyAnimeList"
    ANILIST       = 5, "AniList"
    KITSU         = 6, "Kitsu"
    ANIMEPLANET   = 7, "Anime-Planet"

    IMDB          = 20, "IMDb"
    LETTERBOXD    = 21, "Letterboxd"

    VNDB          = 40, "vndb"
    EROGAMESCAPE  = 41, "ErogameScape"

class LanguageTypes(models.IntegerChoices):
    NOT_APPLICABLE     = 0, "N/A"
    ENGLISH            = 1, "en"
    JAPANESE           = 2, "ja"
    SIMPLIFIED_CHINESE = 3, "zh-cn"
    KOREAN             = 4, "ko"

class Role(models.IntegerChoices):
	AUDIO = 1, "Audio"
	VISUALS = 2, "Visuals"
	DIRECTOR = 4, "Director"
	MUSIC = 8, "Music"
	ARTWORK = 16, "Artwork"
	THANKS = 32, "Special Thanks"

class ThemePref(models.IntegerChoices):
    DEFAULT = 0, "Default"
    ANIKI   = 1, "Aniki"
