<script lang="ts">
	import Section from '$lib/Section.svelte';
	import type { PageProps } from './$types';
	import WorkCard from '$lib/WorkCard.svelte';
	import client from '$lib/api';
	import LoadMoreButton from '$lib/LoadMoreButton.svelte';
	import { m } from '$lib/paraglide/messages';

	let { data }: PageProps = $props();
	let results = $derived(data.results!.items);

	const fetchNextBatch = () =>
		client.GET('/api/work/tags_needed', {
			fetch,
			params: {
				query: {
					limit: data.batch_size,
					offset: results.length
				}
			}
		});
</script>

<svelte:head>
	<title>{m.spry_late_kudu_assure()}</title>
</svelte:head>

<Section title={m.spry_late_kudu_assure()}>
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
