<script lang="ts">
	import Section from '$lib/Section.svelte';
	import { m } from '$lib/paraglide/messages.js';
	import { SongTagCategory } from '$lib/enums';
	import { enhance } from '$app/forms';
	import type { PageProps } from './$types';
	import TagField from '$lib/TagField.svelte';

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
		<table>
			<tbody>
				<tr>
					<th><label for="category">{m.plane_awful_bobcat_spark()}</label></th>
					<td
						><select name="category" bind:value={category}>
							{#each SongTagCategory as cat, i (i)}
								<option value={i}>{cat()}</option>
							{/each}
						</select></td
					>
				</tr>
				<tr>
					<th><label for="parent">Parent</label></th>
					<td
						><TagField
							type="song"
							name="parent"
							value={form?.parent_slug ?? data.parent_slug ?? ''}
						/></td
					>
				</tr>
			</tbody>
		</table>
		<input type="submit" />
	</form>
</Section>
