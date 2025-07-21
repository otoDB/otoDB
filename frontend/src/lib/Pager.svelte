<script lang="ts">
	let { page, page_size, n_count, window_size = 2 } = $props();

	const n_pages = $derived(Math.ceil(n_count / page_size));
	const page_min = $derived(Math.max(0, page - window_size));
	const page_max = $derived(Math.min(n_pages, page + window_size + 1));
	const page_range = $derived(
		Array.from({ length: page_max - page_min }, (_, i) => i + page_min + 1)
	);
</script>

{#if page_range.length > 1}
	<div class="mt-3 flex justify-center gap-2">
		{#each page_range as index, i (i)}
			{#if index - 1 === page}
				{index}
			{:else}
				<a href="?page={index}">{index}</a>
			{/if}
		{/each}
	</div>
{/if}
