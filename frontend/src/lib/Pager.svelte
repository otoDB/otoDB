<script lang="ts">
	import { goto } from '$app/navigation';
	import { page as page_state } from '$app/state';
	let {
		page_size,
		n_count,
		window_size = 2,
		base_url = null,
		param_name = 'page'
	}: {
		n_count: number;
		page_size: number;
		window_size?: number;
		base_url?: string | null;
		param_name?: string;
	} = $props();

	const page = $derived(parseInt(page_state.url.searchParams.get(param_name) ?? '0', 10) || 1);
	const n_pages = $derived(Math.ceil(n_count / page_size));
	const page_min = $derived(Math.max(1, page - window_size));
	const page_max = $derived(Math.min(n_pages, page + window_size));
	const range = (from: number, to: number) =>
		Array.from({ length: to - from + 1 }, (_, i) => i + from);

	const buildUrl = (page: number) => {
		if (!base_url) return `?${param_name}=${page}`;
		// Accept either an absolute URL or a path-only base (e.g. "/thread/13")
		const u = new URL(base_url, page_state.url.origin);
		u.searchParams.set(param_name, page.toString());
		return u.href;
	};

	let pp = $derived(page);
</script>

{#snippet btn(p: number)}
	<a class="bg-otodb-bg-fainter border-otodb-content-faint border p-2" href={buildUrl(p)}>{p}</a>
{/snippet}

{#if n_pages > 1}
	<div class="mt-3 grid grid-cols-[1fr_auto_1fr] gap-2 tabular-nums">
		<div class="flex justify-end gap-2">
			{#if page_min > 1}
				{@render btn(1)}
				{#if page_min > 2}
					...
				{/if}
			{/if}
			{#each range(page_min, page - 1) as p (p)}
				{@render btn(p)}
			{/each}
		</div>
		<input
			autocomplete="off"
			class="p-2"
			type="number"
			min="1"
			max={n_pages}
			bind:value={pp}
			onchange={() => goto(buildUrl(pp))}
		/>
		<div class="flex gap-2">
			{#each range(page + 1, page_max) as p (p)}
				{@render btn(p)}
			{/each}
			{#if page_max < n_pages}
				{#if page_max < n_pages - 1}
					...
				{/if}
				{@render btn(n_pages)}
			{/if}
		</div>
	</div>
{/if}
