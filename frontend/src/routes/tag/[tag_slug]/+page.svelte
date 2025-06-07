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
		SourceConnectionLink,
		SourceConnectionTypes,
		TagWorkConnectionLink,
		TagWorkConnectionTypes,
		WorkTagCategory
	} from '$lib/enums';
	import WorkCard from '$lib/WorkCard.svelte';
	import CommentTree from '$lib/CommentTree.svelte';
	import SongTag from '$lib/SongTag.svelte';
	import client from '$lib/api.js';
	import { getLocale } from '$lib/paraglide/runtime.js';

	let { data } = $props();
	let results = $derived(data.works!.items);
	const aliases = $derived(
		data.display_name === data.tag.name
			? data.aliases?.map((a) => a.name)
			: [
					data.tag.name,
					...(data.aliases
						?.filter((a) => a.name !== data.display_name)
						.map((a) => a.name) ?? [])
				]
	);
	let wikiView = $state(
		Languages[data.wiki_page?.find(({ lang }) => lang === Languages[getLocale()])?.lang] ??
			Languages[data.wiki_page?.at(0)?.lang] ??
			undefined
	);

	let fetching = $state(false);
	const getNextBatch = async () => {
		fetching = true;
		const { data: d } = await client.GET('/api/tag/works', {
			fetch,
			params: {
				query: {
					tag_slug: data.tag.slug,
					limit: data.batch_size,
					offset: results.length
				}
			}
		});
		results = results.concat(d!.items);
		fetching = false;
	};
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
			> <a href={node.slug}>{node.name}</a> >
		{:else}
			>
		{/each}
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
				name: aliases.join(', ')
			})}
		</h3>
	{/if}

	{#if data.connections}
		<ul>
			{#each data.connections[0] as s, i (i)}
				<li>
					<a href={TagWorkConnectionLink[s.site](s.content_id)}>
						{TagWorkConnectionTypes[s.site]}
					</a>
				</li>
			{/each}
			{#if data.connections[1]}
				{#each data.connections[1] as s, i (i)}
					<li>
						<a
							href={(data.tag.category === 3
								? SourceConnectionLink
								: ProfileConnectionLink)[s.site](s.content_id)}
						>
							{(data.tag.category === 3
								? SourceConnectionTypes
								: ProfileConnectionTypes)[s.site]}
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
		{#if data.wiki_page?.find(({ lang }) => lang === Languages[wikiView])}
			<!-- eslint-disable-next-line svelte/no-at-html-tags -->
			{@html data.wiki_page?.find(({ lang }) => lang === Languages[wikiView])?.page_rendered}
		{/if}
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
				<tr><th>BPM</th><td>{data.tag.song.bpm}</td></tr>
				<tr><th>{m.crisp_red_canary_tickle()}</th><td>{data.tag.song.author}</td></tr>
			</tbody>
		</table>
		{#if data.song_connections}
			<ul>
				{#each data.song_connections as s, i (i)}
					<li>
						<a href={SongConnectionLink[s.site](s.content_id)}>
							{SongConnectionTypes[s.site]}
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
		{#if data.song_relation_svg}
			<!-- eslint-disable-next-line svelte/no-at-html-tags -->
			{@html data.song_relation_svg}
		{/if}
	</Section>
{/if}

{#if data.tag.children.length}
	<Section title={m.weird_nimble_fireant_climb()}>
		<ul>
			{#each data.tag.children as tag, i (i)}
				<li><a href={tag.slug}>{tag.name}</a></li>
			{/each}
		</ul>
	</Section>
{/if}

<Section title={m.quiet_super_kangaroo_kiss({ tag: data.display_name })}>
	{#if results}
		<div class="grid grid-cols-[repeat(auto-fill,minmax(192px,1fr))] gap-x-4 gap-y-4">
			{#each results as work, i (i)}
				<WorkCard {work} />
			{/each}
		</div>
		{#if !fetching && results.length < data.works!.count}
			<button class="center mx-auto mt-5 block p-2" onclick={getNextBatch}
				>{m.red_pink_bear_play()}</button
			>
		{/if}
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
</style>
