<script lang="ts">
	import Section from '$lib/Section.svelte';
	import { m } from '$lib/paraglide/messages.js';
	import { SongRelationTypes, WorkTagCategory } from '$lib/enums';
	import { enhance } from '$app/forms';
	import type { PageProps } from './$types';
	import TagField from '$lib/TagField.svelte';
	import Markdown from 'svelte-exmarkdown';
	import RelationEditor from '$lib/RelationEditor.svelte';

	let { data, form }: PageProps = $props();

	let category = $state(form?.category ?? data.tag?.category);
	let md = $state(data.wiki_page);
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
	<form method="POST" use:enhance action="?/edit">
		{#if form?.failed}<p class="error">Failed!</p>{/if}
		{#if data.tag.category === 2 && category !== 2}
			<p class="text-red-500">
				Changing the category will delete all related information about the song, including
				tags and relations!
			</p>
		{/if}
		<table>
			<tbody>
				<tr>
					<th><label for="category">{m.plane_awful_bobcat_spark()}</label></th>
					<td
						><select name="category" bind:value={category}>
							{#each WorkTagCategory as cat, i}
								<option value={i}>{cat()}</option>
							{/each}
						</select></td
					>
				</tr>
				<tr>
					<th><label for="parent">Parent</label></th>
					<td
						><TagField
							type="work"
							name="parent"
							value={form?.parent_slug ?? data.parent_slug ?? ''}
						/></td
					>
				</tr>
			</tbody>
		</table>
		{#if category === 2}
			<table>
				<tbody>
					<tr
						><th><label for="song_title">Title</label></th><td
							><input
								type="text"
								name="song_title"
								value={data.tag?.song?.title ?? ''}
							/></td
						></tr
					>
					<tr
						><th><label for="song_author">Author</label></th><td
							><input
								type="text"
								name="song_author"
								value={data.tag?.song?.author ?? ''}
							/></td
						></tr
					>
					<tr
						><th><label for="song_bpm">BPM</label></th><td
							><input
								type="number"
								name="song_bpm"
								value={data.tag?.song?.bpm ?? 100}
							/></td
						></tr
					>
				</tbody>
			</table>
		{/if}
		<input type="submit" />
	</form>
</Section>

{#if category === 2 && data.tag.category === 2}
	<Section title="Song: {data.tag?.song.title}" menuLinks={data.song_links}>
		<RelationEditor
			init_relations={data.song_relations}
			obj_type="song"
			this_id={data.tag.song?.id!}
		></RelationEditor>
	</Section>
{/if}

<Section title="Wiki page">
	<form action="?/wiki_page" method="POST" use:enhance>
		<div class="grid grid-cols-2 gap-3">
			<textarea required name="md" bind:value={md}></textarea>
			<div id="md-preview">
				<Markdown {md} />
			</div>
		</div>
		<input type="submit" />
	</form>
</Section>
