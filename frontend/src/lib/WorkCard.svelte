<script lang="ts">
	import type { components } from './schema';
	import WorkTag from './WorkTag.svelte';

	interface Props {
		work: components['schemas']['WorkSchema'];
		class?: string;
	}
	const { work, ...props }: Props = $props();
</script>

<div
	class={[
		props.class,
		'group bg-otodb-bg-color relative row-span-2 grid grid-rows-subgrid gap-0'
	]}
>
	<a href="/work/{work.id}" class="flex h-full items-center">
		<img src={work.thumbnail} alt={work.title} class="aspect-video w-full object-cover" />
	</a>
	<a href="/work/{work.id}" class="my-2 line-clamp-2 self-center px-4">{work.title}</a>
	{#if work.tags}
		<div
			class="bg-otodb-bg-color absolute top-full z-1 hidden w-full flex-wrap gap-1 p-2 group-hover:flex"
		>
			{#each work.tags as tag, i (i)}
				<WorkTag {tag} />
			{/each}
		</div>
	{/if}
</div>
