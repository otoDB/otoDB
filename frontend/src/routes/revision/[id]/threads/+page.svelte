<script lang="ts">
	import Pager from '$lib/Pager.svelte';
	import { m } from '$lib/paraglide/messages';
	import Section from '$lib/Section.svelte';
	import ThreadTable from '$lib/ThreadTable.svelte';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
</script>

<Section title="{m.arable_direct_swan_glow()} #{data.revision.id}" menuLinks={data.links}>
	<a href="/post/new?category=3&entity=r{data.revision.id}">{m.antsy_aloof_horse_grace()}</a>
	{#if data.threads.items.length}
		<ThreadTable
			posts={data.threads.items}
			entityFilter={(e) =>
				!(e.entity === 'revision' && String(e.id) === String(data.revision.id))}
		/>
		<Pager n_count={data.threads.count} page={data.page} page_size={data.batch_size} />
	{/if}
</Section>
