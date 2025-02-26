(function() {
    const rssVideoData = [];

    async function init() {
        const foundRssLink = document.querySelector('link[type="application/rss+xml"]')?.href;
        if (!foundRssLink) {
            console.warn('RSS link not found');
            return;
        }
        const rssLink = new URL(window.location.href);
        const params = rssLink.searchParams;
        params.append('rss', '2.0');

        const res = await fetch(rssLink.toString());
        if (!res.ok) {
            throw new Error(`Failed to fetch RSS: ${res.status} ${res.statusText}`);
        }
        const text = await res.text();
        const parser = new DOMParser();
        const xmlDoc = parser.parseFromString(text, 'application/xml');
        const parseError = xmlDoc.querySelector('parsererror');
        if (parseError) {
            throw new Error("XML parsing error: " + parseError.textContent);
        }

        Array.from(xmlDoc.querySelectorAll("item")).forEach((item) => {
            const title = item.querySelector("title")?.textContent || "";
            const link = item.querySelector("link")?.textContent?.split("?")[0] || "";
            const pubDate = (new Date(item.querySelector("pubDate")?.textContent));
          
            const descriptionEl = new DOMParser().parseFromString(item.querySelector("description")?.textContent || "", "text/html");
            let thumbnailUrl = descriptionEl.querySelector('.nico-thumbnail img')?.src || "";
            if (thumbnailUrl) {
                thumbnailUrl += ".M";
            }
            let description = descriptionEl.querySelector('.nico-description')?.textContent || "";
            if (description) {
                description = decodeURIComponent(description);
            }
            const info = descriptionEl.querySelector('.nico-info')?.textContent || "";
  
            const videoId = link.split("/").pop();
          
            rssVideoData.push({ videoId, title, link, pubDate, thumbnailUrl, description, info });
        });

        await setupMutationObserver();
    }

    async function setupMutationObserver() {
        const q = ".videoList ul[data-video-list] li.item";
        const observer = new MutationObserver(async _ => {
            const videoItemEls = document.querySelectorAll(q);
            if (videoItemEls.length > 0) {
                await processVideoItems(videoItemEls);
            }
        });
        observer.observe(document.body, { childList: true, subtree: true });
    }

    async function processVideoItems(videoItemEls) {
        if (!rssVideoData) return;
        let index = 0;
        const pendingRequests = [];
        for (const videoItemEl of videoItemEls) {
            if (videoItemEl.hasAttribute("data-video-item-sensitive")) {
                const rssItem = rssVideoData?.[index];
                const sensitiveEl = replaceSensitiveEl(videoItemEl, rssItem);
                pendingRequests.push({ sensitiveEl, url: videoItemEl.querySelector('a')?.href });
            }
            index++;
        }
        for (const request of pendingRequests) {
            try {
                const el = request.sensitiveEl;
                const data = await getServerResponseJson(request.url);
                if (data) {
                    const viewCount = data?.video?.count?.view || "-";
                    const commentCount = data?.video?.count?.comment || "0";
                    const mylistCount = data?.video?.count?.mylist || "0";
                    const likeCount = data?.video?.count?.like || "0";
                    const duration = data?.video?.duration || "--:--";
                    el.querySelector('.count.view .value').innerText = viewCount.toLocaleString();
                    el.querySelector('.count.comment .value').innerText = commentCount.toLocaleString();
                    el.querySelector('.count.mylist .value').innerText = mylistCount.toLocaleString();
                    el.querySelector('.count.like .value').innerText = likeCount.toLocaleString();
                    el.querySelector('.videoLength').innerText = new Date(duration * 1000).toISOString().substring(11, 19).replace(/^[0:]+/, '')
                }
            } catch (error) {
                console.error("Error processing server response request:", error);
            }
        }    
    }

    async function getServerResponseJson(url) {
        if (!url) return;
        const res = await fetch(url);
        if (!res.ok) {
            throw new Error(`Failed to fetch URL for server response: ${res.status} ${res.statusText}`);
        }
        const text = await res.text();
        const parser = new DOMParser();
        const htmlDoc = parser.parseFromString(text, 'text/html');
        const jsonStr = htmlDoc.querySelector('meta[name="server-response"]')?.content;
        if (!jsonStr) {
            throw new Error("No server response JSON found");
        }
        const data = JSON.parse(jsonStr);
        return data?.['data']?.['response'];
    }

    function replaceSensitiveEl(sensitiveItemEl, rssItem) {
        if (!sensitiveItemEl || !rssItem) return;

        sensitiveItemEl.removeAttribute('data-video-item-sensitive');
        sensitiveItemEl.setAttribute('data-video-item', '');
        sensitiveItemEl.setAttribute('data-video-id', rssItem.videoId);
        sensitiveItemEl.setAttribute('data-nicoad-video', '');
        sensitiveItemEl.setAttribute('data-nicoad-decorated', '1');

        const thumbBox = sensitiveItemEl.querySelector('.videoList01Wrap');
        if (thumbBox) {
            const thumbWrap = document.createElement('div');
            thumbWrap.className = 'uadWrap';
            thumbWrap.innerHTML = `
            <div class="itemThumbBox">
                <div class="itemThumb" data-video-thumbnail="" data-id="${rssItem.videoId}">
                    <a href="/watch/${rssItem.videoId}" class="itemThumbWrap" data-link="">
                        <img
                            class="thumb" src="${rssItem.thumbnailUrl}" alt="${rssItem.title}"
                            data-thumbnail="" decoding="async" loading="lazy"
                            onerror="if(this.src.endsWith('.M')) this.src = this.src.slice(0, -2);"
                        >
                    </a>
                </div>
                <span class="videoLength"></span>
            </div>
            <div class="balloon recent active" data-message="" style="display:none"></div>
            `;
            const existingTime = thumbBox.querySelector('.itemTime');
            thumbBox.innerHTML = '';
            thumbBox.appendChild(existingTime);
            thumbBox.appendChild(thumbWrap);
        }

        const contentBox = sensitiveItemEl.querySelector('.itemContent');
        if (contentBox) {
            contentBox.innerHTML = `
            <p class="itemTitle">
                <a title="${rssItem.title}" href="/watch/${rssItem.videoId}">${rssItem.title}</a>
            </p>
            <div class="wrap">
                <p title="${rssItem.description}" class="itemDescription">${rssItem.description}</p>
            </div>
            <div class="itemData">
                <ul class="list">
                    <li class="count view">再生<span class="value">-</span></li>
                    <li class="count comment">コメ<span class="value">-</span></li>
                    <li class="count like">いいね！<span class="value">-</span></li>
                    <li class="count mylist">マイ<span class="value">-</span></li>
                </ul>
            </div>
            `;
        }

        return sensitiveItemEl;
    }
    
    if (document.readyState === "complete" || document.readyState === "interactive")
        init();
    else
        document.addEventListener("DOMContentLoaded", init, false);
})();