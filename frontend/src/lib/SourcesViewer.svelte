<script lang="ts">
	import WorkThumbnail from '$lib/WorkThumbnail.svelte';
	import ExternalEmbed from '$lib/ExternalEmbed.svelte';
	import { PlatformNames, WorkOriginNames } from '$lib/enums';
	import { m } from '$lib/paraglide/messages.js';
	import type { components } from '$lib/schema';

	interface Props {
		sources: components['schemas']['WorkSourceSchema'][];
		thumbnail?: string | null;
		thumbnailAlt?: string;
		width?: number;
		height?: number;
	}

	let {
		sources,
		thumbnail = null,
		thumbnailAlt = '',
		width = 480,
		height = 270
	}: Props = $props();

	let selected = $state(-1);

	$effect(() => {
		void sources;
		selected = -1;
	});

	let visibleSources = $derived(sources.filter((s) => s.work_status !== 1));
</script>

{#if selected === -1}
	<WorkThumbnail {thumbnail} alt={thumbnailAlt} class="h-[270px] w-[480px] object-cover" />
{:else}
	<ExternalEmbed {width} {height} src={visibleSources[selected]} />
{/if}
<div class="my-2 max-w-[480px]">
	<a
		href={thumbnail}
		target="_blank"
		rel="noopener noreferrer"
		class="cover_select"
		class:selected={selected === -1}
		onclick={(e) => {
			e.preventDefault();
			selected = -1;
		}}
	>
		{m.heroic_ideal_orangutan_aid()}
	</a>{#each visibleSources as s, i (i)}<a
			href={s.url}
			target="_blank"
			rel="noopener noreferrer"
			class="cover_select"
			class:selected={selected === i}
			onclick={(e) => {
				e.preventDefault();
				selected = i;
			}}
		>
			{PlatformNames[s.platform]}{s.work_origin === 0
				? ''
				: ' ' + WorkOriginNames[s.work_origin]()}
		</a>{/each}
</div>

<style>
	.cover_select {
		padding: 0.2rem 0.5rem;
		display: inline-block;
		background-color: var(--otodb-color-bg-primary);
		border: 1px solid var(--otodb-color-content-primary);
		text-decoration: none;
		&:hover {
			background-color: var(--otodb-color-bg-fainter);
		}
		&:active {
			background-color: var(--otodb-color-bg-faint);
		}
		&.selected {
			background-color: var(--otodb-color-content-primary);
			border: 1px solid var(--otodb-color-bg-primary);
			color: var(--otodb-color-bg-primary);
		}
	}
</style>
