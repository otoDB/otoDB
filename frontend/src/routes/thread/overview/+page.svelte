<script lang="ts">
	import Section from '$lib/Section.svelte';
	import ThreadTable from '$lib/ThreadTable.svelte';
	import { enumValues } from '$lib/enums.js';
	import { postCategoryNames } from '$lib/enums/postCategory.js';
	import { m } from '$lib/paraglide/messages.js';
	import { PostCategory } from '$lib/schema.js';

	let { data } = $props();

	const statusTabs: { key: typeof data.status; label: string }[] = [
		{ key: 'open', label: m.thread_overview_tab_open() },
		{ key: 'closed', label: m.thread_overview_tab_closed() }
	];
</script>

<Section title={m.just_salty_anaconda_nourish()} menuLinks={data.links}>
	<div class="mb-4 flex gap-2">
		{#each statusTabs as tab (tab.key)}
			<a
				href="?status={tab.key}"
				class={[
					'border px-3 py-1',
					data.status === tab.key ? 'bg-otodb-content-primary text-otodb-bg-primary' : ''
				]}
			>
				{tab.label}
			</a>
		{/each}
	</div>

	{#each enumValues(PostCategory) as c, i (i)}
		{#if data.categories[c].length}
			<h2 class="mt-4 text-base">
				<a href="/thread?category={i}">{postCategoryNames[c]()}</a>
			</h2>
			<ThreadTable posts={data.categories[c]} />
		{/if}
	{/each}
</Section>
