<script lang="ts">
	import type { components } from './schema';
	import WorkTag from './WorkTag.svelte';

	interface Props {
		work: components['schemas']['WorkSchema'];
	}
	const { work }: Props = $props();
</script>

<div class="group relative row-span-2 grid grid-rows-subgrid gap-0 bg-[var(--otodb-bg-color))]">
	<a href="/work/{work.id}" class="flex h-full items-center">
		<img src={work.thumbnail} alt={work.title} class="aspect-video w-full object-cover" />
	</a>
	<a href="/work/{work.id}" class="my-2 line-clamp-2 self-center px-4">{work.title}</a>
	<div
		class="absolute top-full z-1 hidden w-full flex-wrap gap-1 bg-[var(--otodb-bg-color))] p-2 group-hover:flex"
	>
		{#each work.tags as tag, i (i)}
			<WorkTag {tag} />
		{/each}
	</div>
</div>
