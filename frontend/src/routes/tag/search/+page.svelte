<script lang="ts">
	import Section from '$lib/Section.svelte';
	import type { PageProps } from './$types';
	import { m } from '$lib/paraglide/messages.js';
	import WorkTag from '$lib/WorkTag.svelte';

	let { data }: PageProps = $props();
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
	<form tagert="_self" method="get">
		<input
			type="text"
			name="query"
			placeholder="{m.mean_top_antelope_love()}..."
			value={data.query}
		/>
	</form>

	<div class="flex flex-wrap gap-3">
		{#each data.results.items as tag, i (i)}
			<WorkTag {tag} />
		{/each}
	</div>
</Section>
