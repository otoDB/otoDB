<script lang="ts">
	import Section from '$lib/Section.svelte';
	import { WorkRelationTypes } from '$lib/enums.js';
	import { m } from '$lib/paraglide/messages.js';
	import { mermaid_BFS } from '$lib/ui.js';
	import mermaid from 'mermaid';
	import { onMount } from 'svelte';
	import { SVGViewer } from 'svelte-svg-viewer';
	let { data } = $props();

	let works = data.works?.map((o) => ({ visited: false, ...o }));
	let deg = $state(2);
	let direction = $state('TB');
	let allowed_types = $state(new Array(WorkRelationTypes.length).fill(true));

	const get_svg_mermaid = (nodes, links) =>
		mermaid.render(
			'Relations',
			`flowchart ${direction}
    style ${data.id} color:#f00
${nodes
	.map(
		(w) => `${w.id}@{ img: "${w.thumbnail}", constraint: on, w: 10 }
    ${w.id}["${w.title.replaceAll('"', '#quot;')}"]
    click ${w.id} "${`/work/${w.id}`}"`
	)
	.join('\n')}
    ${links.map((r) => `${r.A_id} _${r.A_id}_${r.B_id}_@-->|${WorkRelationTypes[r.relation]()}| ${r.B_id}`).join('\n')}`
		);

	let svg = $derived.by(() => {
		if (!works) return;
		const [nodes, links] = mermaid_BFS(
			structuredClone(works),
			structuredClone(data.relations),
			data.id,
			deg,
			allowed_types
		);
		return get_svg_mermaid(nodes, links);
	});

	onMount(() => {
		if (works)
			mermaid.initialize({ maxTextSize: 1000000, startOnLoad: false, theme: 'neutral' });
	});

	let svgContainer = $state<HTMLDivElement | undefined>(undefined);

	function svgMouseOver(event: MouseEvent) {
		const target = event.target as HTMLElement;
		const node = target.closest('[id^="flowchart-"]');

		if (node && svgContainer) {
			// Extract numeric ID from node ID (e.g. "flowchart-1-0" -> "1")
			const nodeId = node.id.split('-')[1];
			if (nodeId) {
				const links = svgContainer.querySelectorAll(`[id*="_${nodeId}_"]`);
				links.forEach((link) => {
					link.classList.add('highlighted');
				});
			}
		}
	}

	function svgMouseOut() {
		if (svgContainer) {
			const highlightedLinks = svgContainer.querySelectorAll('.highlighted');
			highlightedLinks.forEach((link) => {
				link.classList.remove('highlighted');
			});
		}
	}
</script>

<Section
	title={m.mild_loud_shad_enchant({ type: m.grand_merry_fly_succeed(), name: data.title })}
	menuLinks={data.links}
>
	{#if data.works}
		<label>
			{m.just_grassy_mantis_slurp()}
			<input type="number" bind:value={deg} min="1" />
		</label>
		<label>
			{m.fair_aware_salmon_twist()}
			<select bind:value={direction}
				><option value="LR">{m.top_front_ray_treasure()}</option><option value="TB"
					>{m.stout_jumpy_ox_feel()}</option
				></select
			>
		</label>
		{#each WorkRelationTypes as t, i (i)}
			<label class="type-label">
				<input type="checkbox" class="hidden" bind:checked={allowed_types[i]} />
				{t()}
			</label>
		{/each}
		{#await svg}
			{m.sunny_light_duck_surge()}
		{:then s}
			<div bind:this={svgContainer} on:mouseover={svgMouseOver} on:mouseout={svgMouseOut}>
				<SVGViewer
					maxScale={90}
					height="600px"
					width="100%"
					svgClass="fill-transparent dark:fill-black"
				>
					<!-- eslint-disable-next-line svelte/no-at-html-tags -->
					{@html s.svg}
				</SVGViewer>
			</div>
		{/await}
	{:else}
		<p>{m.left_watery_jellyfish_grip()}</p>
	{/if}
</Section>

<style>
	label.type-label {
		padding: 0 0.3rem;
		margin: 0.1rem;
		border: 1px solid var(--otodb-color-content-primary);
		&:has(input:checked) {
			background-color: var(--otodb-color-content-primary);
			color: var(--color-otodb-bg-primary);
		}
		color: var(--otodb-color-content-primary);
		background-color: var(--otodb-color-bg-primary);
	}
	:global(.highlighted) {
		stroke: #f00 !important;
		stroke-width: 2px !important;
	}
</style>
