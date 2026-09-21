(function() {
	const SENSITIVE_KEYS = ['requireSensitiveMasking', 'sensitive'];
	const WORKING_EMBED_VIDEO_ID = 'sm1097445';

	const isEmbed = window.location.hostname === 'embed.nicovideo.jp';
	const originalJSONParse = JSON.parse;
	const originalFetch = window.fetch;

	let embedVideoId = null;
	let embedWatchData = null;

	function mentionsSensitive(text) {
		return typeof text === 'string' && SENSITIVE_KEYS.some(key => text.includes(`"${key}"`));
	}

	function uncensor(value) {
		if (typeof value !== 'object' || value === null) {
			return value;
		}
		for (const key of Object.keys(value)) {
			if (SENSITIVE_KEYS.includes(key) && typeof value[key] === 'boolean') {
				value[key] = false;
			} else {
				uncensor(value[key]);
			}
		}
		return value;
	}

	// Guests get 403 HARMFUL_VIDEO for age-gated videos, the logged in user does not
	function fetchWatchAsUser(url, init) {
		return originalFetch(
			// Bogus parameter to denote that this is a request from extension (see background.js)
			url + (url.includes('?') ? '&' : '?') + '_=1',
			{
				...init,
				body: JSON.stringify({ ...originalJSONParse(init.body), asGuest: false }),
				credentials: 'include'
			}
		);
	}

	JSON.parse = function(text, ...rest) {
		const result = originalJSONParse.call(this, text, ...rest);
		return mentionsSensitive(text) ? uncensor(result) : result;
	};

	const xhrUrls = new WeakMap();
	const originalXHROpen = XMLHttpRequest.prototype.open;
	const originalXHRSend = XMLHttpRequest.prototype.send;

	XMLHttpRequest.prototype.open = function(method, url, ...rest) {
		xhrUrls.set(this, String(url));
		return originalXHROpen.call(this, method, url, ...rest);
	};

	XMLHttpRequest.prototype.send = function(...args) {
		if (xhrUrls.get(this)?.includes('delivery.domand.nicovideo.jp')) {
			this.withCredentials = true;
		}
		return originalXHRSend.apply(this, args);
	};

	window.fetch = async function(...args) {
		const url = typeof args[0] === 'string' || args[0] instanceof URL ? String(args[0]) : '';

		if (embedVideoId) {
			// Before playing, the embed player asks whether the video may be embedded, which is always
			// refused for age-gated videos. Only the status of the response is looked at.
			if (url.match(/^(?:https?:)?\/\/embed\.nicovideo\.jp\/play\/([^/?]+)(\?|$)/)?.[1] === embedVideoId) {
				return new Response(null, { status: 200, statusText: 'OK' });
			}

			// The embed player fetches its watch data (which includes the HLS URL) and counts the view as a guest
			const watchMatch = url.match(/^https:\/\/nvapi\.nicovideo\.jp\/v4\/watch\/([^/?]+)(\/side-effect)?(\?|$)/);
			if (watchMatch?.[1] === embedVideoId) {
				const watch = embedWatchData;
				if (!watchMatch[2] && watch) {
					embedWatchData = null;
					if (watch.expiresAt > Date.now()) {
						return new Response(watch.json, {
							status: 200,
							statusText: 'OK',
							headers: { 'Content-Type': 'application/json' }
						});
					}
				}

				try {
					return fetchWatchAsUser(url, args[1]);
				} catch (e) {
					console.error('Error rewriting watch request:', e);
				}
				return originalFetch(...args);
			}
		}

		const response = await originalFetch(...args);
		if (response.ok && response.headers.get('Content-Type')?.split(';')[0] === 'application/json') {
			try {
				const text = await response.clone().text();
				if (mentionsSensitive(text)) {
					return new Response(JSON.stringify(uncensor(originalJSONParse(text))), {
						status: response.status,
						statusText: response.statusText,
						headers: response.headers
					});
				}
			} catch (e) {
				console.error('Error attempting to modify data in fetch():', e);
			}
		}
		return response;
	};

	async function replaceRefusedEmbed() {
		const videoId = window.location.pathname.match(/^\/watch\/([a-zA-Z]{2}\d+)/)?.[1];
		if (!videoId || !document.querySelector('script[src*="js/error_"]')) {
			return;
		}

		try {
			const response = await originalFetch(`https://embed.nicovideo.jp/watch/${WORKING_EMBED_VIDEO_ID}${window.location.search}`);
			if (!response.ok) {
				console.error('Could not fetch working embed page.');
				return;
			}

			const doc = new DOMParser().parseFromString(await response.text(), 'text/html');
			const player = doc.getElementById('ext-player');
			const props = originalJSONParse(player.dataset.props);

			const watchResponse = await fetchWatchAsUser(`https://nvapi.nicovideo.jp/v4/watch/${videoId}`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					'X-Frontend-Id': String(props.frontendId),
					'X-Frontend-Version': String(props.frontendVersion),
					'X-Request-With': window.location.origin
				},
				body: JSON.stringify({ actionTrackId: props.actionTrackId })
			});
			if (!watchResponse.ok) {
				console.error('Could not fetch watch data.');
				return;
			}
			const watchJson = await watchResponse.text();
			const { video, tags, media } = originalJSONParse(watchJson).data;

			// The player is rendered from these props alone
			Object.assign(props, {
				videoWatchId: videoId,
				videoId: video.id,
				title: video.title,
				description: video.description,
				thumbnailUrl: {
					normal: video.thumbnail.normal,
					ogp: video.thumbnail.ogp,
					listing: video.thumbnail.player || video.thumbnail.normal
				},
				firstRetrieve: Date.parse(video.registeredAt),
				lengthInSeconds: video.duration,
				viewCounter: video.count.view,
				mylistCounter: video.count.mylist,
				commentCounter: video.count.comment,
				tags: tags.items.map(tag => tag.name)
			});
			// Not included in the watch data
			delete props.videoUploaderId;

			player.dataset.props = JSON.stringify(props);
			// Drop the server-rendered markup of the working embed
			player.replaceChildren();
			doc.title = doc.title.replace(/^.*(?= - )/, () => video.title);

			embedVideoId = videoId;
			embedWatchData = { json: watchJson, expiresAt: Date.parse(media.hls.expiredAt) };

			document.open();
			document.write('<!DOCTYPE html>\n' + doc.documentElement.outerHTML);
			document.close();
		} catch (error) {
			console.error('Error replacing refused embed page:', error);
		}
	}

	if (isEmbed) {
		document.addEventListener('DOMContentLoaded', replaceRefusedEmbed, { once: true });
	}
})();
