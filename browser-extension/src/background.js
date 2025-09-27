const RULE_ID = 2;

async function updateUserSessionRule() {
	try {
		const userSessionCookies = await chrome.cookies.getAll({
			url: 'https://www.nicovideo.jp'
		});

		const removeRuleIds = [RULE_ID];
		let addRules = [];

		if (userSessionCookies.length > 0) {
			const cookieHeaderValue = userSessionCookies
				.map(cookie => `${cookie.name}=${cookie.value}`)
				.join('; ');

			addRules = [{
				id: RULE_ID,
				priority: 1,
				action: {
					type: 'modifyHeaders',
					requestHeaders: [{
						header: 'cookie',
						operation: 'set',
						value: cookieHeaderValue
					}]
				},
				condition: {
					// For nvapi.nicovideo.jp, require &_=1 at the end (which we inject) to add cookies; for others, allow anything.
					// This is because normally requests on the embed.nicovideo.jp domain expect no cookies to be used.
					// Adding cookies likely causes the JWT token or some other auth mechanism to fail.
					regexFilter: "^(https://nvapi\\.nicovideo\\.jp/.*&_\\=1$|https://(www|delivery\\.domand)\\.nicovideo\\.jp/.*$)",
					requestDomains: [
						'www.nicovideo.jp',
						'nvapi.nicovideo.jp',
						'delivery.domand.nicovideo.jp'
					],
					resourceTypes: ['xmlhttprequest', 'media']
				}
			}];
		}

		await chrome.declarativeNetRequest.updateDynamicRules({
			removeRuleIds,
			addRules
		});
		console.debug('DeclarativeNetRequest rules updated.');

	} catch (error) {
		console.error('Failed to update niconico cookie rules:', error);
	}
}

// Update rules on install, startup, and when the cookies change
chrome.runtime.onInstalled.addListener(updateUserSessionRule);
chrome.runtime.onStartup.addListener(updateUserSessionRule);
chrome.cookies.onChanged.addListener(changeInfo => {
	// If any cookie on nicovideo.jp changes, update the rule
	if (changeInfo.cookie.domain === '.nicovideo.jp') {
		updateUserSessionRule();
	}
});
