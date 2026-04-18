<script lang="ts">
	import Section from '$lib/Section.svelte';
	import ThreadTable from '$lib/ThreadTable.svelte';
	import { enumValues } from '$lib/enums.js';
	import { postCategoryNames } from '$lib/enums/postCategory.js';
	import { m } from '$lib/paraglide/messages.js';
	import { PostCategory } from '$lib/schema.js';

	let { data } = $props();
</script>

<Section title={m.just_salty_anaconda_nourish()} menuLinks={data.links}>
	{#each enumValues(PostCategory) as c, i (i)}
		{#if data.categories[c].length}
			<h2 class="mt-4 text-base">
				<a href="/post?category={i}">{postCategoryNames[c]()}</a>
			</h2>
			<ThreadTable posts={data.categories[c]} showAuthor={i > 0} />
		{/if}
	{/each}
</Section>
