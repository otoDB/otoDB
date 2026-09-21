(function() {
    function tryUncensor(obj) {
        if (typeof obj !== 'object' || obj === null) {
            return obj;
        }

        if (Array.isArray(obj)) {
            return obj.map(item => tryUncensor(item));
        } else {
            const result = {};
            for (const key in obj) {
                if ((key === 'requireSensitiveMasking' || key === 'sensitive') && obj[key] instanceof Boolean) {
                    result[key] = false;
                } else {
                    result[key] = tryUncensor(obj[key]);
                }
            }
            return result;
        }
    }

    const originalJSONParse = JSON.parse;
    const originalFetch = window.fetch;
    const originalXMLHttpRequest = window.XMLHttpRequest;

    JSON.parse = function(...args) {
        let result = originalJSONParse.call(JSON, ...args);
        if (result && typeof result === 'object') {
            try {
                result = tryUncensor(result);
            } catch (e) {
                console.error("Error attempting to modify data in JSON.parse():", e);
            }
        }
        return result;
    };

    window.XMLHttpRequest = function() {
        const xhr = new originalXMLHttpRequest();
        const originalOpen = xhr.open;
        const originalSend = xhr.send;

        let targetUrl = '';

        xhr.open = function(method, url, ...args) {
            targetUrl = url;
            return originalOpen.call(this, method, url, ...args);
        };

        xhr.send = function(...args) {
            if (targetUrl && targetUrl.includes('delivery.domand.nicovideo.jp')) {
                this.withCredentials = true;
            }
            return originalSend.call(this, ...args);
        };

        return xhr;
    };

	window.fetch = async function(...args) {
		const url = typeof args[0] === 'string' || args[0] instanceof URL ? String(args[0]) : '';

		// Before playing, the embed player asks whether the video may be embedded, which is always
		// refused for age-gated videos. Only the status of the response is looked at.
		if (
			window.location.hostname === 'embed.nicovideo.jp' &&
			window.otodb_video_id &&
			url.match(/^(?:https?:)?\/\/embed\.nicovideo\.jp\/play\/([^/?]+)(\?|$)/)?.[1] === window.otodb_video_id
		) {
			return new Response(null, { status: 200, statusText: 'OK' });
		}

		// The embed player fetches its watch data (which includes the HLS URL) and counts the view
		// as a guest. Guests get 403 HARMFUL_VIDEO for age-gated videos, so for the video set by
		// niconico-embed-injected.js, make these requests as the logged in user instead.
		const watchMatch = url.match(/^https:\/\/nvapi\.nicovideo\.jp\/v4\/watch\/([^/?]+)(\/side-effect)?(\?|$)/);
		if (
			window.location.hostname === 'embed.nicovideo.jp' &&
			window.otodb_video_id &&
			watchMatch?.[1] === window.otodb_video_id
		) {
			// niconico-embed-injected.js already requested the watch data, use that the first time
			const watch = window.otodb_watch;
			if (!watchMatch[2] && watch) {
				delete window.otodb_watch;
				if (watch.expiresAt > Date.now()) {
					return new Response(watch.json, {
						status: 200,
						statusText: 'OK',
						headers: { 'Content-Type': 'application/json' }
					});
				}
			}

			try {
				const init = { ...args[1] };
				init.body = JSON.stringify({ ...originalJSONParse(init.body), asGuest: false });
				init.credentials = 'include';

				// Bogus parameter to denote that this is a request from extension
				return originalFetch(url + (url.includes('?') ? '&' : '?') + '_=1', init);
			} catch (e) {
				console.error("Error rewriting watch request:", e);
			}

			return originalFetch(...args);
		}

        const response = await originalFetch(...args);
        if (response.ok && response.headers.get('Content-Type')?.split(';')[0] === 'application/json') {
            const clonedResponseText = response.clone();
            const clonedResponseJson = response.clone();
            try {
                const text = await clonedResponseText.text();
                if (!text) {
                    return response;
                }
                const data = await clonedResponseJson.json();
                const result = tryUncensor(data);
                return new Response(JSON.stringify(result), {
                    status: response.status,
                    statusText: response.statusText,
                    headers: response.headers
                });
            } catch (e) {
                console.error("Error attempting to modify data in fetch():", e);
                const rawResponse = response.clone();
                const rawText = await rawResponse.text();
                console.error("Raw response body:", rawText);
            }
        }
        return response;
    };
})();
