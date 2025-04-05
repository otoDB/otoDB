<script lang="ts">
	import Section from '$lib/Section.svelte';
	import type { PageProps } from './$types';
	import { m } from '$lib/paraglide/messages.js';
	import TagsField from '$lib/TagsField.svelte';
	import client from '$lib/api';
	import { goto } from '$app/navigation';

	let tags = $state([]),
		selected = $state('');

	const submit = async (e: SubmitEvent) => {
		e.preventDefault();
		const { error } = await client.POST('/api/tag/alias', {
			fetch,
			params: { query: { into_tag: selected } },
			body: tags
		});
		if (!error) goto(`/tag/${selected}`, { invalidateAll: true });
	};
</script>

<svelte:head>
	<title>Alias Tags</title>
</svelte:head>

<Section title="Alias Tags">
	Start by giving a space-delimited list of tags.
	<TagsField type="work" class="w-full" bind:value={tags} />
	{#if tags.length}
		into
		<form onsubmit={submit}>
			<select name="" bind:value={selected}>
				{#each tags as t (t)}
					<option value={t}>{t}</option>
				{/each}
			</select>
			<input type="submit" disabled={selected === ''} />
		</form>
	{/if}
</Section>
