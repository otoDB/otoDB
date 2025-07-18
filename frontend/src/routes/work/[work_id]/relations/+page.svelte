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
    ${links.map((r) => `${r.A_id} -->|${WorkRelationTypes[r.relation]()}| ${r.B_id}`).join('\n')}`
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
</script>

<Section
	title={m.mild_loud_shad_enchant({ type: m.grand_merry_fly_succeed(), name: data.title })}
	menuLinks={data.links}
>
	{#if data.works}
		<label>
			Distance:
			<input type="number" bind:value={deg} min="1" />
		</label>
		<label>
			Direction:
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
			<SVGViewer
				maxScale={90}
				height="600px"
				width="100%"
				svgClass="fill-transparent dark:fill-black"
			>
				<!-- eslint-disable-next-line svelte/no-at-html-tags -->
				{@html s.svg}
			</SVGViewer>
		{/await}
	{:else}
		<p>{m.left_watery_jellyfish_grip()}</p>
	{/if}
</Section>

<style>
	label.type-label {
		padding: 0 0.3rem;
		margin: 0.1rem;
		border: 1px solid var(--otodb-content-color);
		&:has(input:checked) {
			background-color: var(--otodb-content-color);
			color: var(--color-otodb-bg-color);
		}
		color: var(--otodb-content-color);
		background-color: var(--otodb-bg-color);
	}
</style>
