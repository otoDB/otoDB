<script>
	import client from './api';
	import { m } from './paraglide/messages';
	import { FAQ_POST_ID, GUIDELINE_POST_ID } from './ui';
	const r = client.GET('/api/post/post', {
		fetch,
		params: { query: { post_id: GUIDELINE_POST_ID } }
	});
</script>

<h4>
	{m.born_these_snake_devour()} <a href="/post/{GUIDELINE_POST_ID}"
		>{m.arable_direct_cougar_win()}</a
	>
	& <a href="/post/{FAQ_POST_ID}">FAQ</a> {#await r}
		<!-- Blank -->
	{:then post}
		{#if post.data}
			({m.mild_loud_shad_enchant({
				type: m.lower_full_opossum_bless(),
				name: new Date(
					Math.max(...post.data.pages.map((p) => new Date(p.modified)))
				).toLocaleString()
			})})
		{/if}
	{/await}
</h4>
