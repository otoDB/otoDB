from django.db import models

from .base import SourceWorkBase


class SourceWorkNiconicoCategory(models.IntegerChoices):
    NONE                  =  0, "None"
    ENTERTAINMENT         =  1, "エンターテイメント"
    RADIO                 =  2, "ラジオ"
    MUSIC_SOUND           =  3, "音楽・サウンド"
    DANCE                 =  4, "ダンス"
    ANIMAL                =  5, "動物"
    NATURE                =  6, "自然"
    COOKING               =  7, "料理"
    TRAVELING_OUTDOOR     =  8, "旅行・アウトドア"
    VEHICLE               =  9, "乗り物"
    SPORTS                = 10, "スポーツ"
    SOCIETY_POLITICS_NEWS = 11, "社会・政治・時事"
    TECHNOLOGY_CRAFT      = 12, "技術・工作"
    COMMENTARY_LECTURE    = 13, "解説・講座"
    ANIME                 = 14, "アニメ"
    GAME                  = 15, "ゲーム"
    OTHER                 = 16, "その他"
    R18                   = 17, "R-18"


class SourceWorkNiconico(SourceWorkBase):
    source_id = models.CharField(max_length=100)
    likes = models.IntegerField(null=True, blank=True)
    mylists = models.IntegerField(null=True, blank=True)
    category = models.IntegerField(
        choices=SourceWorkNiconicoCategory.choices,
        default=SourceWorkNiconicoCategory.NONE
    )

    def __str__(self):
        return f'Niconico'
