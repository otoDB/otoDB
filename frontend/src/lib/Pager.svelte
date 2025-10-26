<script lang="ts">
	let { page, page_size, n_count, window_size = 2, base_url = null } = $props();

	const n_pages = $derived(Math.ceil(n_count / page_size));
	const page_min = $derived(Math.max(1, page - window_size));
	const page_max = $derived(Math.min(n_pages, page + window_size));
	const page_range = $derived(
		Array.from({ length: page_max - page_min + 1 }, (_, i) => i + page_min)
	);
	const url = (page: number) => {
		if (!base_url) return `?page=${page}`;
		const u = new URL(base_url);
		u.searchParams.set('page', page.toString());
		return u.href;
	};

	let pp = $derived(page);
</script>

{#snippet btn(p)}
	<a class="bg-otodb-bg-fainter border-otodb-content-faint border p-2" href={url(p)}>{p}</a>
{/snippet}

{#if page_range.length > 1}
	<div class="mt-3 flex justify-center gap-2">
		{#if page_range[0] !== 1}
			{@render btn(1)}
			{#if page_range[0] !== 2}
				...
			{/if}
		{/if}
		{#each page_range as index, i (i)}
			{#if index === page}
				<form target="_self" method="get">
					<input
						class="p-2"
						type="number"
						name="page"
						min="1"
						max={n_pages}
						bind:value={pp}
					/>
				</form>
			{:else}
				{@render btn(index)}
			{/if}
		{/each}

		{#if page_range.at(-1) !== n_pages}
			{#if page_range.at(-1) !== n_pages - 1}
				...
			{/if}
			{@render btn(n_pages)}
		{/if}
	</div>
{/if}
