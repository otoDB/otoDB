(function() {
    const errorScript = document.querySelector('script[src*="js/error_"]');
    if (!errorScript) {
        return;
    }

    // Runs in page context rather than extension context
    function inject() {
        (async () => {
            const workingVideoId = 'sm1097445'; // Known working embed
            const workingEmbedUrl = `https://embed.nicovideo.jp/watch/${workingVideoId}`;
            const oldVideoIdMatch = window.location.pathname.match(/\/watch\/(sm\d+)/);

            if (oldVideoIdMatch) {
                const oldVideoId = oldVideoIdMatch[1];
                window.otodb_video_id_map = {
                    old: oldVideoId,
                    new: workingVideoId
                };
            }

            try {
                const response = await fetch(workingEmbedUrl);
                if (!response.ok) {
                    console.error('Could not fetch working embed page.');
                    return;
                }

                const html = await response.text();

                document.open();
                document.write(html);
                document.close();
            } catch (error) {
                console.error('Error replacing 403 embed page:', error);
            }
        })();
    }

    const script = document.createElement('script');
    script.textContent = `(${inject.toString()})();`;
    (document.head || document.documentElement).appendChild(script);
    script.remove();
})();
