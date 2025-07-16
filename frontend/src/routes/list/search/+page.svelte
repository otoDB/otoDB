<script lang="ts">
	import Section from '$lib/Section.svelte';
	import type { PageProps } from './$types';
	import { m } from '$lib/paraglide/messages.js';
	import client from '$lib/api';
	import LoadMoreButton from '$lib/LoadMoreButton.svelte';

	let { data }: PageProps = $props();
	let results = $derived(data.results!.items);

	const fetchNextBatch = () =>
		client.GET('/api/list/search', {
			fetch,
			params: { query: { query: data.query, limit: data.batch_size, offset: results.length } }
		});
</script>

<svelte:head>
	<title>{m.mean_top_antelope_love()}</title>
</svelte:head>

<Section
	title={m.mean_top_antelope_love()}
	menuLinks={[
		{ title: m.grand_merry_fly_succeed(), pathname: `work/search?query=${data.query}` },
		{ title: m.empty_legal_chicken_taste(), pathname: `tag/search?query=${data.query}` },
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

	<table class="w-full">
		<thead>
			<tr>
				<th>{m.large_factual_octopus_exhale()}</th>
				<th>{m.crisp_red_canary_tickle()}</th>
			</tr>
		</thead><tbody>
			{#each results as list, i (i)}
				<tr>
					<td><a href="/list/{list.id}">{list.name}</a></td>
					<td><a href="/profile/{list.author.username}">{list.author.username}</a></td>
				</tr>
			{/each}
		</tbody>
	</table>
	<LoadMoreButton bind:results maxCount={data.results!.count} {fetchNextBatch} />
</Section>
