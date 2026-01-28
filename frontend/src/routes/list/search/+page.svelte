<script lang="ts">
	import Section from '$lib/Section.svelte';
	import type { PageProps } from './$types';
	import { m } from '$lib/paraglide/messages.js';
	import Pager from '$lib/Pager.svelte';
	import { page } from '$app/state';

	let { data }: PageProps = $props();
</script>

<svelte:head>
	<title
		>{m.mild_loud_shad_enchant({
			type: m.mean_top_antelope_love(),
			name: m.stale_loose_squid_cut()
		})}</title
	>
</svelte:head>

<Section
	title={m.stale_loose_squid_cut()}
	type={m.mean_top_antelope_love()}
	menuLinks={[
		{ title: m.grand_merry_fly_succeed(), pathname: `work/search?query=${data.query}` },
		{ title: m.empty_legal_chicken_taste(), pathname: `tag/search?query=${data.query}` },
		{ title: m.grand_nice_pony_belong(), pathname: `song/search?query=${data.query}` },
		{
			title: m.dull_plain_angelfish_cuddle(),
			pathname: `song_attribute/search?query=${data.query}`
		},
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
			{#each data.results?.items as list, i (i)}
				<tr>
					<td><a href="/list/{list.id}">#{list.id} - {list.name}</a></td>
					<td><a href="/profile/{list.author.username}">{list.author.username}</a></td>
				</tr>
			{/each}
		</tbody>
	</table>
	{#if data.results?.count}
		<Pager
			n_count={data.results.count}
			page={data.page}
			page_size={data.batch_size}
			base_url={page.url}
		/>
	{/if}
</Section>
