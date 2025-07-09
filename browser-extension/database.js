const OTODB_URL = `https://otodb.net`;

const getSiteInfo = (url) => {
	if (url.hostname.endsWith('youtube.com')) {
		const match = url.href.match(/v=([a-zA-Z0-9_-]{11})/);
		if (match) {
			return {
				platform: 'youtube',
				id: match[1]
			};
		}
	}
	else if (url.hostname.endsWith('bilibili.com')) {
		const match = url.href.match(/\/video\/(BV[a-zA-Z0-9]{10})\//);
		if (match) {
			return {
				platform: 'bilibili',
				id: match[1]
			};
		}
	}
	else if (url.hostname.endsWith('nicovideo.jp')) {
		const match = url.href.match(/\/watch\/([ns]m[0-9]+)/);
		if (match) {
			return {
				platform: 'niconico',
				id: match[1]
			};
		}
	}
	else if (url.hostname.endsWith('soundcloud.com')) {
		return {
			url: `${url.protocol}//${url.hostname}${url.pathname}`
		};
	}
};

const updateUI = (container, status) => {
    container.innerHTML = '';

    let mainLink = document.createElement('A');
    mainLink.innerText = "otoDB";
    mainLink.href = OTODB_URL;
    mainLink.target = '_blank';
    container.appendChild(mainLink);

    let statusElement = document.createElement('P');
    statusElement.innerText = status;
    container.appendChild(statusElement);

    return { mainLink, statusElement };
};

const displayResults = (container, work_id, tags, mainLink) => {
    const { statusElement } = updateUI(container, '');
    statusElement.remove();

    // Update main link to point to the work
    mainLink.innerText = "View this work on otoDB";
    mainLink.href = `${OTODB_URL}/work/${work_id}`;

    // Add tag links
    tags.forEach((tag) => {
        let tagLink = document.createElement('A');
        tagLink.innerText = tag.name;
        tagLink.href = `${OTODB_URL}/tag/${tag.slug}`;
        tagLink.target = '_blank';
        container.appendChild(tagLink);
    });
};

const displayNotFound = (container, currentUrl) => {
    const { statusElement } = updateUI(container, 'This work is not in the database.');

    let addLink = document.createElement('A');
    addLink.innerText = "Add this work to otoDB...";
    addLink.href = `${OTODB_URL}/work/add?${new URLSearchParams({ url: currentUrl })}`;
    addLink.target = '_blank';
    container.appendChild(addLink);
};

const init = async () => {
    const container = document.getElementById('otodb-tags');

    try {
        // Get current tab information
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        const siteInfo = getSiteInfo(new URL(tab.url));

        if (!siteInfo) {
            updateUI(container, 'This site is not supported.');
            return;
        }

        const { mainLink } = updateUI(container, 'Fetching...');

        const response = await fetch(`${OTODB_URL}/api/work/query_external?${new URLSearchParams(siteInfo)}`, {
            mode: 'cors'
        });

        if (response.ok) {
            const { work_id, tags } = await response.json();
            displayResults(container, work_id, tags, mainLink);
        }
        else if (response.status === 404) {
            displayNotFound(container, tab.url);
        }
        else {
            updateUI(container, 'Cannot reach the database.');
        }

    } catch (error) {
        console.error('Error:', error);
        updateUI(container, 'An error occurred while fetching data.');
    }
};

document.addEventListener('DOMContentLoaded', init);
