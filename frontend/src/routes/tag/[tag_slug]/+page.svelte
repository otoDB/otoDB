<script lang="ts">
	import Section from '$lib/Section.svelte';
	import { m } from '$lib/paraglide/messages.js';
	import {
		LanguageNames,
		Languages,
		ProfileConnectionLink,
		ProfileConnectionTypes,
		SongConnectionLink,
		SongConnectionTypes,
		MediaConnectionLink,
		MediaConnectionTypes,
		TagWorkConnectionLink,
		TagWorkConnectionTypes,
		WorkTagCategory
	} from '$lib/enums';
	import WorkCard from '$lib/WorkCard.svelte';
	import CommentTree from '$lib/CommentTree.svelte';
	import SongTag from '$lib/SongTag.svelte';
	import client, { getTagDisplayName, makeTagDisplayName } from '$lib/api.js';
	import { getLocale } from '$lib/paraglide/runtime.js';
	import LoadMoreButton from '$lib/LoadMoreButton.svelte';
	import { SVGViewer } from 'svelte-svg-viewer';
	import ConnectionFavicon from '$lib/ConnectionFavicon.svelte';
	import { SongRelationTypes } from '$lib/enums';
	import mermaid from 'mermaid';
	import { mermaid_BFS } from '$lib/ui.js';
	import { onMount } from 'svelte';
	import WorkTag from '$lib/WorkTag.svelte';

	let { data } = $props();
	let results = $derived(data.works!.items);

	const aliases = $derived(
		[data.tag.name, ...(data.aliases?.map((e) => e.name) ?? [])]
			.map(makeTagDisplayName)
			.filter((e) => e !== data.display_name)
	);

	let wikiView = $state(
		Languages[data.wiki_page?.find(({ lang }) => lang === Languages[getLocale()])?.lang] ??
			Languages[data.wiki_page?.at(0)?.lang] ??
			undefined
	);

	const fetchNextBatch = () =>
		client.GET('/api/tag/works', {
			fetch,
			params: {
				query: {
					tag_slug: data.tag.slug,
					limit: data.batch_size,
					offset: results.length
				}
			}
		});

	const ext_cat_types = $derived(
		data.tag.category === 6 ? MediaConnectionTypes : ProfileConnectionTypes
	);
	const ext_cat_links = $derived(
		data.tag.category === 6 ? MediaConnectionLink : ProfileConnectionLink
	);

	// Song Relation
	let songs = data.song_relations?.[1]?.map((o) => ({ visited: false, ...o }));
	let deg = $state(2);
	let direction = $state('LR');
	let allowed_types = $state(new Array(SongRelationTypes.length).fill(true));

	const get_svg_mermaid = (nodes, links) =>
		mermaid.render(
			'Relations',
			`flowchart ${direction}
    style ${data.tag.song!.id} color:#f00
${nodes
	.map(
		(w) => `${w.id}["${w.title.replaceAll('"', '#quot;')}"]
    click ${w.id} "${`/tag/${w.work_tag}`}"`
	)
	.join('\n')}
    ${links.map((r) => `${r.A_id} -->|${SongRelationTypes[r.relation]()}| ${r.B_id}`).join('\n')}`
		);

	let svg = $derived.by(() => {
		if (!songs?.length) return;
		const [nodes, links] = mermaid_BFS(
			structuredClone(songs),
			structuredClone(data.song_relations![0]),
			data.tag.song!.id,
			deg,
			allowed_types
		);
		return get_svg_mermaid(nodes, links);
	});

	onMount(() => {
		if (songs)
			mermaid.initialize({ maxTextSize: 1000000, startOnLoad: false, theme: 'neutral' });
	});
</script>

<Section
	title={m.mild_loud_shad_enchant({
		type: m.empty_legal_chicken_taste(),
		name: data.display_name
	})}
	menuLinks={data.links}
>
	<div>
		<span>{m.empty_legal_chicken_taste()}</span>
		{#each data.tree as node, i (i)}
			> <a href={node.slug}>{getTagDisplayName(node)}</a>&nbsp;
		{/each}
		>
		<span>{data.display_name}</span>
	</div>

	<h2>
		{m.mild_loud_shad_enchant({
			type: m.plane_awful_bobcat_spark(),
			name: WorkTagCategory[data.tag.category]()
		})}
	</h2>

	{#if aliases.length}
		<h3>
			{m.mild_loud_shad_enchant({
				type: m.tiny_sharp_lark_fall(),
				name: aliases?.join(', ')
			})}
		</h3>
	{/if}

	{#if data.tag.deprecated}
		<h2>This tag has been deprecated. It will not be displayed under works.</h2>
	{/if}

	{#if data.connections}
		<ul class="list-none">
			{#each data.connections[0] as s, i (i)}
				<li>
					<ConnectionFavicon
						type={TagWorkConnectionTypes[s.site]}
						class="inline size-4"
					/>
					<a
						href={TagWorkConnectionLink[s.site](s.content_id)}
						target="_blank"
						rel="noopener noreferrer"
					>
						{decodeURI(TagWorkConnectionLink[s.site](s.content_id))}
					</a>
				</li>
			{/each}
			{#if data.connections[1]}
				{#each data.connections[1] as s, i (i)}
					<li>
						<ConnectionFavicon type={ext_cat_types[s.site]} class="inline size-4" />
						<a
							href={ext_cat_links[s.site](s.content_id)}
							target="_blank"
							rel="noopener noreferrer"
						>
							{ext_cat_links[s.site](s.content_id)}
						</a>
					</li>
				{/each}
			{/if}
		</ul>
	{/if}

	<hr class="my-2" />

	{#if data.wiki_page && data.wiki_page.length}
		<div class="float-right clear-left my-2">
			{#each data.wiki_page as page, i (i)}
				<label class="wiki-lang-tab">
					<input type="radio" bind:group={wikiView} value={Languages[page.lang]} />
					{LanguageNames[Languages[page.lang]]}
				</label>
			{/each}
		</div>
		<div class="prose prose-neutral prose-sm dark:prose-invert max-w-4xl">
			{#if data.wiki_page?.find(({ lang }) => lang === Languages[wikiView])}
				<!-- eslint-disable-next-line svelte/no-at-html-tags -->
				{@html data.wiki_page?.find(({ lang }) => lang === Languages[wikiView])
					?.page_rendered}
			{/if}
		</div>
	{:else}
		<p>{m.tame_dirty_goldfish_flow()}</p>
	{/if}
</Section>

{#if data.tag.song}
	<Section
		title={m.mild_loud_shad_enchant({
			type: m.grand_nice_pony_belong(),
			name: data.tag.song.title
		})}
		menuLinks={data.song_links}
	>
		<table>
			<tbody>
				<tr><th>{m.large_factual_octopus_exhale()}</th><td>{data.tag.song.title}</td></tr>
				<tr
					><th>BPM</th><td
						>{#if data.tag.song.variable_bpm}{m.glad_fresh_thrush_hack({
								bpm: data.tag.song.bpm
							})}{:else}{data.tag.song.bpm}{/if}</td
					></tr
				>
				<tr><th>{m.crisp_red_canary_tickle()}</th><td>{data.tag.song.author}</td></tr>
			</tbody>
		</table>
		{#if data.song_connections}
			<ul class="list-none">
				{#each data.song_connections as s, i (i)}
					<li>
						<ConnectionFavicon
							type={SongConnectionTypes[s.site]}
							class="inline size-4"
						/>
						<a
							href={SongConnectionLink[s.site](s.content_id)}
							target="_blank"
							rel="noopener noreferrer"
						>
							{decodeURI(SongConnectionLink[s.site](s.content_id))}
						</a>
					</li>
				{/each}
			</ul>
		{/if}
		{#if data.tag?.song.tags.length}
			<ul id="song-tags">
				{#each data.tag?.song.tags as tag, i (i)}
					<li><SongTag {tag} /></li>
				{/each}
			</ul>
		{/if}
		{#if songs?.length}
			<label>
				{m.just_grassy_mantis_slurp()}
				<input type="number" bind:value={deg} min="1" />
			</label>
			<label>
				{m.fair_aware_salmon_twist()}
				<select bind:value={direction}
					><option value="LR">{m.top_front_ray_treasure()}</option><option value="TB"
						>{m.stout_jumpy_ox_feel()}</option
					></select
				>
			</label>
			{#each SongRelationTypes as t, i (i)}
				<label class="type-label">
					<input type="checkbox" class="hidden" bind:checked={allowed_types[i]} />
					{t()}
				</label>
			{/each}
			{#await svg}
				{m.sunny_light_duck_surge()}
			{:then s}
				<SVGViewer
					maxScale={90}
					height="200px"
					width="100%"
					svgClass="fill-transparent dark:fill-black"
				>
					<!-- eslint-disable-next-line svelte/no-at-html-tags -->
					{@html s.svg}
				</SVGViewer>
			{/await}
		{/if}
	</Section>
{/if}

{#if data.tag.children.length}
	<Section title={m.weird_nimble_fireant_climb()}>
		<div class="flex flex-wrap gap-3">
			{#each data.tag.children as tag, i (i)}
				<WorkTag {tag} />
			{/each}
		</div>
	</Section>
{/if}

<Section title={m.quiet_super_kangaroo_kiss({ tag: data.display_name })}>
	{#if results}
		<div class="grid grid-cols-[repeat(auto-fill,minmax(192px,1fr))] gap-x-4 gap-y-4">
			{#each results as work, i (i)}
				<WorkCard {work} />
			{/each}
		</div>
		<LoadMoreButton bind:results maxCount={data.works!.count} {fetchNextBatch} />
	{:else}
		<p>This tag is an orphan.</p>
	{/if}
</Section>

<Section title={m.same_broad_haddock_pinch()}>
	<CommentTree
		comments={data.comments}
		user={data.user ?? null}
		model="tagwork"
		pk={data.tag.id}
	/>
</Section>

<style>
	#song-tags {
		grid-column: 1 / span 2;
		border-top: var(--otodb-faint-content) 1px solid;
		margin-top: 1rem;
		padding-top: 1rem;
		display: flex;
		gap: 0.3rem 1rem;
		flex-wrap: wrap;
		list-style: none;
		& > li {
			margin: 0;
		}
	}
	label.wiki-lang-tab {
		padding: 0.2rem 0.5rem;
		display: inline-block;
		background-color: var(--otodb-bg-color);
		border: 1px solid var(--otodb-content-color);
		&:hover {
			background-color: var(--otodb-fainter-bg);
		}
		&:active {
			background-color: var(--otodb-faint-bg);
		}
		& > input {
			display: none;
		}
		&:has(> input:checked) {
			background-color: var(--otodb-content-color);
			border: 1px solid var(--otodb-bg-color);
			color: var(--otodb-bg-color);
		}
	}
	label.type-label {
		padding: 0 0.3rem;
		margin: 0.1rem;
		border: 1px solid var(--otodb-content-color);
		&:has(input:checked) {
			background-color: var(--otodb-content-color);
			color: var(--color-otodb-bg-color);
		}
		color: var(--otodb-content-color);
		background-color: var(--otodb-bg-color);
	}
</style>
