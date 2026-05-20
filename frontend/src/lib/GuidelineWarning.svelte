<script lang="ts">
	import { onMount } from 'svelte';
	import client from '$lib/api';
	import { m } from '$lib/paraglide/messages';
	import { getLocale } from '$lib/paraglide/runtime';
	import { isSOV, isSVO } from '$lib/enums/language';

	let latestMod: null | Date = $state(null);

	onMount(async () => {
		const { data } = await client.GET('/api/wiki/{page_slug}', {
			fetch,
			params: { path: { page_slug: 'editing_guidelines' } }
		});
		if (!data || data.length === 0) return;

		latestMod =
			data
				.map((p) => p.modified)
				.filter((m): m is string => !!m)
				.map((m) => new Date(m))
				.sort((a, b) => b.getTime() - a.getTime())
				.at(0) ?? null;
	});
</script>

<h4>
	{#if isSVO(getLocale())}
		{m.born_these_snake_devour()}
	{/if}
	<a href="/wiki/editing_guidelines">{m.arable_direct_cougar_win()}</a>
	& <a href="/wiki/faq">FAQ</a>
	{#if isSOV(getLocale())}{m.born_these_snake_devour()}{/if}
	{#if latestMod}
		({m.mild_loud_shad_enchant({
			type: m.lower_full_opossum_bless(),
			name: latestMod.toLocaleString()
		})})
	{/if}
</h4>
