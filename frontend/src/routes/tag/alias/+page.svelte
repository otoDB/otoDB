<script lang="ts">
	import Section from '$lib/Section.svelte';
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
	<title>{m.front_maroon_hamster_urge()}</title>
</svelte:head>

<Section title={m.front_maroon_hamster_urge()}>
	<TagsField type="work" class="w-full" bind:value={tags} />
	{#if tags.length}
		{m.male_gross_angelfish_reap()}
		<form onsubmit={submit}>
			<select name="" bind:value={selected}>
				{#each tags as t, i (i)}
					<option value={t}>{t}</option>
				{/each}
			</select>
			<input type="submit" disabled={selected === ''} />
		</form>
	{/if}
</Section>
