const OTODB_WEB = `https://otodb.net`;
const OTODB_API = `https://otodb.net/api`;

const Languages = { en: 1, ja: 2, 'zh-cn': 3, ko: 4 };
// TODO: Handle this more like the frontend
const i18n = {
    en: {
        category: ['General', 'Event', 'Song', 'Source', 'Creator', 'Meta', 'Media'],
        role: { 1: 'Audio', 2: 'Visuals', 4: 'Director', 8: 'Music', 16: 'Artwork', 32: 'Special Thanks' },
        viewOnOtodb: 'View on otoDB',
        fetching: 'Fetching...',
        notFound: 'This work is not in the database.',
        addWork: 'Add this work to otoDB...',
        noConnection: 'No connections found for this page.',
        unreachable: 'Cannot reach the database.',
        error: 'An error occurred while fetching data.',
    },
    ja: {
        category: ['一般的', 'イベント', '曲', '素材', '作者', 'メタ', 'メディア'],
        role: { 1: '音声', 2: '映像', 4: '監督', 8: '音楽', 16: 'イラスト', 32: '特別な感謝' },
        viewOnOtodb: 'otoDBで見る',
        fetching: '読み込み中...',
        notFound: 'この作品はデータベースにありません。',
        addWork: 'この作品をotoDBに登録する...',
        noConnection: 'このページに接続が見つかりませんでした。',
        unreachable: 'データベースに接続できません。',
        error: 'データの取得中にエラーが発生しました。',
    },
    ko: {
        category: ['일반', '이벤트', '곡', '소재', '크리에이터', '메타', '미디어'],
        role: { 1: '음성', 2: '영상', 4: '감독', 8: '음악', 16: '작품', 32: '특별한 감사' },
        viewOnOtodb: 'otoDB에서 보기',
        fetching: '불러오는 중...',
        notFound: '이 작품은 데이터베이스에 없습니다.',
        addWork: '이 작품을 otoDB에 추가...',
        noConnection: '이 페이지에 대한 연결을 찾을 수 없습니다.',
        unreachable: '데이터베이스에 연결할 수 없습니다.',
        error: '데이터를 가져오는 중 오류가 발생했습니다.',
    },
    'zh-cn': {
        category: ['一般', '活动', '曲', '素材', '作者', '元属性', '媒体'],
        role: { 1: '音频', 2: '视频', 4: '导演', 8: '音乐', 16: '绘画', 32: '特别感谢' },
        viewOnOtodb: '在otoDB上查看',
        fetching: '加载中...',
        notFound: '该作品不在数据库中。',
        addWork: '将此作品添加到otoDB...',
        noConnection: '未找到此页面的连接。',
        unreachable: '无法连接到数据库。',
        error: '获取数据时发生错误。',
    },
};


let uiLang = 'en';
const t = (key) => (i18n[uiLang] ?? i18n.en)[key] ?? i18n.en[key];

const WorkTagPresentationOrder = [1, 4, 6, 3, 2, 0, 5];
const WorkTagCategoriesSettableAsSource = [2, 4, 6];
const WorkTagPresentationColours = [
    'rgb(159,163,169)',
    'rgb(8,145,178)',
    'rgb(232,121,249)',
    'rgb(101,163,13)',
    'rgb(220,38,38)',
    'rgb(251,191,36)',
    'rgb(112,26,117)',
];

// TODO: Revisit setHTML when more widely supported
function safeSetHTML(el, html) {
    // if (el.setHTML) {
    //     el.setHTML(html);
    // } else {
        el.innerHTML = DOMPurify.sanitize(html, { ADD_ATTR: ['target'] });
    // }
}

function safeAppendHTML(el, html) {
    const temp = document.createElement('div');
    safeSetHTML(temp, html);
    el.append(...temp.childNodes);
}

async function getPreferredLang() {
    const langs = await chrome.i18n.getAcceptLanguages();
    for (const l of langs) {
        const key = l.toLowerCase();
        if (Languages[key] !== undefined) return { lang: Languages[key], uiLang: key };
        const base = key.split('-')[0];
        if (Languages[base] !== undefined) return { lang: Languages[base], uiLang: base };
    }
    return { lang: null, uiLang: 'en' };
}

const makeTagDisplayName = (name) => name.replaceAll('_', ' ');
const getTagDisplayName = (tag, lang) =>
    makeTagDisplayName(
        tag.lang_prefs?.find(p => p.lang === lang)?.tag ?? tag.name
    );
const getTagDisplaySlug = (tag, lang) =>
    tag.lang_prefs?.find(p => p.lang === lang)?.slug ?? tag.slug;

function merge_paths(tags) {
    const graph = new Map();
    tags
        .filter(p => p.primary_path?.length)
        .forEach(path =>
            path.primary_path.forEach((p, i, a) => {
                const nextNode = (i + 1 === a.length ? path : a[i + 1]).slug;
                if (graph.has(p.slug)) graph.get(p.slug).add(nextNode);
                else graph.set(p.slug, new Set([nextNode]));
            })
        );
    const allNodes = [...tags, ...tags.flatMap(p => p.primary_path || [])];
    const traverse = (node) => ({
        node: allNodes.find(n => n.slug === node),
        real: tags.some(n => n.slug === node),
        children: Array.from(graph.get(node) ?? []).map(n => traverse(n))
    });
    return [
        ...Array.from(graph.keys())
            .filter(n => !Array.from(graph.values()).some(s => s.has(n)))
            .map(traverse),
        ...tags
            .filter(p => !p.primary_path?.length && !graph.has(p.slug))
            .map(n => ({ node: n, real: true }))
    ];
}

function getQuery(url) {
    if (url.hostname.endsWith('youtube.com')) {
        const match = url.href.match(/v=([a-zA-Z0-9_-]{11})/);
        if (match) {
            return { platform: 'youtube', id: match[1] };
        }
    }
    else if (url.hostname.endsWith('bilibili.com')) {
        const match = url.href.match(/\/video\/(BV[a-zA-Z0-9]{10})\//);
        if (match) {
            return { platform: 'bilibili', id: match[1] };
        }
    }
    else if (url.hostname.endsWith('nicovideo.jp')) {
        const match = url.href.match(/\/watch\/([ns]m[0-9]+)/);
        if (match) {
            return { platform: 'niconico', id: match[1] };
        }
    }
    else if (url.hostname.endsWith('twitter.com') || url.hostname.endsWith('x.com')) {
        const match = url.href.match(/status\/([0-9]+)/);
        if (match) {
            return { platform: 'twitter', id: match[1] };
        }
    }
    else if (url.hostname.endsWith('acfun.cn')) {
        const match = url.href.match(/\/v\/(ac[\d_]+)/);
        if (match) {
            return { platform: 'acfun', id: match[1] };
        }
    }
    else if (url.hostname.endsWith('soundcloud.com')) {
        return { url: `${url.protocol}//${url.hostname}${url.pathname}` };
    }
}

const setStatus = (message) => {
    document.getElementById('status').textContent = message;
};

const clearResults = () => {
    document.getElementById('results').replaceChildren();
};

function render_tag(entity, lang, { border = true, sampleOverride = false, fadeOut = false } = {}) {
    const colorCat = sampleOverride ? 3 : entity.category;
    const color = WorkTagPresentationColours[colorCat];
    const name = entity.song_title || getTagDisplayName(entity, lang);
    const slug = getTagDisplaySlug(entity, lang);
    const classes = [
        'rounded-xl border-solid px-2',
        border ? 'border-2' : 'border',
        fadeOut && 'opacity-50',
        entity.has_connection === false && 'name-match',
    ].filter(Boolean).join(' ');

    const roleMap = t('role');
    const rolesHtml = (entity.category === 4 && entity.creator_roles?.length)
        ? `<address class="text-otodb-content-fainter inline px-1 text-xs">${entity.creator_roles.map(r => roleMap[r] || r).join(',\u00a0')}</address>`
        : '';

    return `<a href="${OTODB_WEB}/tag/${slug}" target="_blank" rel="noopener noreferrer" class="${classes}" style="border-color: ${color}">${name}</a>${rolesHtml}`;
}

function render_tree(treeNode, lang) {
    const isSample = WorkTagCategoriesSettableAsSource.includes(treeNode.node.category) && treeNode.node.sample;
    const tagHtml = render_tag(treeNode.node, lang, {
        border: false,
        fadeOut: !treeNode.real,
        sampleOverride: isSample,
    });

    const childrenHtml = (treeNode.children || [])
        .map(child => `<li>${render_tree(child, lang)}</li>`)
        .join('');

    return `<ul class="tag-tree my-0.5 list-none"><li class="inline">${tagHtml}</li>${childrenHtml}</ul>`;
}

const render_tag_groups = (resultsEl, entities, lang) => {
    const hasTreeData = entities.some(e => e.primary_path !== undefined);
    const categoryNames = t('category');

    // Group by category, with sample override
    const groups = {};
    for (const entity of entities) {
        const cat = (hasTreeData && WorkTagCategoriesSettableAsSource.includes(entity.category) && entity.sample)
            ? 3 : entity.category;
        if (!groups[cat]) groups[cat] = [];
        groups[cat].push(entity);
    }

    // Sort by presentation order
    const sortedCats = Object.keys(groups).sort((a, b) => {
        const ai = WorkTagPresentationOrder.indexOf(+a);
        const bi = WorkTagPresentationOrder.indexOf(+b);
        return (ai === -1 ? 999 : ai) - (bi === -1 ? 999 : bi);
    });

    let html = '';
    for (const cat of sortedCats) {
        const color = WorkTagPresentationColours[cat];
        const categoryName = categoryNames[cat] || 'Other';

        let itemsHtml;
        if (hasTreeData) {
            const trees = merge_paths(groups[cat]);
            itemsHtml = trees.map(tree => `<li class="m-0">${render_tree(tree, lang)}</li>`).join('');
        } else {
            itemsHtml = groups[cat].map(entity => `<li class="m-0">${render_tag(entity, lang)}</li>`).join('');
        }

        html += `<span class="mt-4 border-l-2 px-3 pb-2" style="border-color: ${color}; background-color: color-mix(in hsl, ${color}, transparent 85%)">
            <h5 class="my-2 font-bold">${categoryName}</h5>
            <ul class="flex list-none flex-wrap gap-2">${itemsHtml}</ul>
        </span>`;
    }

    safeAppendHTML(resultsEl, html);
};

const displayResults = (work_id, tags, lang) => {
    clearResults();
    setStatus('');

    const mainEl = document.getElementById('main');
    mainEl.textContent = t('viewOnOtodb');
    mainEl.href = `${OTODB_WEB}/work/${work_id}`;
    mainEl.target = "_blank";
    mainEl.rel = "noopener noreferrer";

    render_tag_groups(document.getElementById('results'), tags, lang);
};

const displayConnectionResults = (data, lang) => {
    clearResults();
    setStatus('');

    const mainEl = document.getElementById('main');
    mainEl.textContent = "otoDB";
    mainEl.href = OTODB_WEB;
    mainEl.target = "_blank";
    mainEl.rel = "noopener noreferrer";

    render_tag_groups(document.getElementById('results'), data.entities, lang);
};

const displayNotFound = (currentUrl) => {
    clearResults();
    setStatus(t('notFound'));

    const url = `${OTODB_WEB}/work/add?${new URLSearchParams({ url: currentUrl })}`;
    safeAppendHTML(
        document.getElementById('results'),
        `<a href="${url}" target="_blank" rel="noopener noreferrer">${t('addWork')}</a>`
    );
};

const init = async () => {
    try {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        const preferred = await getPreferredLang();
        const lang = preferred.lang;
        uiLang = preferred.uiLang;
        const query = getQuery(new URL(tab.url));

        if (query) {
            // Work platform lookup
            setStatus(t('fetching'));

            const response = await fetch(`${OTODB_API}/work/query_external?${new URLSearchParams(query)}`, {
                mode: 'cors'
            });

            if (response.ok) {
                const { work_id, tags } = await response.json();
                displayResults(work_id, tags, lang);
            }
            else if (response.status === 404) {
                displayNotFound(tab.url);
            }
            else {
                setStatus(t('unreachable'));
            }
        } else {
            // Connection URL lookup
            setStatus(t('fetching'));

            const response = await fetch(`${OTODB_API}/tag/query_connection?${new URLSearchParams({ url: tab.url })}`, {
                mode: 'cors'
            });

            if (response.ok) {
                const data = await response.json();
                displayConnectionResults(data, lang);
            }
            else if (response.status === 404) {
                setStatus(t('noConnection'));
            }
            else {
                setStatus(t('unreachable'));
            }
        }

    } catch (error) {
        console.error('Error:', error);
        setStatus(t('error'));
    }
};

document.addEventListener('DOMContentLoaded', init);
