const RULE_ID = 2;

async function updateUserSessionRule() {
    try {
        const userSessionCookies = await chrome.cookies.getAll({
            url: 'https://www.nicovideo.jp'
        });

        const removeRuleIds = [RULE_ID];
        let addRules = [];

        if (userSessionCookies && userSessionCookies.length > 0) {
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
                    requestDomains: [
                        'api.nicovideo.jp',
                        'nvapi.nicovideo.jp',
                        'www.nicovideo.jp',
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
        console.debug('otoDB: DeclarativeNetRequest rules updated.');

    } catch (error) {
        console.error('otoDB Error: Failed to update niconico cookie rules:', error);
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
