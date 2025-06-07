<script lang="ts">
	import Section from '$lib/Section.svelte';
	import type { PageProps } from './$types';
	import { m } from '$lib/paraglide/messages.js';
	import WorkTag from '$lib/WorkTag.svelte';
	import client from '$lib/api';
	import { WorkTagCategory } from '$lib/enums';

	let { data }: PageProps = $props();
	let results = $derived(data.results!.items);
	let category = $state(data.category);

	let fetching = $state(false);
	const getNextBatch = async () => {
		fetching = true;
		const { data: d } = await client.GET('/api/tag/search', {
			fetch,
			params: {
				query: {
					query: data.query,
					limit: data.batch_size,
					offset: results.length,
					category: category
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
		<select name="category" bind:value={category}>
			<option value={-1}>{m.keen_soft_crow_relish()}</option>
			{#each WorkTagCategory as cat, i (i)}
				<option value={i}>{cat()}</option>
			{/each}
		</select>
		<input type="submit" value={m.mean_top_antelope_love()} />
	</form>

	<hr class="my-5" />

	<div class="flex flex-wrap gap-3">
		{#each results as tag, i (i)}
			<WorkTag {tag} />
		{/each}
	</div>

	{#if !fetching && results.length < data.results!.count}
		<button class="center mx-auto mt-5 block p-2" onclick={getNextBatch}
			>{m.red_pink_bear_play()}</button
		>
	{/if}
</Section>
