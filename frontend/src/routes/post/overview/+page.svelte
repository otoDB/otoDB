<script lang="ts">
	import Section from '$lib/Section.svelte';
	import ThreadTable from '$lib/ThreadTable.svelte';
	import { m } from '$lib/paraglide/messages.js';
	import { PostCategories } from '$lib/enums';

	let { data } = $props();
</script>

<Section title={m.just_salty_anaconda_nourish()} menuLinks={data.links}>
	{#each data.categories as c, i (i)}
		{#if c.length}
			<h2 class="mt-4 text-base">
				<a href="/post?category={i}">{PostCategories[i]()}</a>
			</h2>
			<ThreadTable posts={c} showAuthor={i > 0} />
		{/if}
	{/each}
</Section>
