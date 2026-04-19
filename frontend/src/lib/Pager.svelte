<script lang="ts">
	import { goto } from '$app/navigation';

	let {
		page,
		page_size,
		n_count,
		window_size = 2,
		base_url = null
	}: {
		page: number;
		n_count: number;
		page_size: number;
		window_size?: number;
		base_url?: string | null;
	} = $props();

	const n_pages = $derived(Math.ceil(n_count / page_size));

	const middle = $derived.by(() => {
		const min = Math.max(1, page - window_size);
		const max = Math.min(n_pages, page + window_size);

		return Array.from({ length: max - min + 1 }, (_, i) => i + min);
	});

	const buildUrl = (page: number) => {
		if (!base_url) return `?page=${page}`;
		const u = new URL(base_url);
		u.searchParams.set('page', page.toString());
		return u.href;
	};
</script>

{#snippet btn(p: number, current: boolean)}
	<a
		aria-current={current ? 'page' : undefined}
		href={buildUrl(p)}
		class="bg-otodb-bg-primary border-otodb-content-faint aria-[current=page]:border-otodb-content-fainter aria-[current=page]:bg-otodb-bg-fainter hover:bg-otodb-bg-fainter aria-[current=page]:text-otodb-content-fainter text-otodb-content-primary border px-4
		py-2 no-underline"
	>
		{p}
	</a>
{/snippet}

{#if middle.length > 1}
	<div class="mt-3 flex flex-nowrap items-center justify-center gap-x-2">
		{#if middle[0] !== 1}
			{@render btn(1, false)}
			{#if middle[0] !== 2}
				<span class="text-otodb-content-fainter">&hellip;</span>
			{/if}
		{/if}

		{#each middle as index (index)}
			{@render btn(index, index === page)}
		{/each}

		{#if middle.at(-1) !== n_pages}
			{#if middle.at(-1) !== n_pages - 1}
				<span class="text-otodb-content-fainter">&hellip;</span>
			{/if}
			{@render btn(n_pages, false)}
		{/if}
	</div>
{/if}
