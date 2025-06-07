<script lang="ts">
	import Section from '$lib/Section.svelte';
	import type { PageProps } from './$types';
	import { m } from '$lib/paraglide/messages.js';
	import WorkCard from '$lib/WorkCard.svelte';
	import TagsField from '$lib/TagsField.svelte';
	import client from '$lib/api';

	let { data }: PageProps = $props();
	let results = $derived(data.results!.items);
	let tags = $derived(data.query_tags.split(' '));

	let fetching = $state(false);
	const getNextBatch = async () => {
		fetching = true;
		const { data: d } = await client.GET('/api/work/search', {
			fetch,
			params: {
				query: {
					query: data.query,
					tags: tags.join(' '),
					limit: data.batch_size,
					offset: results.length
				}
			}
		});
		results = results.concat(d!.items);
		fetching = false;
	};
</script>

<svelte:head>
	<title>{m.mean_top_antelope_love()}</title>
</svelte:head>

<Section
	title={m.mean_top_antelope_love()}
	menuLinks={[
		{ title: m.grand_merry_fly_succeed(), pathname: 'work/search' },
		{ title: m.empty_legal_chicken_taste(), pathname: 'tag/search' },
		{ title: m.stale_loose_squid_cut(), pathname: 'list/search' }
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
		<TagsField type="work" name="tags" bind:value={tags} class="w-full" />
	</form>
	<hr />
	<div class="grid grid-cols-[repeat(auto-fill,minmax(192px,1fr))] gap-x-4 gap-y-4">
		{#each results as work, i (i)}
			<WorkCard {work} />
		{/each}
	</div>
	{#if !fetching && results.length < data.results!.count}
		<button class="center mx-auto mt-5 block p-2" onclick={getNextBatch}
			>{m.red_pink_bear_play()}</button
		>
	{/if}
</Section>

<style>
	hr {
		margin: 1rem 0;
	}
</style>
