<script lang="ts">
	import Pager from '$lib/Pager.svelte';
	import { m } from '$lib/paraglide/messages';
	import Section from '$lib/Section.svelte';
	import ThreadTable from '$lib/ThreadTable.svelte';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
</script>

<Section title={data.tag.name} type={m.big_tiny_kitten_devour()} menuLinks={data.links}>
	<a href="/post/new?category=3&entity=[[{data.tag.slug}]]">{m.antsy_aloof_horse_grace()}</a>
	{#if data.threads.items.length}
		<ThreadTable
			posts={data.threads.items}
			entityFilter={(e) => !(e.entity === 'tagwork' && e.id === data.tag.slug)}
		/>
		<Pager n_count={data.threads.count} page={data.page} page_size={data.batch_size} />
	{/if}
</Section>
