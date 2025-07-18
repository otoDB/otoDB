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
		if (
			window.otodb_video_id_map &&
			typeof args[0] === 'string' &&
			args[0].match(/^https:\/\/nvapi\.nicovideo\.jp\/v1\/watch\/[^/]+\/access-rights\/hls/) &&
			window.location.hostname === 'embed.nicovideo.jp'
		) {
			let init = args[1] || {};
			let accessRightKey = '';

			if (init.headers) {
				let headersObj = init.headers instanceof Headers
					? init.headers
					: new Headers(init.headers);
				accessRightKey = headersObj.get('X-Access-Right-Key') || '';
			}

			init.headers = new Headers({
				'X-Frontend-Id': '6',
				'X-Frontend-Version': '0',
				'X-Niconico-Language': 'ja-jp',
				'X-Access-Right-Key': accessRightKey,
				'X-Request-With': 'nicovideo',
			});
			init.credentials = 'include';

			args[1] = init;

			return originalFetch(...args);
		}

        if (window.otodb_video_id_map && typeof args[0] === 'string') {
			const { old: oldId, new: newId } = window.otodb_video_id_map;
            const url = args[0];
            const watchApiRegex = /https:\/\/www\.nicovideo\.jp\/api\/watch\/v3_guest\/.+/;
            const match = url.match(watchApiRegex);

            if (match) {
                const embedUrl = `https://www.nicovideo.jp/watch/${oldId}`;
                try {
					const embedResponse = await originalFetch(embedUrl, ...args.slice(1));
                    if (!embedResponse.ok) {
						return originalFetch(...args);
                    }

                    const embedHtml = await embedResponse.text();
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(embedHtml, 'text/html');
                    const metaTag = doc.querySelector('meta[name="server-response"]');

                    if (metaTag) {
                        const serverResponseJson = metaTag.getAttribute('content');
						const responseData = originalJSONParse(serverResponseJson)?.data;
						const data = {
							meta: { status: 200 },
							data: responseData.response
						};
						return new Response(JSON.stringify(data), {
							status: 200,
							statusText: 'OK',
							headers: { 'Content-Type': 'application/json' }
						});
                    }
                } catch (e) {
                    console.error("Error fetching or parsing embed page:", e);
                }

				return originalFetch(...args);
            }
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
