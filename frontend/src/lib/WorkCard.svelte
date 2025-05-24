<script lang="ts">
	import type { components } from './schema';
	import WorkTag from './WorkTag.svelte';

	interface Props {
		work: components['schemas']['WorkSchema'];
		width: number;
	}
	const { work }: Props = $props();
</script>

<div class="card group relative row-span-2 grid grid-rows-subgrid bg-[var(--otodb-bg-color))]">
	<div class="">
		<a href="/work/{work.id}" class="block flex h-full items-center">
			<img src={work.thumbnail} alt={work.title} class="w-full" />
		</a>
	</div>
	<div class="px-4 py-2">
		<a href="/work/{work.id}" class="block">{work.title}</a>
	</div>
	<div
		class="tags absolute top-full z-1 hidden w-full flex-wrap gap-1 bg-[var(--otodb-bg-color))] p-2 group-hover:flex"
	>
		{#each work.tags as tag, i (i)}
			<WorkTag {tag} />
		{/each}
	</div>
</div>
