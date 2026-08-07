<script lang="ts">
	import Pager from '$lib/Pager.svelte';
	import ModerationEventsTable from '$lib/ModerationEventsTable.svelte';
	import { page } from '$app/state';

	let { data } = $props();
</script>

<svelte:head>
	<meta name="robots" content="noindex" />
</svelte:head>

<ModerationEventsTable events={data.events} />

{#if data.events?.count}
	<Pager n_count={data.events.count} page_size={data.batchSize} base_url={page.url.toString()} />
{/if}
