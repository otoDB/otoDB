<script lang="ts">
	import Section from '$lib/Section.svelte';
	import type { PageProps } from './$types';
	import { m } from '$lib/paraglide/messages.js';
	import client from '$lib/api';
	import { enhance } from '$app/forms';

	let { data }: PageProps = $props();
	const batch_size = 20;
	let results = $derived(data.results!.items);

	const getNextBatch = async () => {
		const { data: d } = await client.GET('/api/list/search', {
			fetch,
			params: { query: { query: data.query, limit: batch_size, offset: results.length } }
		});
		results = results.concat(d!.items);
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
	</form>
	<hr class="my-5" />

	<ul>
		{#each results as list, i (i)}
			<li><a href="/list/{list.id}">{list.name}</a></li>
		{/each}
	</ul>

	{#if results.length < data.results!.count}
		<button class="center mx-auto mt-5 block p-2" onclick={getNextBatch}
			>{m.red_pink_bear_play()}</button
		>
	{/if}
</Section>
