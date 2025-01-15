const main = async ({inject, div, div_ready}) => {
    const OTODB_URL = `http://127.0.0.1:8000`;

    // 1. temp interface
    if (!div) {
        div = document.createElement('DIV');
        div.style.border = '2px solid red';
        div.id = 'otodb-tags';
        inject(div);
    }
    else div.innerHTML = '';

    if (div_ready) div_ready(div)

    let link = document.createElement('A');
    link.innerText = "otoDB";
    link.href = `${OTODB_URL}`;
    div.appendChild(link);

    let status = document.createElement('P');
    status.innerText = 'Fetching...';
    div.appendChild(status);

    // 2. ping endpoint 
    const response = await fetch(`${OTODB_URL}/api/query_video?url=${encodeURIComponent(window.location)}`,
        { mode: 'cors' }
    ).catch(r => { status.innerText = 'Cannot reach the database.'; });

    // 3. update interface with response
    if (response.ok) {
        status.remove();
        const { tags, rel } = await response.json();
        tags.forEach(([tag, rel]) => {
            let a = document.createElement('A');
            a.innerText = tag;
            a.href = `${OTODB_URL}${rel}`;
            div.appendChild(a);
        });
        link.innerText = "View this work on otoDB"
        link.href = `${OTODB_URL}${rel}`
    }
    else if (response.status === 404) status.innerText = 'This work is not in the database.';
    else status.innerText = 'Cannot reach the database.';
};

const wait_for_target = (get_target, mutation_props, mutation_host = document) => new Promise(resolve => {
    let t = get_target([]);
    if (t) return resolve(t);

    const observer = new MutationObserver((records, observer) => {
        let target = get_target(records);
        if (target) {
            resolve(target);
            observer.disconnect();
        }
    });
    observer.observe(mutation_host , mutation_props);
});

const init = async () => {    
    if (window.location.hostname.endsWith('youtube.com')) {
        const target = await wait_for_target(records => document.querySelector('ytd-watch-metadata #title'), { subtree: true, childList: true });
        const div = await new Promise(resolve => main({ inject: node => target.insertAdjacentElement('afterend', node), div: null, div_ready: resolve }));
        const spa_target = await wait_for_target(records => document.querySelector('#movie_player video'), { subtree: true, childList: true });

        while (true) {
            await wait_for_target(records => records.some(record => record.type === 'attributes' && record.attributeName === 'src'), { attributes: true }, spa_target);
            main({div: div});
        }
    }
    else if (window.location.hostname.endsWith('bilibili.com'))
        main({ inject: node => document.querySelector('.video-desc-container').insertAdjacentElement('afterend', node), div: null });
    else if (window.location.hostname.endsWith('nicovideo.jp')) {
        const target = await wait_for_target(records => document.getElementsByClassName('grid-area_[meta]')[0]?.firstElementChild, { subtree: true, childList: true });
        const div = await new Promise(resolve => main({ inject: node => target.insertAdjacentElement('afterend', node), div: null, div_ready: resolve }));
        const spa_target = await wait_for_target(records => document.querySelector('video'), { subtree: true, childList: true });

        while (true) {
            await wait_for_target(records => records.some(record => record.type === 'attributes' && record.attributeName === 'src'), { attributes: true }, spa_target);
            main({div: div});
        }
    }
    else if (window.location.hostname.endsWith('soundcloud.com'))
        ; // TODO
};

if (document.readyState === "complete" || document.readyState === "interactive")
    init();
else
    document.addEventListener("DOMContentLoaded", init, false);
