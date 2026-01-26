<script lang="ts">
	import Section from '$lib/Section.svelte';
	import { m } from '$lib/paraglide/messages.js';
	import TagsField from '$lib/TagsField.svelte';
	import client from '$lib/api';
	import { goto } from '$app/navigation';
	import { isSOV, isSVO } from '$lib/ui';
	import { getLocale } from '$lib/paraglide/runtime';
	import GuidelineWarning from '$lib/GuidelineWarning.svelte';

	let { data } = $props();

	let tags = $state(data.from),
		selected = $state(''),
		del = $state(false);

	const submit = async (e: SubmitEvent) => {
		e.preventDefault();
		const { error, data } = await client.POST('/api/tag/alias', {
			fetch,
			params: { query: { into_tag: selected, delete: del, type: 'song' } },
			body: tags
		});
		if (!error) goto(`/song_attribute/${data.merged_slug}`, { invalidateAll: true });
	};
</script>

<svelte:head>
	<title>{m.front_maroon_hamster_urge()}</title>
</svelte:head>

<Section title={m.front_maroon_hamster_urge()}>
	<GuidelineWarning />
	<TagsField type="song" class="w-full" bind:value={tags} />
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
					><option value={false}>{m.dirty_lazy_mammoth_empower()}</option><option
						value={true}>{m.real_born_goat_snap()}</option
					></select
				></label
			>
			<input type="submit" disabled={selected === ''} class="block" />
		</form>
	{/if}
</Section>
