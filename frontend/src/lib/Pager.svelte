<script lang="ts">
	let { page, page_size, n_count, window_size = 2 } = $props();

	const n_pages = $derived(Math.ceil(n_count / page_size));
	const page_min = $derived(Math.max(1, page - window_size));
	const page_max = $derived(Math.min(n_pages - 1, page + window_size));
	const page_range = $derived(
		Array.from({ length: page_max - page_min + 1 }, (_, i) => i + page_min)
	);
</script>

{#if page_range.length > 1}
	<div class="mt-3 flex justify-center gap-2">
		{#each page_range as index, i (i)}
			{#if index === page}
				{index}
			{:else}
				<a href="?page={index}">{index}</a>
			{/if}
		{/each}
	</div>
{/if}
