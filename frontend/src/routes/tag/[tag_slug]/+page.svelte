<script lang="ts">
	import Section from '$lib/Section.svelte';
	import { m } from '$lib/paraglide/messages.js';
	import { WorkTagCategory } from '$lib/enums';
	import WorkCard from '$lib/WorkCard.svelte';
	import CommentTree from '$lib/CommentTree.svelte';
	import SongTag from '$lib/SongTag.svelte';

	let { data } = $props();
</script>

<svelte:head>
	<title
		>{m.mild_loud_shad_enchant({
			type: m.empty_legal_chicken_taste(),
			name: data.tag.name
		})}</title
	>
</svelte:head>

<Section
	title={m.mild_loud_shad_enchant({ type: m.empty_legal_chicken_taste(), name: data.tag.name })}
	menuLinks={data.links}
>
	<div>
		<span>{m.empty_legal_chicken_taste()}</span>
		<!-- eslint-disable-next-line svelte/require-each-key -->
		{#each data.tree as node}
			> <a href={node.slug}>{node.name}</a> >
		{:else}
			>
		{/each}
		<span>{data.tag.name}</span>
	</div>

	<h2>
		{m.mild_loud_shad_enchant({
			type: m.plane_awful_bobcat_spark(),
			name: WorkTagCategory[data.tag.category]()
		})}
	</h2>

	{#if data.tag.aliases.length}
		<h3>
			<!-- eslint-disable-next-line svelte/require-each-key -->
			Also known as: {#each data.tag.aliases as alias, i}{alias}{#if i + 1 != data.tag.aliases.length},
				{/if}{/each}.
		</h3>
	{/if}

	<hr />

	{#if data.wiki_page}
		<!-- eslint-disable-next-line svelte/no-at-html-tags -->
		{@html data.wiki_page}
	{:else}
		<p>This tag does not yet have a wiki page.</p>
	{/if}
</Section>

{#if data.tag.song}
	<Section title="Song: {data.tag.song.title}" menuLinks={data.song_links}>
		<table>
			<tbody>
				<tr><th>{m.large_factual_octopus_exhale()}</th><td>{data.tag.song.title}</td></tr>
				<tr><th>BPM</th><td>{data.tag.song.bpm}</td></tr>
				<tr><th>{m.crisp_red_canary_tickle()}</th><td>{data.tag.song.author}</td></tr>
			</tbody>
		</table>
		{#if data.tag?.song.tags.length}
			<ul id="song-tags">
				<!-- eslint-disable-next-line svelte/require-each-key -->
				{#each data.tag?.song.tags as tag}
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
			<!-- eslint-disable-next-line svelte/require-each-key -->
			{#each data.tag.children as tag}
				<li><a href={tag.slug}>{tag.name}</a></li>
			{/each}
		</ul>
	</Section>
{/if}

<Section title="Works tagged with {data.tag.name}">
	{#if data.works.items.length}
		<div class="flex flex-wrap gap-3">
			<!-- eslint-disable-next-line svelte/require-each-key -->
			{#each data.works.items as work}
				<WorkCard {work} />
			{/each}
		</div>
	{:else}
		<p>This tag is an orphan.</p>
	{/if}
</Section>

<Section title={m.same_broad_haddock_pinch()}>
	<CommentTree
		comments={data.comments}
		user={data.user ?? null}
		model="tagwork"
		pk={data.tag.id!}
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
</style>
