<script lang="ts">
	import Section from '$lib/Section.svelte';
	import type { PageProps } from './$types';
	import { m } from '$lib/paraglide/messages.js';
	import Pager from '$lib/Pager.svelte';

	let { data }: PageProps = $props();
</script>

<svelte:head>
	<title>{m.free_keen_wren_exhale()}</title>
</svelte:head>

<Section title={m.free_keen_wren_exhale()}>
	<table class="w-full">
		<tbody>
			{#each data.notifications as n, i (i)}
				<tr><td>{JSON.stringify(n)}</td></tr>
			{/each}
		</tbody>
	</table>
	<!-- {#if data.results?.count}
		<Pager
			n_count={data.results.count}
			page={data.page}
			page_size={data.batch_size}
			base_url={page.url}
		/>
	{/if} -->
</Section>
