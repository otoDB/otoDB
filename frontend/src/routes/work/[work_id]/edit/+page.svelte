<script lang="ts">
	import Section from '$lib/Section.svelte';
	import { m } from '$lib/paraglide/messages.js';
	import { enhance } from '$app/forms';
	import type { PageProps } from '../$types';
	import { Platform, Rating, WorkOrigin, WorkRelationTypes } from '$lib/enums';
	import CollapsibleText from '../CollapsibleText.svelte';
	import RelationEditor from '$lib/RelationEditor.svelte';

	let { data, form }: PageProps = $props();
	let title: string = $state(form?.title ?? data.title!),
		description: string = $state(form?.description ?? data.description!),
		rating: number = $state(form?.rating ?? data.rating!),
		thumbnail: string = $state(form?.thumbnail ?? data.thumbnail!);
</script>

<svelte:head>
	<title
		>{m.mild_loud_shad_enchant({ type: m.grand_merry_fly_succeed(), name: data.title })}</title
	>
</svelte:head>

<Section
	title={m.mild_loud_shad_enchant({ type: m.grand_merry_fly_succeed(), name: data.title })}
	menuLinks={data.links}
>
	<form method="POST" use:enhance action="?/edit">
		{#if form?.failed}<p class="error">Failed!</p>{/if}
		<table class="inline">
			<tbody>
				<tr
					><th><label for="title">Title</label></th><td
						><input required type="text" name="title" bind:value={title} /></td
					></tr
				>
				<tr
					><th><label for="description">Description</label></th><td
						><textarea name="description" bind:value={description}></textarea></td
					></tr
				>
				<tr
					><th><label for="rating">Rating</label></th><td
						><select name="rating" bind:value={rating}>
							<!-- eslint-disable-next-line svelte/require-each-key -->
							{#each Rating as r, i}<option value={i}>{r()}</option>{/each}</select
						></td
					></tr
				>
				<tr
					><th><label for="thumbnail">Thumbnail</label></th><td
						><input type="text" required name="thumbnail" bind:value={thumbnail} /></td
					></tr
				>
				<tr
					><th><label for="reason">Update Reason</label></th><td
						><input type="text" required name="reason" value={form?.reason ?? ''} /></td
					></tr
				>
			</tbody>
		</table>
		<table class="inline">
			<thead
				><tr>
					<th></th>
					<th>{m.large_factual_octopus_exhale()}</th>
					<th>{m.clear_lucky_peacock_pick()}</th>
					<th>{m.sour_swift_sparrow_spin()}</th>
					<th>{m.large_polite_otter_thrive()}</th>
				</tr></thead
			>
			<tbody>
				<!-- eslint-disable-next-line svelte/require-each-key -->
				{#each data.sources! as src}
					<tr>
						<td
							><button
								onclick={() => {
									title = src.title;
									description = src.description;
									thumbnail = src.thumbnail;
								}}
								type="button">&lt;&lt;</button
							></td
						>
						<td class="whitespace-nowrap">{src.title}</td>
						<td><CollapsibleText text={src.description}></CollapsibleText></td>
						<td>{Platform[src.platform]}</td>
						<td class="whitespace-nowrap">{WorkOrigin[src.work_origin]()}</td>
					</tr>
				{/each}
			</tbody>
		</table>
		<br />
		<input type="submit" />
	</form>
</Section>

<Section title="Relations">
	<RelationEditor init_relations={data.relations} obj_type="work" this_id={data.id!}
	></RelationEditor>
</Section>
