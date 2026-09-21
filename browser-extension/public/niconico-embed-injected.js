(async () => {
    const workingVideoId = 'sm1097445'; // Known working embed
    const workingEmbedUrl = `https://embed.nicovideo.jp/watch/${workingVideoId}${window.location.search}`;
    const videoIdMatch = window.location.pathname.match(/\/watch\/([a-zA-Z]{2}\d+)/);
    if (!videoIdMatch) {
        return;
    }

    const videoId = window.otodb_video_id = videoIdMatch[1];

    try {
        const response = await fetch(workingEmbedUrl);
        if (!response.ok) {
            console.error('Could not fetch working embed page.');
            return;
        }

        const doc = new DOMParser().parseFromString(await response.text(), 'text/html');
        const player = doc.getElementById('ext-player');
        const props = JSON.parse(player.dataset.props);

        const watchResponse = await fetch(`https://nvapi.nicovideo.jp/v4/watch/${videoId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Frontend-Id': String(props.frontendId),
                'X-Frontend-Version': String(props.frontendVersion),
                'X-Request-With': window.location.origin,
            },
            body: JSON.stringify({ actionTrackId: props.actionTrackId, asGuest: false }),
        });
        if (!watchResponse.ok) {
            console.error('Could not fetch watch data.');
            return;
        }
        const { video, tags } = (await watchResponse.json()).data;

        // The player is rendered from these props alone
        Object.assign(props, {
            videoWatchId: videoId,
            videoId: video.id,
            title: video.title,
            description: video.description,
            thumbnailUrl: {
                normal: video.thumbnail.normal,
                ogp: video.thumbnail.ogp,
                listing: video.thumbnail.player || video.thumbnail.normal,
            },
            firstRetrieve: Date.parse(video.registeredAt),
            lengthInSeconds: video.duration,
            viewCounter: video.count.view,
            mylistCounter: video.count.mylist,
            commentCounter: video.count.comment,
            tags: tags.items.map(tag => tag.name),
        });
        // Not included in the watch data
        delete props.videoUploaderId;

        player.dataset.props = JSON.stringify(props);
        // Drop the server-rendered markup of the working embed
        player.replaceChildren();
        doc.title = doc.title.replace(/^.*(?= - )/, () => video.title);

        document.open();
        document.write('<!DOCTYPE html>\n' + doc.documentElement.outerHTML);
        document.close();
    } catch (error) {
        console.error('Error replacing 403 embed page:', error);
    }
})();
