<script lang="ts">
	import Section from '$lib/Section.svelte';

	import { m } from '$lib/paraglide/messages.js';
	import client from '$lib/api';
	import { EnumValues, SongTagCategoryNames } from '$lib/enums';
	import LoadMoreButton from '$lib/LoadMoreButton.svelte';
	import SongTag from '$lib/SongTag.svelte';
	import { SongTagCategory } from '$lib/schema.js';

	let { data } = $props();
	let results = $derived(data.results!.items);
	let category = $state(data.category);

	const fetchNextBatch = () =>
		client.GET('/api/tag/song_tag_search', {
			fetch,
			params: {
				query: {
					query: data.query,
					limit: data.batch_size,
					offset: results.length,
					category: data.category === -1 ? null : data.category
				}
			}
		});
</script>

<Section
	title={m.dull_plain_angelfish_cuddle()}
	type={m.mean_top_antelope_love()}
	menuLinks={[
		{ title: m.grand_merry_fly_succeed(), pathname: `work?query=${data.query}` },
		{ title: m.empty_legal_chicken_taste(), pathname: `tag?query=${data.query}` },
		{ title: m.grand_nice_pony_belong(), pathname: `song?query=${data.query}` },
		{ title: m.dull_plain_angelfish_cuddle(), pathname: 'song_attribute' },
		{ title: m.stale_loose_squid_cut(), pathname: `list?query=${data.query}` }
	]}
>
	<form target="_self" method="get">
		<input
			type="text"
			name="query"
			placeholder="{m.mean_top_antelope_love()}..."
			value={data.query}
		/>
		<select name="category" bind:value={category}>
			<option value={-1}>{m.keen_soft_crow_relish()}</option>
			{#each EnumValues(SongTagCategory) as cat, i (i)}
				<option value={cat}>{SongTagCategoryNames[cat]()}</option>
			{/each}
		</select>
		<input type="submit" value={m.mean_top_antelope_love()} />
	</form>

	<hr class="my-5" />

	<div class="flex flex-wrap gap-3">
		{#each results as tag, i (i)}
			<SongTag {tag} />
		{/each}
	</div>
	<LoadMoreButton {fetchNextBatch} maxCount={data.results!.count} bind:results />
</Section>
