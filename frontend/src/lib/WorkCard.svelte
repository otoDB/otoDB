<script lang="ts">
	import type { components } from './schema';
	import WorkTag from './WorkTag.svelte';
	import { m } from '$lib/paraglide/messages.js';

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
	<div
		class="bg-otodb-bg-color absolute top-full z-1 hidden w-full flex-wrap gap-1 p-2 px-4 group-hover:flex"
	>
		{#if work.tags.length > 0}
			{#each work.tags as tag, i (i)}
				<WorkTag {tag} />
			{/each}
		{:else}
			<span class="text-otodb-fainter-content">{m.mild_patchy_jaguar_trust()}</span>
		{/if}
	</div>
</div>
