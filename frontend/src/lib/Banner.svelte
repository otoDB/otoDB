<script lang="ts">
	import type { Snippet } from 'svelte';

	type Variant = 'info' | 'warning' | 'danger' | 'caution';

	const VARIANT_CLASSES: Record<Variant, string> = {
		info: 'border-sky-600 bg-sky-600/10',
		warning: 'border-yellow-600 bg-yellow-600/10',
		danger: 'border-red-600 bg-red-600/10',
		caution: 'border-orange-600 bg-orange-600/10'
	};

	let {
		variant = 'info',
		title,
		children
	}: {
		variant?: Variant;
		title?: string;
		children?: Snippet;
	} = $props();
</script>

<div class={['mb-3 border px-4 py-2', VARIANT_CLASSES[variant]]}>
	{#if title}
		<div class="font-bold">{title}</div>
	{/if}
	{#if children}
		{@render children()}
	{/if}
</div>
