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
        return {keys[key]: info[key] for key in keys.keys() if key in info}
