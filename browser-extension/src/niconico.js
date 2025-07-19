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
        for (const [index, request] of pendingRequests.entries()) {
            try {
                const el = request.sensitiveEl;
                const data = await getServerResponseJson(request.url);
                if (data) {
                    const viewCount = data?.video?.count?.view || "-";
                    const commentCount = data?.video?.count?.comment || "0";
                    const mylistCount = data?.video?.count?.mylist || "0";
                    const likeCount = data?.video?.count?.like || "0";
                    const duration = data?.video?.duration || "0";
                    el.querySelector('.count.view .value').innerText = viewCount.toLocaleString();
                    el.querySelector('.count.comment .value').innerText = commentCount.toLocaleString();
                    el.querySelector('.count.mylist .value').innerText = mylistCount.toLocaleString();
                    el.querySelector('.count.like .value').innerText = likeCount.toLocaleString();
                    el.querySelector('.videoLength').innerText = new Date(duration * 1000).toISOString().substring(11, 19).replace(/^00:0?|^0/, '');
                }
            } catch (error) {
                console.error("Error processing server response request:", error);
                // If the first request is the one that failed, back off making any more requests
                if (index === 0) {
                    console.warn("First server response request failed, stopping further requests");
                    break;
                }
            }
        }
    }

    async function getServerResponseJson(url) {
        if (!url) return;
        const res = await fetch(url);
        const text = await res.text();
        const parser = new DOMParser();
        const htmlDoc = parser.parseFromString(text, 'text/html');
        const jsonStr = htmlDoc.querySelector('meta[name="server-response"]')?.content;
        if (!jsonStr) {
            throw new Error("No server response JSON found");
        }
        const payload = JSON.parse(jsonStr);
        const response = payload?.data?.response;
        const errorCode = response?.errorCode;
        if (errorCode && !response?.video && ["FORBIDDEN"].includes(errorCode.toUpperCase())) {
            throw new Error("Server response JSON indicates an error");
        }
        return response;
    }

    function replaceSensitiveEl(sensitiveItemEl, rssItem) {
        if (!sensitiveItemEl || !rssItem) return;

        sensitiveItemEl.removeAttribute('data-video-item-sensitive');
        sensitiveItemEl.setAttribute('data-video-item', '');
        sensitiveItemEl.setAttribute('data-video-id', rssItem.videoId);
        sensitiveItemEl.setAttribute('data-nicoad-video', '');
        sensitiveItemEl.setAttribute('data-nicoad-decorated', '1');

        const thumbBox = sensitiveItemEl.querySelector('img.thumb').closest('div');
        if (thumbBox) {
            const thumbWrap = document.createElement('div');
            thumbWrap.className = 'uadWrap';

            const itemThumbBox = document.createElement('div');
            itemThumbBox.className = 'itemThumbBox';

            const itemThumb = document.createElement('div');
            itemThumb.className = 'itemThumb';
            itemThumb.setAttribute('data-video-thumbnail', '');
            itemThumb.setAttribute('data-id', rssItem.videoId);

            const thumbLink = document.createElement('a');
            thumbLink.href = `/watch/${rssItem.videoId}`;
            thumbLink.className = 'itemThumbWrap';
            thumbLink.setAttribute('data-link', '');

            const thumbImg = document.createElement('img');
            thumbImg.className = 'thumb';
            thumbImg.src = rssItem.thumbnailUrl;
            thumbImg.alt = rssItem.title;
            thumbImg.setAttribute('data-thumbnail', '');
            thumbImg.setAttribute('decoding', 'async');
            thumbImg.setAttribute('loading', 'lazy');
            thumbImg.onerror = function() {
                if(this.src.endsWith('.M')) this.src = this.src.slice(0, -2);
            };

            const videoLength = document.createElement('span');
            videoLength.className = 'videoLength';
            videoLength.textContent = '-:--';

            const balloon = document.createElement('div');
            balloon.className = 'balloon recent active';
            balloon.setAttribute('data-message', '');
            balloon.style.display = 'none';

            thumbLink.appendChild(thumbImg);
            itemThumb.appendChild(thumbLink);
            itemThumbBox.appendChild(itemThumb);
            itemThumbBox.appendChild(videoLength);
            thumbWrap.appendChild(itemThumbBox);
            thumbWrap.appendChild(balloon);

            const existingTime = thumbBox.querySelector('.itemTime');
            const timeSpan = document.createElement('span');
            timeSpan.textContent = rssItem.pubDate.toLocaleString('ja-JP', {
                timeZone: 'Asia/Tokyo',
                year: 'numeric',
                month: 'numeric',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });

            const separateSpan = document.createElement('span');
            separateSpan.className = 'separate';
            separateSpan.textContent = '投稿';

            const videoUploadedSpan = document.createElement('span');
            videoUploadedSpan.className = 'video_uploaded';
            videoUploadedSpan.appendChild(timeSpan);
            videoUploadedSpan.appendChild(separateSpan);

            existingTime.innerHTML = '';
            existingTime.appendChild(videoUploadedSpan);

            thumbBox.innerHTML = '';
            thumbBox.appendChild(existingTime);
            thumbBox.appendChild(thumbWrap);
        }

        const contentBox = sensitiveItemEl.querySelector('.itemContent');
        if (contentBox) {
            contentBox.innerHTML = '';

            const titleP = document.createElement('p');
            titleP.className = 'itemTitle';

            const titleLink = document.createElement('a');
            titleLink.title = rssItem.title;
            titleLink.href = `/watch/${rssItem.videoId}`;
            titleLink.textContent = rssItem.title;

            titleP.appendChild(titleLink);

            const wrap = document.createElement('div');
            wrap.className = 'wrap';

            const descP = document.createElement('p');
            descP.title = rssItem.description;
            descP.className = 'itemDescription';
            descP.textContent = rssItem.description;

            wrap.appendChild(descP);

            const itemData = document.createElement('div');
            itemData.className = 'itemData';

            const list = document.createElement('ul');
            list.className = 'list';

            function createCountItem(className, label) {
                const li = document.createElement('li');
                li.className = `count ${className}`;
                li.textContent = label;

                const span = document.createElement('span');
                span.className = 'value';
                span.textContent = '-';

                li.appendChild(span);
                return li;
            }

            list.appendChild(createCountItem('view', '再生'));
            list.appendChild(createCountItem('comment', 'コメ'));
            list.appendChild(createCountItem('like', 'いいね！'));
            list.appendChild(createCountItem('mylist', 'マイ'));

            itemData.appendChild(list);

            contentBox.appendChild(titleP);
            contentBox.appendChild(wrap);
            contentBox.appendChild(itemData);
        }

        return sensitiveItemEl;
    }

    if (document.readyState === "complete" || document.readyState === "interactive")
        init();
    else
        document.addEventListener("DOMContentLoaded", init, false);
})();
