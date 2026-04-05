<script lang="ts">
	import Section from '$lib/Section.svelte';
	import { m } from '$lib/paraglide/messages.js';
	import TagsField from '$lib/TagsField.svelte';
	import client from '$lib/api';
	import { goto } from '$app/navigation';
	import { isSOV, isSVO } from '$lib/enums';
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
			params: { query: { into_tag: selected, delete: del } },
			body: tags
		});
		if (!error) goto(`/tag/${data.merged_slug}/edit`, { invalidateAll: true });
	};
</script>

<Section title={m.front_maroon_hamster_urge()}>
	<GuidelineWarning />
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

			<label class="block"
				>{m.mild_loud_shad_enchant({
					type: m.still_happy_cheetah_savor(),
					name: ''
				})}<select name="behaviour" bind:value={del}
					><option value={false}>{m.dirty_lazy_mammoth_empower()}</option><option
						value={true}>{m.real_born_goat_snap()}</option
					></select
				></label
			>
			<input type="submit" disabled={selected === ''} class="block" />
		</form>
	{/if}
</Section>
