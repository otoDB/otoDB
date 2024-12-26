from yt_dlp import YoutubeDL

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
    with YoutubeDL({'http_headers': {'Accept-Language': 'ja'}}) as ydl:
        info = ydl.extract_info(link, download=False)
        if info.get('_type') == 'playlist':
            info = info['entries'][0] # todo need some work...
        info['extractor'] = info['extractor'].lower()
        if info['extractor'] == 'bilibili':
            info['tags'] = [tag[3:-1] if tag.startswith('发现《') and tag.endswith('》') else tag for tag in info['tags']]
        match info['extractor']:
            case 'youtube':
                info['webpage_url'] = f'https://youtu.be/{info['id']}'
            case 'bilibili':
                info['webpage_url'] = f'https://bilibili.com/video/{info['id']}/'
            case 'niconico':
                info['webpage_url'] = f'https://nicovideo.jp/watch/{info['id']}'
            case 'soundcloud':
                pass

        return { keys[key]: info[key] for key in keys if key in info }
