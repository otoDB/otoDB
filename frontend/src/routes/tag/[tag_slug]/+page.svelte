<script lang="ts">
	import { page } from '$app/state';
	import CommentTree from '$lib/CommentTree/CommentTree.svelte';
	import Connections from '$lib/Connections.svelte';
	import LoadMoreButton from '$lib/LoadMoreButton.svelte';
	import RelationViewer from '$lib/RelationViewer.svelte';
	import Section from '$lib/Section.svelte';
	import SongTag from '$lib/SongTag.svelte';
	import WorkCard from '$lib/WorkCard.svelte';
	import WorkTag from '$lib/WorkTag.svelte';
	import WikiView from '$lib/WikiView.svelte';
	import client from '$lib/api.js';
	import { mediaTypes, resolveMediaTypeKeyById } from '$lib/enums/mediaType.js';
	import { mediaConnectionMap } from '$lib/enums/mediaConnection.js';
	import { profileConnectionMap } from '$lib/enums/profileConnection.js';
	import { songConnectionMap } from '$lib/enums/songConnection.js';
	import { TagWorkConnectionMap } from '$lib/enums/tagWorkConnection.js';

	import { m } from '$lib/paraglide/messages.js';
	import {
		MediaConnectionTypes,
		ModelsWithComments,
		ProfileConnectionTypes,
		WorkTagCategory,
		type components
	} from '$lib/schema.js';
	import { WorkTagCategoryMap } from '$lib/enums/workTagCategory.js';
	import { getTagDisplayName, getTagDisplaySlug } from '$lib/ui.js';

	let { data } = $props();
	let results = $derived(data.works!.items);

	const articleLd = $derived(
		data.wiki_page?.length
			? '<script type="application/ld+json">' +
					JSON.stringify({
						'@context': 'https://schema.org',
						'@type': 'Article',
						'headline': data.display_name,
						'url': `https://otodb.net${page.url.pathname}`
					}) +
					'</' +
					'script>'
			: null
	);

	const aliases = $derived(
		[data.tag.name, ...(data.aliases?.map((e) => e.name) ?? [])].filter(
			(e) => e !== data.display_name
		)
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

	const sortedChildTags = $derived(
		[...data.tag.children].sort((a, b) => Number(a.deprecated) - Number(b.deprecated))
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

<svelte:head>
	{#if articleLd}
		<!-- eslint-disable-next-line svelte/no-at-html-tags -->
		{@html articleLd}
	{/if}
</svelte:head>

<Section title={data.display_name} type={m.empty_legal_chicken_taste()} menuLinks={data.links}>
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
			name: WorkTagCategoryMap[data.tag.category].nameFn()
		})}
		{#if data.tag.category === WorkTagCategory.Media && data.tag.media_type?.length}
			({#each data.tag.media_type as t, i (i)}{mediaTypes[
					resolveMediaTypeKeyById(t)
				].nameFn()}{#if i + 1 !== data.tag.media_type.length},&nbsp;{/if}{/each})
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
		<Connections items={data.connections[0]} map={TagWorkConnectionMap} />
		{#if data.connections[1]?.length}
			{#if data.tag.category === WorkTagCategory.Media}
				<Connections
					items={data.connections[1] as {
						site: MediaConnectionTypes;
						content_id: string;
					}[]}
					map={mediaConnectionMap}
				/>
			{:else if data.tag.category === WorkTagCategory.Creator}
				<Connections
					items={data.connections[1] as {
						site: ProfileConnectionTypes;
						content_id: string;
						dead?: boolean | null;
					}[]}
					map={profileConnectionMap}
				/>
			{/if}
		{/if}
	{/if}

	<hr class="my-2" />

	<WikiView wiki_page={data.wiki_page} />
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
			<Connections items={data.song_connections} map={songConnectionMap} />
		{/if}
		{#if data.tag?.song.tags.length}
			<ul id="song-tags">
				{#each data.tag?.song.tags as tag, i (i)}
					<li><SongTag {tag} /></li>
				{/each}
			</ul>
		{/if}
		{#if data.song_relations && data.song_relations[0].length}
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

{#if sortedChildTags.length}
	<Section title={m.weird_nimble_fireant_climb()}>
		<div class="flex flex-wrap gap-3">
			{#each sortedChildTags as tag, i (i)}
				<WorkTag {tag} fade={tag.deprecated} />
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

<Section
	title="{m.quiet_super_kangaroo_kiss({ tag: data.display_name })} ({data.works?.count})"
	href="/work?tags={encodeURIComponent('^' + getTagDisplaySlug(data.tag))}"
>
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
		model={ModelsWithComments.tagwork}
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
