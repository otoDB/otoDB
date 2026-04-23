<script lang="ts">
    import { onMount } from 'svelte';
    import { WorkTagCategoryMap } from '$lib/enums/workTagCategory';
    import { merge_paths } from '$lib/merge_paths';
    import { m } from '$lib/paraglide/messages';
    import { WorkTagCategory, type components } from '$lib/schema';
    import WorkTag from '$lib/WorkTag.svelte';
    import WorkTagTree from '$lib/WorkTagTree.svelte';

    type WorkTagInstance = components['schemas']['TagWorkInstanceSchema'];
    type ConnectionEntity = components['schemas']['ConnectionTagResult'];
    type Tag = WorkTagInstance | ConnectionEntity;

    const OTODB_API = 'https://otodb.net/api';
    const OTODB_WEB = 'https://otodb.net';

    type WorkQuery =
        | { platform: 'youtube' | 'bilibili' | 'niconico' | 'twitter' | 'acfun'; id: string }
        | { url: string };

    function getQuery(url: URL): WorkQuery | undefined {
        if (url.hostname.endsWith('youtube.com')) {
            const match = url.href.match(/v=([a-zA-Z0-9_-]{11})/);
            if (match) return { platform: 'youtube', id: match[1] };
        } else if (url.hostname.endsWith('bilibili.com')) {
            const match = url.href.match(/\/video\/(BV[a-zA-Z0-9]{10})\//);
            if (match) return { platform: 'bilibili', id: match[1] };
        } else if (url.hostname.endsWith('nicovideo.jp')) {
            const match = url.href.match(/\/watch\/([a-zA-Z]{2}[0-9]+)/);
            if (match) return { platform: 'niconico', id: match[1] };
        } else if (url.hostname.endsWith('twitter.com') || url.hostname.endsWith('x.com')) {
            const match = url.href.match(/status\/([0-9]+)/);
            if (match) return { platform: 'twitter', id: match[1] };
        } else if (url.hostname.endsWith('acfun.cn')) {
            const match = url.href.match(/\/v\/(ac[\d_]+)/);
            if (match) return { platform: 'acfun', id: match[1] };
        } else if (url.hostname.endsWith('soundcloud.com')) {
            return { url: `${url.protocol}//${url.hostname}${url.pathname}` };
        }
    }

    type State =
        | { kind: 'loading' }
        | { kind: 'status'; message: string }
        | { kind: 'work'; workId: number; tags: WorkTagInstance[] }
        | { kind: 'connection'; tags: ConnectionEntity[] }
        | { kind: 'notFound'; currentUrl: string };

    let view = $state<State>({ kind: 'loading' });
    let mainHref = $state(OTODB_WEB);
    let mainLabel: () => string = $state(() => 'otoDB');

    async function bootstrap() {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        if (!tab?.url) {
            view = { kind: 'status', message: m.grim_plain_crane_crash() };
            return;
        }

        const tabUrl = new URL(tab.url);
        const query = getQuery(tabUrl);

        view = { kind: 'status', message: m.calm_silver_bison_wait() };

        try {
            if (query) {
                const url = `${OTODB_API}/work/query_external?${new URLSearchParams(query as Record<string, string>)}`;
                const response = await window.fetch(url, { credentials: 'include' });
                if (response.ok) {
                    const data: components['schemas']['ExternalQuery'] = await response.json();
                    mainLabel = m.noisy_proud_robin_gaze;
                    mainHref = `${OTODB_WEB}/work/${data.work_id}`;
                    view = { kind: 'work', workId: data.work_id, tags: data.tags };
                } else if (response.status === 404) {
                    view = { kind: 'notFound', currentUrl: tab.url };
                } else {
                    view = { kind: 'status', message: m.weary_broken_eagle_sigh() };
                }
            } else {
                const url = `${OTODB_API}/tag/query_connection?${new URLSearchParams({ url: tab.url })}`;
                const response = await window.fetch(url, { credentials: 'include' });
                if (response.ok) {
                    const data: components['schemas']['ConnectionLookupResponse'] = await response.json();
                    view = { kind: 'connection', tags: data.entities };
                } else if (response.status === 404) {
                    view = { kind: 'status', message: m.quiet_dusty_fox_search() };
                } else {
                    view = { kind: 'status', message: m.weary_broken_eagle_sigh() };
                }
            }
        } catch (error) {
            console.error(error);
            view = { kind: 'status', message: m.grim_plain_crane_crash() };
        }
    }

    onMount(bootstrap);

    function groupAndSort(tags: Tag[]): [WorkTagCategory, Tag[]][] {
        return [
            ...Map.groupBy(tags, (t): WorkTagCategory => {
                const c = t.category;
                if (WorkTagCategoryMap[c].canSetAsSource && 'sample' in t && t.sample)
                    return WorkTagCategory.Source;
                return c;
            }).entries()
        ].toSorted(([a], [b]) => WorkTagCategoryMap[a].order - WorkTagCategoryMap[b].order);
    }

    const grouped: [WorkTagCategory, Tag[]][] = $derived(
        view.kind === 'work'
            ? groupAndSort(view.tags)
            : view.kind === 'connection'
                ? groupAndSort(view.tags)
                : []
    );

    const hasTreeData = $derived(
        (view.kind === 'work' || view.kind === 'connection') &&
            view.tags.some((t) => 'primary_path' in t && t.primary_path !== undefined)
    );
</script>

<div class="flex h-full w-full flex-col">
    <div
        class="border-otodb-content-faint flex shrink-0 items-center border-b p-4"
        style="background-color: var(--otodb-color-bg-primary)"
    >
        <a
            href={mainHref}
            target="_blank"
            rel="noopener noreferrer"
            class="flex items-center justify-center rounded-full bg-slate-500 px-4 py-1.5 text-[15px] font-medium text-white no-underline hover:opacity-80"
        >
            {mainLabel()}
        </a>
    </div>

    {#if view.kind === 'status'}
        <div
            class="shrink-0 p-4 text-center text-sm"
            style="color: var(--otodb-color-content-fainter)"
        >
            {view.message}
        </div>
    {/if}

    <div
        class="flex flex-1 flex-row flex-wrap content-start gap-x-3 overflow-y-auto p-4 text-[15px]"
    >
        {#if view.kind === 'notFound'}
            <div
                class="w-full shrink-0 pb-4 text-center text-sm"
                style="color: var(--otodb-color-content-fainter)"
            >
                {m.tiny_lost_marmot_roam()}
            </div>
            <a
                href={`${OTODB_WEB}/upload/add?${new URLSearchParams({ url: view.currentUrl })}`}
                target="_blank"
                rel="noopener noreferrer"
            >
                {m.merry_brisk_owl_submit()}
            </a>
        {:else if view.kind === 'work' || view.kind === 'connection'}
            {#each grouped as [category, tags] (category)}
                {@const color = WorkTagCategoryMap[category].color}
                <span
                    class="mt-4 border-l-2 px-3 pb-2"
                    style="border-color: {color}; background-color: color-mix(in hsl, {color}, transparent 85%)"
                >
                    <h5 class="my-2 font-bold">{WorkTagCategoryMap[category].nameFn()}</h5>
                    <ul class="flex list-none flex-wrap gap-2">
                        {#if hasTreeData}
                            {#each merge_paths(tags.map((t) => ({ ...t, primary_path: ('primary_path' in t ? t.primary_path : undefined) ?? [] }))) as tree, i (i)}
                                <li class="m-0">
                                    <WorkTagTree {tree} />
                                </li>
                            {/each}
                        {:else}
                            {#each tags as tag (tag.id)}
                                <li class="m-0">
                                    <WorkTag {tag} />
                                </li>
                            {/each}
                        {/if}
                    </ul>
                </span>
            {/each}
        {/if}
    </div>
</div>
