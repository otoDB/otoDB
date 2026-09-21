(async () => {
    const workingVideoId = 'sm1097445'; // Known working embed
    const workingEmbedUrl = `https://embed.nicovideo.jp/watch/${workingVideoId}`;
    const newVideoIdMatch = window.location.pathname.match(/\/watch\/([a-zA-Z]{2}\d+)/);

    if (newVideoIdMatch) {
        const newVideoId = newVideoIdMatch[1];
        window.otodb_video_id = newVideoId;
        window.otodb_video_id_numeric = newVideoId.replace(/[^0-9]/g, '');
    }

    try {
        const response = await fetch(workingEmbedUrl);
        if (!response.ok) {
            console.error('Could not fetch working embed page.');
            return;
        }

        const html = await response.text();
        const modifiedHtml = html.replace(/1:39/g, '?:??');
        const parser = new DOMParser();
        const doc = parser.parseFromString(modifiedHtml, 'text/html');

        const img = doc.querySelector('img[src*="//img.cdn.nimg.jp/s/nicovideo/thumbnails/"]');
        if (img) {
            img.src = `https://nicovideo.cdn.nimg.jp/thumbnails/${window.otodb_video_id_numeric}/${window.otodb_video_id_numeric}`;
        }
        const videoInfoEl = doc.getElementById('rootElementId')?.lastElementChild?.lastElementChild?.lastElementChild;
        if (videoInfoEl && videoInfoEl.querySelector('.shareButton')) {
            videoInfoEl.style.display = 'none';
        }

        document.open();
        document.write('<!DOCTYPE html>\n' + doc.documentElement.outerHTML);
        document.close();
    } catch (error) {
        console.error('Error replacing 403 embed page:', error);
    }
})();
