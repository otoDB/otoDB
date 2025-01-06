const main = async inject => {
    const OTODB_URL = `http://127.0.0.1:8000`;

    // 1. temp interface
    let div = document.createElement('DIV'),
        title = document.createElement('H5'),
        status = document.createElement('P');
    title.innerText = 'otodb';
    status.innerText = 'Fetching...';
    div.style.border = '2px solid red';
    div.appendChild(title);
    div.appendChild(status);
    div.id = 'otodb-tags';
    inject(div);

    // 2. ping endpoint 
    const response = await fetch(`${OTODB_URL}/api/query_video?url=${encodeURIComponent(window.location)}`,
        { mode: 'cors' }
    );

    // 3. update interface with response
    if (response.ok) {
        status.remove();
        const { tags } = await response.json();
        tags.forEach(([tag, rel]) => {
            let a = document.createElement('A');
            a.innerText = tag;
            a.href = `${OTODB_URL}${rel}`;
            div.appendChild(a);
        });
    }
    else
        status.innerText = 'This work is not in the database.';
};

const init = () => {    
    if (window.location.hostname.endsWith('youtube.com')) {
        const observer = new MutationObserver((records, observer) => {
            let target = document.querySelector('ytd-watch-metadata #title');
            if (target) {
                main(node => target.insertAdjacentElement('afterend', node));
                observer.disconnect();
            }
        });
        observer.observe(document, { subtree: true, childList: true });
    }
    else if (window.location.hostname.endsWith('bilibili.com'))
        main(node => document.querySelector('.video-desc-container').insertAdjacentElement('afterend', node));
    else if (window.location.hostname.endsWith('nicovideo.jp')) {
        const observer = new MutationObserver((records, observer) => {
            let target = document.getElementsByClassName('grid-area_[meta]')[0]?.firstElementChild;
            if (target) {
                main(node => target.insertAdjacentElement('afterend', node));
                observer.disconnect();
            }
        });
        observer.observe(document, { subtree: true, childList: true });
    }
    else if (window.location.hostname.endsWith('soundcloud.com'))
        ;
};

if (document.readyState === "complete" || document.readyState === "interactive")
    init();
else
    document.addEventListener("DOMContentLoaded", init, false);
