<script lang="ts">
	import type { components } from './schema';
	import WorkTag from './WorkTag.svelte';
	import DisplayText from './DisplayText.svelte';
	import WorkThumbnail from './WorkThumbnail.svelte';
	import { m } from '$lib/paraglide/messages.js';
	import { getDisplayText } from './api';

	interface Props {
		work: components['schemas']['WorkSchema'];
		class?: string;
	}
	const { work, ...props }: Props = $props();
</script>

<div
	class={[
		props.class,
		'group bg-otodb-bg-primary relative row-span-2 grid size-full grid-rows-subgrid gap-0'
	]}
>
	<a href="/work/{work.id}" tabindex="-1" class="flex h-full items-center">
		<WorkThumbnail
			thumbnail={work.thumbnail}
			alt={getDisplayText(work.title)}
			class="aspect-video h-full object-cover min-w-full"
		/>
	</a>
	<a href="/work/{work.id}" class="my-2 line-clamp-2 self-center px-4"
		><DisplayText value={work.title} /></a
	>
	<!-- Caller can choose to not supply tags -->
	{#if work.tags}
		<div
			class="bg-otodb-bg-primary absolute top-full z-1 hidden w-full flex-wrap px-4 py-2 group-hover:block"
		>
			{#if work.tags.length > 0}
				<div class="flex flex-wrap items-center gap-1">
					{#each work.tags.slice(0, 8) as tag, i (i)}
						<WorkTag {tag} />
					{/each}
					{#if work.tags.length > 8}
						<span class="px-1 text-sm">
							{m.icy_each_pigeon_transform({ count: work.tags.length - 8 })}
						</span>
					{/if}
				</div>
			{:else}
				<span class="text-otodb-content-fainter">{m.mild_patchy_jaguar_trust()}</span>
			{/if}
		</div>
	{/if}
</div>
