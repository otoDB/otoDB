const OTODB_URL = `https://otodb.net`;

function getQuery(url) {
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
	else if (url.hostname.endsWith('twitter.com') || url.hostname.endsWith('x.com')) {
		const match = url.href.match(/status\/([0-9]+)/);
		if (match) {
			return {
				platform: 'twitter',
				id: match[1]
			};
		}
	}
	else if (url.hostname.endsWith('acfun.cn')) {
		const match = url.href.match(/\/v\/ac([\d_]+)/);
		if (match) {
			return {
				platform: 'acfun',
				id: match[1]
			};
		}
	}
    else if (url.hostname.endsWith('soundcloud.com')) {
        return {
            url: `${url.protocol}//${url.hostname}${url.pathname}`
        };
    }
}

const setStatus = (message) => {
    const statusElement = document.getElementById('status');
    statusElement.innerText = message;
};

const clearResults = () => {
    document.getElementById('results').innerHTML = '';
};

const displayResults = (work_id, tags) => {
    clearResults();
    setStatus('');

    const mainEl = document.getElementById('main');
    const resultsEl = document.getElementById('results');

    mainEl.innerText = "View on otoDB";
    mainEl.href = `${OTODB_URL}/work/${work_id}`;
	mainEl.target = "_blank";
	mainEl.rel = "noopener noreferrer";

    // Add tag links
    tags.forEach((tag) => {
        let tagLink = document.createElement('A');
        tagLink.innerText = tag.name;
        tagLink.href = `${OTODB_URL}/tag/${tag.slug}`;
		tagLink.target = "_blank";
		tagLink.rel = "noopener noreferrer";
		tagLink.classList.add(`tag-category-${tag.category}`);
        resultsEl.appendChild(tagLink);
    });
};

const displayNotFound = (currentUrl) => {
    clearResults();
    setStatus('This work is not in the database.');

    const resultsContainer = document.getElementById('results');
    let addLink = document.createElement('A');
    addLink.innerText = "Add this work to otoDB...";
    addLink.href = `${OTODB_URL}/work/add?${new URLSearchParams({ url: currentUrl })}`;
	addLink.target = "_blank";
	addLink.rel = "noopener noreferrer";
    resultsContainer.appendChild(addLink);
};

const init = async () => {
    try {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        const query = getQuery(new URL(tab.url));

        if (!query) {
            setStatus('This site is not supported.');
            return;
        }

        setStatus('Fetching...');

        const response = await fetch(`${OTODB_URL}/api/work/query_external?${new URLSearchParams(query)}`, {
            mode: 'cors'
        });

        if (response.ok) {
            const { work_id, tags } = await response.json();
            displayResults(work_id, tags);
        }
        else if (response.status === 404) {
            displayNotFound(tab.url);
        }
        else {
            setStatus('Cannot reach the database.');
        }

    } catch (error) {
        console.error('Error:', error);
        setStatus('An error occurred while fetching data.');
    }
};

document.addEventListener('DOMContentLoaded', init);
