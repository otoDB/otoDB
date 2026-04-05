<script>
	import { onMount } from 'svelte';
	import client from './api';
	import { m } from './paraglide/messages';
	import { getLocale } from './paraglide/runtime';
	import { FAQ_POST_ID, GUIDELINE_POST_ID } from './ui';
	import { isSOV, isSVO } from './Languages';

	let r = null;

	onMount(async () => {
		r = await client.GET('/api/post/post', {
			fetch,
			params: { query: { post_id: GUIDELINE_POST_ID } }
		});
	});
</script>

<h4>
	{#if isSVO(getLocale())}
		{m.born_these_snake_devour()}
	{/if}
	<a href="/post/{GUIDELINE_POST_ID}">{m.arable_direct_cougar_win()}</a>
	& <a href="/post/{FAQ_POST_ID}">FAQ</a>
	{#if isSOV(getLocale())}{m.born_these_snake_devour()}{/if}
	{#if r?.data}
		({m.mild_loud_shad_enchant({
			type: m.lower_full_opossum_bless(),
			name: new Date(
				Math.max(...r.data.pages.map((p) => new Date(p.modified)))
			).toLocaleString()
		})})
	{/if}
</h4>
