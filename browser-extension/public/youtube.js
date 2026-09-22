// Restore classic YouTube embed player.
// rules.json swaps the embed's two bundles for the classic ones:
//   /s/player/<hash>/player_embed_es6.vflset/* -> /s/player/<hash>/player_es6.vflset/*
//   /s/_/ytembeds/_/js/*                       -> /s/embeds/7c0ed1a1/www-embed-player-es6.vflset/www-embed-player-es6.js
// 7c0ed1a1 is a pinned build. If that URL ever stops resolving, replace it with the hash the embed page
// itself still uses for /s/embeds/<hash>/lottie-light.vflset/lottie-light.js.

(function() {
	'use strict';

	function patch(config) {
		const context = config.WEB_PLAYER_CONTEXT_CONFIGS?.WEB_PLAYER_CONTEXT_CONFIG_ID_EMBEDDED_PLAYER;
		if (context) {
			context.disableOrganicUi = false;
			context.embedsEnableEmc3ds = false;
			context.storeUserVolume = false;
		}

		// Play embed disabled videos
		try {
			const response = JSON.parse(config.PLAYER_VARS.embedded_player_response);
			const status = response.previewPlayabilityStatus;
			if (status && status.status !== 'OK') {
				// Pre-rendered verdict, which is checked before the player is even started
				status.status = 'OK';
				status.playableInEmbed = true;
				delete status.reason;
				delete status.errorScreen;
				config.PLAYER_VARS.embedded_player_response = JSON.stringify(response);
				config.INNERTUBE_CONTEXT.client.clientName = 'WEB';
			}
		} catch (e) {
			// pass
		}
	}

	let ytcfg;
	Object.defineProperty(window, 'ytcfg', {
		configurable: true,
		enumerable: true,
		get: () => ytcfg,
		set(value) {
			ytcfg = value;
			const originalSet = value?.set;
			if (typeof originalSet === 'function') {
				value.set = function(...args) {
					if (args.length === 1 && typeof args[0] === 'object' && args[0] !== null) {
						patch(args[0]);
					}
					return originalSet.apply(this, args);
				};
			}
		}
	});
})();
