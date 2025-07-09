import requests
import json
import html
import re
from time import mktime
from datetime import datetime
import unicodedata
from http.cookiejar import MozillaCookieJar

import nh3
import diff_match_patch as dmp_mod

from yt_dlp import YoutubeDL
from yt_dlp.extractor.bilibili import BiliBiliIE, BilibiliFavoritesListIE
from yt_dlp.extractor.niconico import NiconicoIE, NiconicoPlaylistIE
from yt_dlp.extractor.youtube import YoutubeIE, YoutubeTabIE
from yt_dlp.extractor.soundcloud import SoundcloudIE, SoundcloudPlaylistIE

from django.conf import settings

from .models import TagWork
from .models.enums import Platform

def NFKC(s: str):
    return unicodedata.normalize('NFKC', s)

def get_diff(delta):
    dmp = dmp_mod.diff_match_patch()

    def diff_prettyHtml(diffs):
        html = []
        for (op, data) in diffs:
            text = (data.replace("&", "&amp;").replace("<", "&lt;")
                        .replace(">", "&gt;").replace("\n", "&para;<br>"))
            if op == dmp.DIFF_INSERT:
                html.append("<ins>%s</ins>" % text)
            elif op == dmp.DIFF_DELETE:
                html.append("<del>%s</del>" % text)
            elif op == dmp.DIFF_EQUAL:
                html.append("<span>%s</span>" % text)
        return "".join(html)

    diffs_html = []

    for change in delta.changes:
        match change.field:
            case 'tags':
                # TODO make this not hardcoded...
                old, new = set([c['work_tag'] for c in change.old]), set([c['work_tag'] for c in change.new])
                old, new = old - new, new - old
                changes = ['- ' + TagWork.objects.get(id=id_).slug for id_ in old] + [
                    '+ ' + TagWork.objects.get(id=id_).slug for id_ in new]
                diffs_html.append({'html': ('<br>').join(changes), 'field': change.field})
            case _:
                old, new = change.old, change.new
                diff_field = dmp.diff_main(str(old), str(new))
                dmp.diff_cleanupSemantic(diff_field)

                diffs_html.append({'html': diff_prettyHtml(diff_field).replace('&para;', ''), 'field': change.field})

    return diffs_html

ydl_playlist = YoutubeDL({'http_headers': {'Accept-Language': 'ja'}, 'extract_flat': True}, auto_init=True)
for e in (YoutubeTabIE, NiconicoPlaylistIE, BilibiliFavoritesListIE, SoundcloudPlaylistIE):
    ydl_playlist.add_info_extractor(e)

ydl, niconico_ie, jar = None, None, None
def reset_cookies(cookie_file=settings.COOKIES_FILE):
    global ydl, niconico_ie, jar

    jar = MozillaCookieJar(cookie_file)
    try:
        jar.load()
    except OSError:
        pass

    opts = { 'http_headers': {'Accept-Language': 'ja'}, 'noplaylist': True }
    if cookie_file:
        opts['cookiefile'] = cookie_file
    ydl = YoutubeDL(opts, auto_init=False)
    niconico_ie = ydl.get_info_extractor(NiconicoIE.ie_key())

    for e in (YoutubeIE, NiconicoIE, BiliBiliIE, SoundcloudIE):
        ydl.add_info_extractor(e)

reset_cookies()

make_video_url = {
    'youtube': lambda s: f'https://youtu.be/{s}',
    'niconico': lambda s: f'https://nicovideo.jp/watch/{s}',
    'bilibili': lambda s: f'https://www.bilibili.com/video/{s}/'
    }

niconico_meta_re = re.compile(r"<meta name=\"server-response\" content=\"([ -~]*?)\" \/>")
hashtag_re = re.compile(r'#(\w+)')

def get_niconico_geoblocked(sm):
    clean_url = make_video_url['niconico'](sm)
    r = requests.get(clean_url, headers={'User-Agent': 'Twitterbot/1.0', 'Accept-Language': 'ja'}, cookies=jar)
    if r.ok:
        res = json.loads(html.unescape(niconico_meta_re.search(r.text).group(1)))['data']['response']
        video = res['video']
        max_res = max(res['media']['domand']['videos'], key=lambda s: s['width'])
        return {
            'extractor': 'niconico',
            'title': video['title'],
            'description': video['description'],
            'tags': [x['name'] for x in res['tag']['items']],
            'width': max_res['width'],
            'height': max_res['height'],
            'duration': video['duration'],
            'webpage_url': clean_url,
            'id': video['id'],
            'thumbnail': video['thumbnail'].get('ogp', video['thumbnail']['url']),
            'timestamp': int(mktime(datetime.fromisoformat(video['registeredAt']).timetuple())),
            'uploader_id': res['owner']['id']
        }

def video_info(link):
    keys = {
            'extractor': 'site',
            'title': 'title',
            'description': 'description',
            'tags': 'tags',
            'width': 'work_width',
            'height': 'work_height',
            'duration': 'work_duration',
            'webpage_url': 'url',
            'id': 'id',
            'thumbnail': 'thumb',
            'timestamp':  'timestamp',
            'uploader_id': 'uploader_id',
        }
    try:
        if niconico_ie.suitable(link):
            info = get_niconico_geoblocked(niconico_ie.get_temp_id(link))
        else:
            info = ydl.extract_info(link, download=False)
            if info.get('_type') == 'playlist':
                info = info['entries'][0] # TODO need some work...
            resolutions = [(f['width'], f['height']) for f in info['formats'] if 'width' in f and f['width'] is not None]
            if resolutions:
                info['width'], info['height'] = max(resolutions, key=lambda s: s[0])

        info['extractor'] = Platform.from_str(info['extractor'])

        match info['extractor']:
            case Platform.YOUTUBE:
                info['webpage_url'] = make_video_url['youtube'](info['id'])
                info['tags'].extend(hashtag_re.findall(info['description']))
            case Platform.BILIBILI:
                chapter_mark = info['id'].find('_')
                if chapter_mark != -1:
                    info['id'] = info['id'][:chapter_mark]
                title_chapter_mark = info['title'].find(' p01') # TODO this is far from perfect
                if chapter_mark != -1:
                    info['title'] = info['title'][:title_chapter_mark]
                info['webpage_url'] = make_video_url['bilibili'](info['id'])
                info['tags'] = [tag[3:-1] if tag.startswith('发现《') and tag.endswith('》') else tag for tag in info['tags']]
            case Platform.NICONICO:
                info['webpage_url'] = make_video_url['niconico'](info['id'])
            case Platform.SOUNDCLOUD:
                pass # TODO
            case _:
                return None

        for c in ['?', '/']: # drop query strings and subdirectories
            i = info['id'].find(c)
            if i != -1:
                info['id'] = info['id'][:i]

        if 'tags' in info:
            info['tags'] = [NFKC(tag.replace(' ', '_')) for tag in info['tags']]

        info['description'] = nh3.clean(info['description'])

        return { keys[key]: info[key] for key in keys if key in info }
    except:
        return None

def playlist_info(link):
    keys = {
            'title': 'title',
            'description': 'description',
            'entries': 'entries',
        }
    info = ydl_playlist.extract_info(link, download=False)
    if info.get('_type') != 'playlist':
        return None

    match info['extractor_key']:
        case 'YoutubeTab':
            pass
        case 'NiconicoPlaylist':
            pass
        case 'BilibiliFavoritesList':
            pass
        # soundcloud?
        # a platform can also have multiple sorts of playlists that call different extractors
        # TODO fail for unsupported playlist types

    info['entries'] = [entry['url'] for entry in info['entries']]

    return { keys[key]: info[key] for key in keys if key in info }
