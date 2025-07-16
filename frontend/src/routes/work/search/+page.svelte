<script lang="ts">
	import Section from '$lib/Section.svelte';
	import type { PageProps } from './$types';
	import { m } from '$lib/paraglide/messages.js';
	import WorkCard from '$lib/WorkCard.svelte';
	import TagsField from '$lib/TagsField.svelte';
	import client from '$lib/api';
	import LoadMoreButton from '$lib/LoadMoreButton.svelte';

	let { data }: PageProps = $props();
	let results = $derived(data.results!.items);

	const fetchNextBatch = () =>
		client.GET('/api/work/search', {
			fetch,
			params: {
				query: {
					query: data.query,
					tags: data.query_tags,
					limit: data.batch_size,
					offset: results.length
				}
			}
		});
</script>

<svelte:head>
	<title>{m.mean_top_antelope_love()}</title>
</svelte:head>

<Section
	title={m.mean_top_antelope_love()}
	menuLinks={[
		{ title: m.grand_merry_fly_succeed(), pathname: 'work/search' },
		{ title: m.empty_legal_chicken_taste(), pathname: `tag/search?query=${data.query}` },
		{ title: m.stale_loose_squid_cut(), pathname: `list/search?query=${data.query}` }
	]}
>
	<form target="_self" method="get">
		<input
			type="text"
			name="query"
			placeholder="{m.mean_top_antelope_love()}..."
			value={data.query}
		/>
		<input type="submit" value={m.mean_top_antelope_love()} />
		<h4>{m.mild_loud_shad_enchant({ type: m.empty_legal_chicken_taste(), name: '' })}</h4>
		<TagsField type="work" name="tags" value={data.query_tags.split(' ')} class="w-full" />
	</form>
	<hr />
	<div class="grid grid-cols-[repeat(auto-fill,minmax(192px,1fr))] gap-x-4 gap-y-4">
		{#each results as work, i (i)}
			<WorkCard {work} />
		{/each}
	</div>
	<LoadMoreButton maxCount={data.results!.count} bind:results {fetchNextBatch} />
</Section>

<style>
	hr {
		margin: 1rem 0;
	}
</style>
