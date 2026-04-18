<script lang="ts" generics="T extends 'work' | 'song'">
	import { m } from '$lib/paraglide/messages.js';
	import { enumValues, SongRelationNames, WorkRelationNames } from '$lib/enums.js';
	import { getDisplayText } from '$lib/api';
	import mermaid from 'mermaid';
	import elkLayouts from '@mermaid-js/layout-elk';
	import { onMount } from 'svelte';
	import { SVGViewer } from 'svelte-svg-viewer';
	import { SongRelationTypes, WorkRelationTypes, type components } from '$lib/schema';

	type Work = components['schemas']['SlimWorkSchema'];
	type Song = components['schemas']['SongSchema'];
	type RelationType = T extends 'work' ? WorkRelationTypes : SongRelationTypes;
	type Node = (T extends 'work' ? Work : Song) & { distance?: number };
	type Edge = { A_id: number; B_id: number; relation: RelationType };
	interface Props {
		id: number;
		type: 'work' | 'song';
		min_height?: number;
		defaultDir: 'TB' | 'LR';
		objects: Node[];
		relations: Edge[];
	}
	let { id, objects, relations, defaultDir = 'TB', type, min_height = 600 }: Props = $props();

	const [RelationTypes, RelationNames] =
		type === 'work'
			? [WorkRelationTypes, WorkRelationNames]
			: [SongRelationTypes, SongRelationNames];

	let deg = $state(1);
	let direction = $state(defaultDir);
	let allowed_types: RelationType[] = $state(enumValues(RelationTypes) as RelationType[]);

	const get_svg_mermaid = (nodes: Node[], links: Edge[], ext: number[]) =>
		mermaid.render(
			'Relations',
			`---
config:
  layout: elk
  elk:
    mergeEdges: true
---
flowchart ${direction}
    style ${id} color:#f00
	classDef moreNodes fill:none,stroke:none;
	classDef untitled font-style:italic;` +
				(type === 'work'
					? `
    ${(nodes as Work[])
		.map(
			(w) => `${w.id}@{ ${w.thumbnail ? `img: "${w.thumbnail}",` : ''} constraint: on, w: 10 }
    ${w.id}["${getDisplayText(w.title).replaceAll('"', '#quot;')}"]${w.title == null ? ':::untitled' : ''}
    click ${w.id} "${`/work/${w.id}`}"`
		)
		.join('\n')}
    ${links
		.map((r) =>
			//  Reverse relation for 'sequel'
			r.relation === 0
				? `${r.B_id} _${r.B_id}_${r.A_id}_@-->|${RelationNames[r.relation]()}| ${r.A_id}`
				: `${r.A_id} _${r.A_id}_${r.B_id}_@-->|${RelationNames[r.relation]()}| ${r.B_id}`
		)
		.join('\n')}
	${ext
		.map(
			(a) => `${a}MORE["${m.fresh_deft_warbler_edit()}"]
	class ${a}MORE moreNodes;
	${a > 0 ? `${a}MORE -.- ${a}` : `${-a} -.- ${a}MORE`}`
		)
		.join('\n')}`
					: `
    ${nodes
		.map(
			(
				w
			) => `${w.id}["${getDisplayText(w.title).replaceAll('"', '#quot;')}"]${w.title == null ? ':::untitled' : ''}
    click ${w.id} "${`/tag/${(w as Song).work_tag}`}"`
		)
		.join('\n')}
    ${links.map((r) => `${r.A_id} -->|${RelationNames[r.relation]()}| ${r.B_id}`).join('\n')}`)
		);

	const mermaid_BFS = (
		ns: Node[],
		ls: Edge[],
		start: number,
		max_distance: number = Number.POSITIVE_INFINITY
	): [(Node & { distance: number })[], Edge[], number[]] => {
		const nodes = structuredClone(ns),
			links = structuredClone(ls);
		let queue = [[start, 0]];
		while (queue.length) {
			const next_queue = [];
			for (const [n, curr_distance] of queue) {
				const ng = nodes.find((nn) => nn.id === n)!;
				if (curr_distance > max_distance || ng.distance !== undefined) continue;
				ng.distance = curr_distance;
				next_queue.push(
					...[
						...new Set(
							links
								.filter(
									(v) =>
										allowed_types.includes(v.relation) &&
										(v.A_id === n || v.B_id === n)
								)
								.flatMap((v) => [v.A_id, v.B_id])
						)
					].map((nn) => [nn, curr_distance + 1])
				);
			}
			queue = next_queue;
		}
		return [
			nodes.filter((v) => v.distance !== undefined) as (Node & { distance: number })[],
			links.filter(
				(v) =>
					allowed_types.includes(v.relation) &&
					nodes.find((w) => w.id === v.A_id)?.distance !== undefined &&
					nodes.find((w) => w.id === v.B_id)?.distance !== undefined
			),
			[
				...new Set(
					links
						.filter((v) => allowed_types.includes(v.relation))
						.map((v) => [v.A_id, v.B_id].map((n) => nodes.find((w) => w.id === n)!))
						.filter(
							([a, b]) => (a.distance === undefined) !== (b.distance === undefined)
						)
						.map(([a, b]) => (a.distance !== undefined ? a.id : -b.id))
				)
			]
		];
	};

	const max_distance = $derived(
		Math.max(...mermaid_BFS(objects, relations, id)[0].map((n) => n.distance))
	);

	let distance = $derived(Math.max(Math.min(deg, max_distance), 1));

	let [nodes, links, ext] = $derived(mermaid_BFS(objects, relations, id, distance));
	let svg = $derived(get_svg_mermaid(nodes, links, ext));

	onMount(() => {
		mermaid.initialize({ maxTextSize: 1000000, startOnLoad: false, theme: 'base' });
		mermaid.registerLayoutLoaders(elkLayouts);
	});

	let svgContainer = $state<HTMLDivElement | undefined>(undefined);

	function svgMouseOver(event: MouseEvent) {
		const target = event.target as HTMLElement;
		const node = target.closest('[id^="flowchart-"]');
		const label: HTMLElement | null = target.closest('.label:has(.edgeLabel)');

		if (svgContainer) {
			if (node) {
				// Extract numeric ID from node ID (e.g. "flowchart-1-0" -> "1")
				const nodeId = node.id.split('-')[1];
				if (nodeId) {
					const links = svgContainer.querySelectorAll(`[id*="_${nodeId}_"]`);
					links.forEach((link) => {
						link.classList.add('highlighted');
					});
					const labels = svgContainer.querySelectorAll(`[data-id*="_${nodeId}_"]`);
					labels.forEach((link) => {
						link.classList.add('highlighted');
					});
				}
			}
			if (label) {
				const edge = svgContainer.querySelector(`[data-id="${label.dataset.id}"`)!;
				edge.classList.add('highlighted');
				label.classList.add('highlighted');
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

	let svg_height = $state(min_height),
		old_svg_height = svg_height;
	let svg_resizing_begin = -1;
</script>

<label>
	{m.just_grassy_mantis_slurp()}
	<input type="number" bind:value={deg} min="1" max={max_distance} /> / {max_distance}
</label>
<label class="mt-2 mb-2 block">
	{m.fair_aware_salmon_twist()}
	<select bind:value={direction}
		><option value="LR">{m.top_front_ray_treasure()}</option><option value="TB"
			>{m.stout_jumpy_ox_feel()}</option
		></select
	>
</label>
{m.mild_loud_shad_enchant({ type: m.mellow_upper_finch_drip(), name: '' })}
<select multiple bind:value={allowed_types}>
	{#each enumValues(RelationTypes) as t, i (i)}
		<option value={t} class="type-label">{RelationNames[t]()}</option>
	{/each}
</select>
{#await svg}
	{m.sunny_light_duck_surge()}
{:then s}
	<div
		class="mt-2"
		bind:this={svgContainer}
		onmouseover={svgMouseOver}
		onmouseout={svgMouseOut}
		role="main"
		onblur={() => {}}
		onfocus={() => {}}
	>
		<button
			class="absolute right-0 bottom-0 hidden cursor-ns-resize text-3xl md:block"
			onmousedown={(e) => {
				svg_resizing_begin = e.clientY;
				old_svg_height = svg_height;
			}}>↕</button
		>
		<SVGViewer resizeBehavior="zoom" maxScale={90} height={`${svg_height}px`} width="100%">
			<!-- eslint-disable-next-line svelte/no-at-html-tags -->
			{@html s.svg}
		</SVGViewer>
	</div>
{/await}

<svelte:body
	onmouseup={() => {
		svg_resizing_begin = -1;
	}}
	onmousemove={(e) => {
		if (svg_resizing_begin >= 0) {
			svg_height = Math.max(min_height, old_svg_height + e.clientY - svg_resizing_begin);
		}
	}}
/>

<style>
	@reference "../app.css";
	option.type-label {
		&:checked {
			@apply text-otodb-bg-primary;
			@apply bg-otodb-content-primary;
		}
		@apply bg-otodb-bg-primary;
		@apply text-otodb-content-primary;
	}
	:global(svg#svg-viewer) {
		& .highlighted {
			stroke: #f00 !important;
			stroke-width: 2px !important;
		}
		& > rect:first-child {
			@apply fill-otodb-bg-primary;
		}
		& #Relations .icon-shape p,
		& #Relations .image-shape span {
			@apply bg-otodb-bg-fainter;
			@apply text-otodb-content-primary;
			@apply fill-otodb-content-primary;
		}
		& #Relations .image-shape p {
			color: inherit;
			background-color: inherit;
			fill: inherit;
		}
		& #Relations .flowchart-link {
			@apply stroke-otodb-content-fainter;
		}
		& #Relations .edgeLabel,
		& #Relations .edgeLabel p {
			@apply text-otodb-content-primary;
			@apply fill-otodb-content-primary;
			@apply stroke-otodb-content-fainter;
			@apply bg-otodb-bg-fainter;
		}
		& #Relations .edgeLabel .label.highlighted {
			outline: #f00 1px solid !important;
		}
		& #Relations .marker {
			@apply stroke-otodb-content-faint;
			@apply fill-otodb-content-faint;
		}
		& #Relations g.moreNodes p {
			@apply text-otodb-content-primary;
		}
	}
</style>
