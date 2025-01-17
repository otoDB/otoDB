import diff_match_patch as dmp_mod
from yt_dlp import YoutubeDL

from otodb.models import TagWork
from otodb.models.enums import Platform

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
                old, new = set([c['tagwork'] for c in change.old]), set([c['tagwork'] for c in change.new])
                old, new = old - new, new - old
                changes = ['- ' + str(TagWork.objects.get(id=id_)) for id_ in old] + ['+ ' + str(TagWork.objects.get(id=id_)) for id_ in new]
                diffs_html.append({'html': ('<br>').join(changes), 'field': change.field})
            case _:
                old, new = change.old, change.new
                diff_field = dmp.diff_main(str(old), str(new))
                dmp.diff_cleanupSemantic(diff_field)
                 
                diffs_html.append({'html': diff_prettyHtml(diff_field).replace('&para;', ''), 'field': change.field})

    return diffs_html

def video_info(link):
    keys = {
            'extractor': 'site',
            'title': 'title',
            'description': 'description',
            'tags': 'tags',
            'width': 'work_width',
            'height': 'work_height',
            'webpage_url': 'url',
            'id': 'id',
            'thumbnail': 'thumb',
            'timestamp':  'timestamp'
        }
    with YoutubeDL({'http_headers': {'Accept-Language': 'ja'}, 'noplaylist': True}) as ydl:
        info = ydl.extract_info(link, download=False)
        if info.get('_type') == 'playlist':
            info = info['entries'][0] # TODO need some work...

        info['extractor'] = Platform.from_str(info['extractor'])

        match info['extractor']:
            case Platform.YOUTUBE:
                info['webpage_url'] = f'https://youtu.be/{info['id']}'
            case Platform.BILIBILI:
                chapter_mark = info['id'].find('_')
                if chapter_mark != -1:
                    info['id'] = info['id'][:chapter_mark]
                title_chapter_mark = info['title'].find(' p01') # TODO this is far from perfect
                if chapter_mark != -1:
                    info['title'] = info['title'][:title_chapter_mark]
                info['webpage_url'] = f'https://www.bilibili.com/video/{info['id']}/'
                info['tags'] = [tag[3:-1] if tag.startswith('发现《') and tag.endswith('》') else tag for tag in info['tags']]
            case Platform.NICONICO:
                info['webpage_url'] = f'https://nicovideo.jp/watch/{info['id']}'
            case Platform.SOUNDCLOUD:
                pass # TODO
        
        for c in ['?', '/']: # drop query strings and subdirectories
            i = info['id'].find(c)
            if i != -1:
                info['id'] = info['id'][:i]

        return { keys[key]: info[key] for key in keys if key in info }


def playlist_info(link):
    keys = {
            'title': 'title',
            'description': 'description',
            'entries': 'entries',
        }
    with YoutubeDL({'http_headers': {'Accept-Language': 'ja'}, 'extract_flat': True}) as ydl:
        info = ydl.extract_info(link, download=False)
        if info.get('_type') != 'playlist':
            return None

        match info['extractor_key']:
            case 'YoutubeTab':
                pass
            case 'NiconicoPlaylist':
                pass
            case 'BilibiliFavoritesList':
                pass

        info['entries'] = [entry['url'] for entry in info['entries']]
        
        if info['description'] != '':
            info['description'] += '\n\n'
    
        info['description'] += f'Extracted from {info['webpage_url']}'

        return { keys[key]: info[key] for key in keys if key in info }
