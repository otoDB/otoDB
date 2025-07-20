<script lang="ts">
	import Section from '$lib/Section.svelte';
	import { m } from '$lib/paraglide/messages.js';
	import TagsField from '$lib/TagsField.svelte';
	import client from '$lib/api';
	import { goto } from '$app/navigation';
	import { isSOV, isSVO } from '$lib/ui';
	import { getLocale } from '$lib/paraglide/runtime';

	let { data } = $props();

	let tags = $state(data.from),
		selected = $state(''),
		del = $state(false);

	const submit = async (e: SubmitEvent) => {
		e.preventDefault();
		const { error } = await client.POST('/api/tag/alias', {
			fetch,
			params: { query: { into_tag: selected, delete: del } },
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
		<form onsubmit={submit}>
			{#if isSVO(getLocale())}
				{m.male_gross_angelfish_reap()}
			{/if}
			<select name="" bind:value={selected}>
				{#each tags as t, i (i)}
					<option value={t}>{t}</option>
				{/each}
			</select>
			{#if isSOV(getLocale())}
				{m.male_gross_angelfish_reap()}
			{/if}

			<label
				>Behaviour: <select name="behaviour" bind:value={del}
					><option value={false}>Keep tags as aliases</option><option value={true}
						>Delete tags</option
					></select
				></label
			>
			<input type="submit" disabled={selected === ''} class="block" />
		</form>
	{/if}
</Section>
