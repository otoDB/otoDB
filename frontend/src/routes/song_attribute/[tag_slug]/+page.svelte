<script lang="ts">
	import Section from '$lib/Section.svelte';
	import { m } from '$lib/paraglide/messages.js';
	import { SongTagCategoryNames } from '$lib/enums';
	import CommentTree from '$lib/CommentTree.svelte';
	import { getTagDisplayName } from '$lib/api.js';
	import { PathsApiCommentCommentDeleteParametersQueryModel } from '$lib/schema.js';

	let { data } = $props();

	const aliases = $derived(
		[data.tag.name, ...(data.aliases?.map((e) => e.name) ?? [])].filter(
			(e) => e !== data.display_name
		)
	);
</script>

<Section title={data.tag.name} type={m.dull_plain_angelfish_cuddle()} menuLinks={data.links}>
	<div>
		<span>{m.dull_plain_angelfish_cuddle()}</span>
		{#each data.tree as node, i (i)}
			> {#if node.slug === data.tag.slug}{data.display_name}{:else}<a href={node.slug}
					>{getTagDisplayName(node)}</a
				>{/if}&nbsp;{/each}> <span>{data.tag.name}</span>
	</div>

	<h2>
		{m.mild_loud_shad_enchant({
			type: m.plane_awful_bobcat_spark(),
			name: SongTagCategoryNames[data.tag.category]()
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
</Section>

{#if data.tag.children.length}
	<Section title={m.misty_great_gazelle_comfort()}>
		<ul>
			{#each data.tag.children as tag, i (i)}
				<li><a href={tag.slug}>{tag.name}</a></li>
			{/each}
		</ul>
	</Section>
{/if}

<Section title={m.red_petty_jurgen_sway({ name: data.tag.name })}>
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
						<td>{song.bpm ?? m.simple_less_marlin_enchant()}</td>
						<td>{song.author}</td>
					</tr>
				{/each}
			</tbody>
		</table>
	{:else}
		<p>{m.noble_sleek_duck_lift()}</p>
	{/if}
</Section>

<Section title={m.same_broad_haddock_pinch()}>
	<CommentTree
		comments={data.comments}
		user={data.user ?? null}
		model={PathsApiCommentCommentDeleteParametersQueryModel.tagsong}
		pk={data.tag.id}
	/>
</Section>
