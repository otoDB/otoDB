<script lang="ts">
	import Section from '$lib/Section.svelte';
	import { m } from '$lib/paraglide/messages.js';
	import { SongTagCategory } from '$lib/enums';
	import CommentTree from '$lib/CommentTree.svelte';

	let { data } = $props();
</script>

<svelte:head>
	<title>{m.mild_loud_shad_enchant({ type: 'Song Tag', name: data.tag.name })}</title>
</svelte:head>

<Section
	title={m.mild_loud_shad_enchant({ type: 'Song Tag', name: data.tag.name })}
	menuLinks={data.links}
>
	<div>
		<span>Song tag</span>
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
			name: SongTagCategory[data.tag.category]()
		})}
	</h2>

	{#if data.tag.aliases.length}
		<h3>
			<!-- eslint-disable-next-line svelte/require-each-key -->
			Also known as: {#each data.tag.aliases as alias, i}{alias}{#if i + 1 != data.tag.aliases.length},
				{/if}{/each}.
		</h3>
	{/if}
</Section>

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

<Section title="Songs tagged with {data.tag.name}">
	{#if data.songs.items.length}
		<table>
			<thead
				><tr>
					<th>Title</th>
					<th>BPM</th>
					<th>Author</th>
				</tr></thead
			>
			<tbody>
				<!-- eslint-disable-next-line svelte/require-each-key -->
				{#each data.songs.items as song}
					<tr>
						<td><a href="/tag/{song.work_tag}">{song.title}</a></td>
						<td>{song.bpm}</td>
						<td>{song.author}</td>
					</tr>
				{/each}
			</tbody>
		</table>
	{:else}
		<p>This tag is an orphan.</p>
	{/if}
</Section>

<Section title={m.same_broad_haddock_pinch()}>
	<CommentTree
		comments={data.comments}
		user={data.user ?? null}
		model="tagsong"
		pk={data.tag.id!}
	/>
</Section>
