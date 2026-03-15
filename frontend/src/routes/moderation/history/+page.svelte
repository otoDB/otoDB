<script lang="ts">
	import Pager from '$lib/Pager.svelte';
	import ModerationEventsTable from '$lib/ModerationEventsTable.svelte';
	import { page } from '$app/state';

	let { data } = $props();
</script>

<ModerationEventsTable events={data.events} isEditor={data.isEditor} />

{#if data.events?.count}
	<Pager
		n_count={data.events.count}
		page={data.page}
		page_size={data.batchSize}
		base_url={page.url}
	/>
{/if}
