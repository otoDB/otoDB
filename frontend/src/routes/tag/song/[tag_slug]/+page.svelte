<script lang="ts">
	import Section from '$lib/Section.svelte';
	import { m } from '$lib/paraglide/messages.js';
	import { SongTagCategory } from '$lib/enums';
	import CommentTree from '$lib/CommentTree.svelte';

	let { data } = $props();
</script>

<Section
	title={m.mild_loud_shad_enchant({ type: m.dull_plain_angelfish_cuddle(), name: data.tag.name })}
	menuLinks={data.links}
>
	<div>
		<span>{m.dull_plain_angelfish_cuddle()}</span>
		{#each data.tree as node, i (i)}
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
</Section>

{#if data.tag.children.length}
	<Section title={m.weird_nimble_fireant_climb()}>
		<ul>
			{#each data.tag.children as tag, i (i)}
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
					<th>{m.large_factual_octopus_exhale()}</th>
					<th>BPM</th>
					<th>{m.crisp_red_canary_tickle()}</th>
				</tr></thead
			>
			<tbody>
				{#each data.songs.items as song, i (i)}
					<tr>
						<td><a href="/tag/{song.work_tag}">{song.title}</a></td>
						<td>{song.bpm}</td>
						<td>{song.author}</td>
					</tr>
				{/each}
			</tbody>
		</table>
	{:else}
		<p>{m.drab_main_husky_dazzle()}</p>
	{/if}
</Section>

<Section title={m.same_broad_haddock_pinch()}>
	<CommentTree
		comments={data.comments}
		user={data.user ?? null}
		model="tagsong"
		pk={data.tag.id}
	/>
</Section>
