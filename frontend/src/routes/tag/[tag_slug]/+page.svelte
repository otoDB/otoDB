<script lang="ts">
	import Section from '$lib/Section.svelte';
	import { m } from '$lib/paraglide/messages.js';
	import {
		Languages,
		ProfileConnectionLink,
		ProfileConnectionTypes,
		SongConnectionLink,
		SongConnectionTypes,
		MediaConnectionLink,
		MediaConnectionTypes,
		TagWorkConnectionLink,
		TagWorkConnectionTypes,
		WorkTagCategory,
		MediaType
	} from '$lib/enums';
	import WorkCard from '$lib/WorkCard.svelte';
	import CommentTree from '$lib/CommentTree.svelte';
	import SongTag from '$lib/SongTag.svelte';
	import client, { getTagDisplayName, makeTagDisplayName } from '$lib/api.js';
	import { getLocale } from '$lib/paraglide/runtime.js';
	import LoadMoreButton from '$lib/LoadMoreButton.svelte';
	import ConnectionFavicon from '$lib/ConnectionFavicon.svelte';
	import WorkTag from '$lib/WorkTag.svelte';
	import LangSwitch from '$lib/LangSwitch.svelte';
	import type { components } from '$lib/schema.js';
	import RelationViewer from '$lib/RelationViewer.svelte';

	let { data } = $props();
	let results = $derived(data.works!.items);

	const aliases = $derived(
		[data.tag.name, ...(data.aliases?.map((e) => e.name) ?? [])]
			.map(makeTagDisplayName)
			.filter((e) => e !== data.display_name)
	);

	let wikiView = $derived(
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

	const paths = $derived.by(() => {
		const get_paths = (node: string): components['schemas']['TagWorkSchema'][][] =>
			Object.hasOwn(data.paths[1], node)
				? data.paths[1][node].flatMap((next) =>
						get_paths(next).map((p) => [
							...p,
							data.paths[0].find((t) => t.slug === node) ?? data.tag
						])
					)
				: [[data.paths[0].find((t) => t.slug === node) ?? data.tag]];
		return get_paths(data.tag.slug);
	});
</script>

<Section
	title={data.display_name}
	type={m.empty_legal_chicken_taste()}
	menuLinks={data.links}
>
	<div>
		{#each paths as path, i (i)}
			<div>
				<span>{m.empty_legal_chicken_taste()}</span>
				{#each path as node, j (j)}
					> {#if node.slug === data.tag.slug}{data.display_name}{:else}<a href={node.slug}
							>{getTagDisplayName(node)}</a
						>{/if}&nbsp;
				{/each}
			</div>
		{/each}
	</div>

	<h2>
		{m.mild_loud_shad_enchant({
			type: m.plane_awful_bobcat_spark(),
			name: WorkTagCategory[data.tag.category]()
		})}
		{#if data.tag.category === 6 && data.tag.media_type?.length}
			({#each data.tag.media_type as t, i (i)}{MediaType[
					t
				]()}{#if i + 1 !== data.tag.media_type.length},&nbsp;{/if}{/each})
		{/if}
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
		<h2>{m.sad_lazy_goat_engage()}</h2>
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
					<li class={{ 'opacity-60': s.dead }}>
						<ConnectionFavicon type={ext_cat_types[s.site]} class="inline size-4" />
						<a
							href={ext_cat_links[s.site](s.content_id)}
							target="_blank"
							rel="noopener noreferrer"
							class={{ 'line-through': s.dead }}
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
			<LangSwitch
				availableLanguages={data.wiki_page.map((v) => Languages[v.lang])}
				bind:value={wikiView}
			/>
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
		title={data.tag.song.title}
		type={m.grand_nice_pony_belong()}
		menuLinks={data.song_links}
	>
		<table>
			<tbody>
				<tr><th>{m.large_factual_octopus_exhale()}</th><td>{data.tag.song.title}</td></tr>
				{#if data.tag.song.bpm || data.tag.song.variable_bpm}<tr
						><th>BPM</th><td
							>{#if data.tag.song.variable_bpm && data.tag.song.bpm}{m.big_helpful_tortoise_swim()}
								({data.tag.song.bpm}){:else if data.tag.song.bpm}{data.tag.song
									.bpm}{:else}{m.big_helpful_tortoise_swim()}{/if}</td
						></tr
					>{/if}
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
		{#if data.song_relations[0]?.length}
			<RelationViewer
				id={data.tag.song.id}
				objects={data.song_relations[1]}
				relations={data.song_relations[0]}
				defaultDir="LR"
				type="song"
				min_height={80}
			/>
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

{#await data.similar}
	<!-- Blank -->
{:then similar}
	{#if similar?.length}
		<Section title={m.topical_main_beaver_walk()}>
			<div class="flex flex-wrap gap-3">
				{#each similar as s, i (i)}
					<WorkTag tag={s} />
				{/each}
			</div>
		</Section>
	{/if}
{/await}

<Section title="{m.quiet_super_kangaroo_kiss({ tag: data.display_name })} ({data.works?.count})">
	{#if results.length}
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
		border-top: var(--otodb-color-content-faint) 1px solid;
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
</style>
