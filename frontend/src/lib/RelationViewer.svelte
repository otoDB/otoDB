<script lang="ts" generics="T extends 'work' | 'song'">
	import { enumValues, SongRelationNames, WorkRelationNames } from '$lib/enums.js';
	import { m } from '$lib/paraglide/messages.js';
	import {
		SongRelationTypes,
		WorkRelationTypes,
		type components,
		GraphViewBackends
	} from '$lib/schema';
	import { getDisplayText } from '$lib/ui';
	import elkLayouts from '@mermaid-js/layout-elk';
	import mermaid from 'mermaid';
	import { onMount } from 'svelte';
	import { SVGViewer } from 'svelte-svg-viewer';
	import * as Viz from '@viz-js/viz';

	type Work = Omit<components['schemas']['SlimWorkSchema'], 'status'>;
	type Song = components['schemas']['SongSchema'];
	type RelationType = T extends 'work' ? WorkRelationTypes : SongRelationTypes;
	type Node = (T extends 'work' ? Work : Song) & { distance?: number };
	type Edge = { A_id: string; B_id: string; relation: RelationType };
	interface Props {
		id: string;
		type: 'work' | 'song';
		min_height?: number;
		defaultDir?: 'TB' | 'LR';
		objects: Node[];
		relations: Edge[];
		backend?: GraphViewBackends;
	}
	let {
		id,
		objects,
		relations,
		defaultDir,
		type,
		min_height = 600,
		backend = GraphViewBackends.Graphviz
	}: Props = $props();

	const RelationTypes = $derived(type === 'work' ? WorkRelationTypes : SongRelationTypes);
	const RelationNames = $derived(type === 'work' ? WorkRelationNames : SongRelationNames);

	let deg = $state(1);
	let show_thumbs = $state(true);
	let allowed_types: RelationType[] = $state(enumValues(RelationTypes) as RelationType[]);

	const get_svg_mermaid = (nodes: Node[], links: Edge[], ext: string[]) =>
		mermaid
			.render(
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
											(
												w
											) => `${w.id}@{ ${show_thumbs && w.thumbnail ? `img: "${w.thumbnail}",` : ''} constraint: on, w: 10 }
    ${w.id}["${getDisplayText(w.title).replaceAll('"', '#quot;')}"]${w.title === null ? ':::untitled' : ''}
    click ${w.id} "${`/work/${w.id}`}"`
										)
										.join('\n')}
    ${links
										.map((r) =>
											//  Reverse relation for 'sequel'
											r.relation === WorkRelationTypes.Sequel
												? `${r.B_id} _${r.B_id}_${r.A_id}_@-->|${RelationNames[r.relation]()}| ${r.A_id}`
												: `${r.A_id} _${r.A_id}_${r.B_id}_@-->|${RelationNames[r.relation]()}| ${r.B_id}`
										)
										.join('\n')}
	${ext
									.map(
										(a) => `${a}MORE["${m.fresh_deft_warbler_edit()}"]
	class ${a}MORE moreNodes;
	${a[0] !== '-' ? `${a}MORE -.- ${a}` : `${-a} -.- ${a}MORE`}`
									)
									.join('\n')}`
						: `
    ${nodes
										.map(
											(
												w
											) => `${w.id}["${getDisplayText(w.title).replaceAll('"', '#quot;')}"]${w.title === null ? ':::untitled' : ''}
    click ${w.id} "${`/tag/${(w as Song).work_tag}`}"`
										)
										.join('\n')}
    ${links.map((r) => `${r.A_id} -->|${RelationNames[r.relation]()}| ${r.B_id}`).join('\n')}`)
			)
			.then((r) => r.svg);

	const relation_BFS = (
		ns: Node[],
		ls: Edge[],
		start: string,
		max_distance: number = Number.POSITIVE_INFINITY
	): [(Node & { distance: number })[], Edge[], string[]] => {
		const nodes = structuredClone(ns),
			links = structuredClone(ls);
		let queue: [string, number][] = [[start, 0]];
		while (queue.length) {
			const next_queue: [string, number][] = [];
			for (const [n, curr_distance] of queue) {
				const ng = nodes.find((nn) => nn.id === n)!;
				if (curr_distance > max_distance || ng.distance !== undefined) continue;
				ng.distance = curr_distance;
				next_queue.push(
					...[
						...new Set(
							links
								.filter((v) => allowed_types.includes(v.relation) && (v.A_id === n || v.B_id === n))
								.flatMap((v) => [v.A_id, v.B_id])
						)
					].map((nn) => [nn, curr_distance + 1] as [string, number])
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
						.filter(([a, b]) => (a.distance === undefined) !== (b.distance === undefined))
						.map(([a, b]) => (a.distance !== undefined ? a.id : '-' + b.id))
				)
			]
		];
	};

	const max_distance = $derived(
		Math.max(...relation_BFS(objects, relations, id)[0].map((n) => n.distance))
	);

	let distance = $derived(Math.max(Math.min(deg, max_distance), 1));

	let [nodes, links, ext] = $derived(relation_BFS(objects, relations, id, distance));

	// heuristic from VNDB's `gen_dot`
	const auto_dir = $derived.by(() => {
		const fanout = new Map<string, number>();
		for (const l of links) {
			fanout.set(l.A_id, (fanout.get(l.A_id) ?? 0) + 1);
			fanout.set(l.B_id, (fanout.get(l.B_id) ?? 0) + 1);
		}
		return Math.max(0, ...fanout.values()) > 6 ? 'LR' : 'TB';
	});
	let direction = $derived(defaultDir ?? auto_dir);

	const gv_font = 'Arial';
	// A node and each of its edges share a rel_<id> class, which is how hovering one finds the other
	const rel_class = (...ids: string[]) => ids.map((i) => `rel_${i}`).join(' ');
	const gv_thumb = (ob: Node) =>
		show_thumbs && type === 'work' ? ((ob as Work).thumbnail ?? null) : null;
	const gv_node = (ob: Node, url: string) => {
		const thumb = gv_thumb(ob);
		return {
			name: ob.id,
			attributes: {
				label: getDisplayText(ob.title),
				tooltip: getDisplayText(ob.title),
				URL: url,
				class: `${rel_class(ob.id)}${ob.title === null ? ' untitled' : ''}${thumb ? ' thumb' : ''}`,
				...(ob.id === id ? { id: 'graph_current' } : {}),
				...(thumb ? { image: thumb, imagescale: 'true', imagepos: 'tc', labelloc: 'b' } : {})
			}
		};
	};
	const gv_more_node = (a: string) => ({
		name: `more:${a}`,
		attributes: { label: m.fresh_deft_warbler_edit(), shape: 'plaintext' }
	});
	const gv_more_edge = (a: string) =>
		a[0] === '-'
			? { tail: a.slice(1), head: `more:${a}`, attributes: { style: 'dashed', dir: 'none' } }
			: { tail: `more:${a}`, head: a, attributes: { style: 'dashed', dir: 'none' } };

	const get_svg_gv = (nodes: (Node & { distance: number })[], links: Edge[], ext: string[]) => {
		const rankdir = direction;
		const names = RelationNames;
		const graph =
			type === 'work'
				? {
						nodes: nodes.map((ob) => gv_node(ob, `/work/${ob.id}`)),
						edges: links.map((r) => {
							const [tail, head] =
								r.relation === WorkRelationTypes.Sequel ? [r.B_id, r.A_id] : [r.A_id, r.B_id];
							return {
								tail,
								head,
								attributes: { label: names[r.relation](), class: rel_class(tail, head) }
							};
						})
					}
				: {
						nodes: nodes.map((ob) => gv_node(ob, `/tag/${(ob as Song).work_tag}`)),
						edges: links.map((r) => ({
							tail: r.A_id,
							head: r.B_id,
							attributes: {
								label: names[r.relation](),
								class: rel_class(r.A_id, r.B_id)
							}
						}))
					};
		return Viz.instance().then((viz) =>
			viz.renderString(
				{
					nodes: [...graph.nodes, ...ext.map(gv_more_node)],
					edges: [...graph.edges, ...ext.map(gv_more_edge)],
					nodeAttributes: { shape: 'box', fontname: gv_font, fontsize: 9 },
					edgeAttributes: { minlen: 2, fontname: gv_font, fontsize: 8, arrowsize: 0.7 }
				},
				{
					format: 'svg_inline',
					graphAttributes: { bgcolor: 'transparent', rankdir },
					images: nodes
						.filter((ob) => gv_thumb(ob))
						.map((ob) => ({ name: gv_thumb(ob)!, width: 160, height: 120 }))
				}
			)
		);
	};

	let svg = $derived(
		backend === GraphViewBackends.Graphviz
			? get_svg_gv(nodes, links, ext)
			: get_svg_mermaid(nodes, links, ext)
	);

	onMount(() => {
		if (backend === GraphViewBackends.Mermaid) {
			mermaid.initialize({ maxTextSize: 1000000, startOnLoad: false, theme: 'base' });
			mermaid.registerLayoutLoaders(elkLayouts);
		}
	});

	let svgContainer = $state<HTMLDivElement | undefined>(undefined);

	function svgMouseOver(event: Event) {
		if (!svgContainer) return;
		const target = event.target as HTMLElement;

		// Hovering a node lights up every edge sharing its rel_<id> class
		const gv_node_el = target.closest('g.node[class*="rel_"]');
		if (gv_node_el) {
			const rel = [...gv_node_el.classList].find((c) => c.startsWith('rel_'));
			if (rel)
				svgContainer
					.querySelectorAll(`g.edge.${rel}`)
					.forEach((e) => e.classList.add('highlighted'));
			return;
		}

		const node = target.closest('[id*="-flowchart-"]');
		const label: HTMLElement | null = target.closest('.label:has(.edgeLabel)');

		if (node) {
			const nodeId = node.id.match(/-flowchart-(.+)-\d+$/)?.[1];
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

	function svgMouseOut() {
		if (svgContainer) {
			const highlightedLinks = svgContainer.querySelectorAll('.highlighted');
			highlightedLinks.forEach((link) => {
				link.classList.remove('highlighted');
			});
		}
	}

	let svg_height = $derived(min_height),
		old_svg_height = 0;
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
{#if type === 'work'}
	<label class="mt-2 mb-2 block">
		<input type="checkbox" bind:checked={show_thumbs} />
		{m.heroic_ideal_orangutan_aid()}
	</label>
{/if}
{m.mild_loud_shad_enchant({ type: m.mellow_upper_finch_drip(), name: '' })}
<select multiple bind:value={allowed_types}>
	{#each enumValues(RelationTypes) as t, i (i)}
		<option value={t} class="type-label">{RelationNames[t]()}</option>
	{/each}
</select>

<!-- Mermaid requires browser API, for GV use browser for view directly -->
{#if backend === GraphViewBackends.Mermaid}
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
				{@html s}
			</SVGViewer>
		</div>
	{/await}
{:else}
	<div
		class="gv-graph"
		bind:this={svgContainer}
		onmouseover={svgMouseOver}
		onmouseout={svgMouseOut}
		onfocusin={svgMouseOver}
		onfocusout={svgMouseOut}
		role="presentation"
	>
		<!-- eslint-disable-next-line svelte/no-at-html-tags -->
		{@html await svg}
	</div>
{/if}
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

<style lang="postcss">
	@reference "../app.css";
	.gv-graph :global {
		svg text {
			font-family: Arial, Helvetica, sans-serif;
			fill: var(--otodb-color-content-primary);
		}
		svg g.node polygon {
			stroke: var(--otodb-color-content-faint);
			/* Allow hovering node to highlight edges */
			pointer-events: all;
		}
		svg g.edge path {
			stroke: var(--otodb-color-content-fainter);
		}
		/* Arrowheads */
		svg g.edge polygon {
			fill: var(--otodb-color-content-faint);
			stroke: var(--otodb-color-content-faint);
		}
		svg #graph_current polygon {
			stroke: var(--otodb-color-del);
		}
		svg #graph_current text {
			fill: var(--otodb-color-del);
		}
		svg g.untitled text {
			font-style: italic;
		}
		svg g.node.thumb text {
			text-shadow:
				0 0 2px var(--otodb-color-bg-primary),
				0 0 4px var(--otodb-color-bg-primary),
				0 0 6px var(--otodb-color-bg-primary);
		}
		svg g.edge.highlighted {
			& path {
				stroke: var(--otodb-color-del);
				stroke-width: 2px;
			}
			& polygon {
				fill: var(--otodb-color-del);
				stroke: var(--otodb-color-del);
			}
			& text {
				fill: var(--otodb-color-del);
			}
		}
	}
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
