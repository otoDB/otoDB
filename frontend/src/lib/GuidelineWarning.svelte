<script lang="ts">
	import { onMount } from 'svelte';
	import client from '$lib/api';
	import { m } from '$lib/paraglide/messages';
	import { getLocale } from '$lib/paraglide/runtime';
	import { FAQ_POST_ID, GUIDELINE_POST_ID } from '$lib/ui';
	import { isSOV, isSVO } from '$lib/enums/language';

	let latestMod: null | Date = $state(null);

	onMount(async () => {
		const { data } = await client.GET('/api/post/post', {
			fetch,
			params: { query: { post_id: GUIDELINE_POST_ID } }
		});
		if (!data) return;

		latestMod =
			data.pages
				.map((p) => new Date(p.modified))
				.sort((a, b) => b.getTime() - a.getTime())
				.at(0) ?? null;
	});
</script>

<h4>
	{#if isSVO(getLocale())}
		{m.born_these_snake_devour()}
	{/if}
	<a href="/post/{GUIDELINE_POST_ID}">{m.arable_direct_cougar_win()}</a>
	& <a href="/post/{FAQ_POST_ID}">FAQ</a>
	{#if isSOV(getLocale())}{m.born_these_snake_devour()}{/if}
	{#if latestMod}
		({m.mild_loud_shad_enchant({
			type: m.lower_full_opossum_bless(),
			name: latestMod.toLocaleString()
		})})
	{/if}
</h4>
