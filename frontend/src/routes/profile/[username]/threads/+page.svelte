<script lang="ts">
	import Pager from '$lib/Pager.svelte';
	import { m } from '$lib/paraglide/messages';
	import { PostEntities } from '$lib/schema';
	import Section from '$lib/Section.svelte';
	import ThreadTable from '$lib/ThreadTable.svelte';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
</script>

<Section title={data.profile.username} type={m.fuzzy_crazy_cobra_lead()} menuLinks={data.links}>
	<a href="/post/new?category=3&entity=@{data.profile.username}">{m.antsy_aloof_horse_grace()}</a>
	{#if data.threads.items.length}
		<ThreadTable
			posts={data.threads.items}
			entityFilter={(e) =>
				!(
					e.entity === PostEntities.account &&
					String(e.id) === String(data.profile.username)
				)}
		/>
		<Pager n_count={data.threads.count} page={data.page} page_size={data.batch_size} />
	{/if}
</Section>
