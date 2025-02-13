const main = async ({inject, div, div_ready, query}) => {
    const OTODB_URL = `http://127.0.0.1:8000`;

    // 1. temp interface
    if (!div) {
        div = document.createElement('DIV');
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
    const response = await fetch(`${OTODB_URL}/api/query_video?${new URLSearchParams(query)}`,
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
    else if (response.status === 404) {
        status.innerText = 'This work is not in the database.';
        let add = document.createElement('A');
        add.innerText = "Add this work to otoDB...";
        add.href = `${OTODB_URL}/works/new?${new URLSearchParams({ url: window.location.toString() })}`;
        div.appendChild(add);    
    }
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
        const get_query = () => ({
            platform: 'youtube',
            id: window.location.toString().match(/v=([a-zA-Z0-9_-]{11})/)[1]
        });

        const target = await wait_for_target(records => document.querySelector('ytd-watch-metadata #top-row'), { subtree: true, childList: true });
        const div = await new Promise(resolve => main({
            div_ready: resolve,
            inject: node => target.insertAdjacentElement('afterend', node),
            div: null,
            query: get_query(),
        }));
        const spa_target = await wait_for_target(records => document.querySelector('#movie_player video'), { subtree: true, childList: true });

        while (true) {
            await wait_for_target(records => records.some(record => record.type === 'attributes' && record.attributeName === 'src'), { attributes: true }, spa_target);
            main({
                div: div,
                query: get_query(),
            });
        }
    }
    else if (window.location.hostname.endsWith('bilibili.com')) {
        const get_query = () => ({
            platform: 'bilibili',
            id: window.location.toString().match(/\/video\/(BV[a-zA-Z0-9]{10})\//)[1]
        });
        const get_div = () => new Promise(resolve => main({
            div_ready: resolve,
            // We put it outside #app -- the reactive (meta)-framework used fails if we insert unexpected nodes inside #app
            inject: node => document.querySelector('#app').insertAdjacentElement('afterend', node),
            div: null,
            query: get_query(),
        })), set_style = div => {
            // TODO this is not ideal...
            div.style.position = 'fixed';
            div.style.bottom = 0;
            div.style.zIndex = 1;
        };

        let div = await get_div();
        set_style(div);
        const spa_target = await wait_for_target(records => document.querySelector('video'), { subtree: true, childList: true });

        while (true) {
            await wait_for_target(records => records.some(record => record.type === 'attributes' && record.attributeName === 'src'), { attributes: true }, spa_target);
            div.remove();
            div = await get_div();
            set_style(div);
        }
    }
    else if (window.location.hostname.endsWith('nicovideo.jp')) {
        const get_query = () => ({
            platform: 'niconico',
            id: window.location.toString().match(/\/watch\/(sm[0-9]+)/)[1]
        });

        const target = await wait_for_target(records => document.getElementsByClassName('grid-area_[meta]')[0]?.firstElementChild, { subtree: true, childList: true });
        const div = await new Promise(resolve => main({
            div_ready: resolve,
            inject: node => target.insertAdjacentElement('afterend', node),
            div: null,
            query: get_query(),
        }));
        
        while (true) {
            const spa_target = await wait_for_target(records => document.querySelector('video'), { subtree: true, childList: true });
            await wait_for_target(records => records.some(record => record.type === 'attributes' && record.attributeName === 'src'), { attributes: true }, spa_target);
            main({
                div: div,
                query: get_query(),
            });
        }
    }
    else if (window.location.hostname.endsWith('soundcloud.com'))
        ; // TODO
};

if (document.readyState === "complete" || document.readyState === "interactive")
    init();
else
    document.addEventListener("DOMContentLoaded", init, false);
