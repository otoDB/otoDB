<script lang="ts">
	import { browser } from '$app/environment';
	import { page } from '$app/state';
	import { enumValues, SongRelationNames, WorkRelationNames } from '$lib/enums.js';
	import { asDirection, type Direction, type GraphType } from '$lib/graph';
	import { graphView } from '$lib/graph.remote';
	import { m } from '$lib/paraglide/messages.js';
	import { GraphViewBackends, SongRelationTypes, WorkRelationTypes } from '$lib/schema';
	import { getLocalPref } from '$lib/ui';
	import { SVGViewer } from 'svelte-svg-viewer';

	interface Props {
		id: string;
		type: GraphType;
		min_height?: number;
		defaultDir?: Direction;
		backend?: GraphViewBackends;
	}
	let { id, type, defaultDir, min_height = 600, backend }: Props = $props();

	const active_backend = $derived(
		backend ?? page.data.user?.prefs?.GRAPH_VIEW_BACKEND ?? getLocalPref('GRAPH_VIEW_BACKEND')
	);

	const RelationTypes = $derived(type === 'work' ? WorkRelationTypes : SongRelationTypes);
	const RelationNames = $derived(
		(type === 'work' ? WorkRelationNames : SongRelationNames) as Record<number, () => string>
	);

	const params = $derived(page.url.searchParams);
	const deg = $derived(Number(params.get('deg')) || 1);
	const thumbs = $derived(params.getAll('thumbs').at(-1) !== '0');
	const types = $derived(params.has('types') ? params.getAll('types').map(Number) : null);
	const dir = $derived(asDirection(params.get('dir')) ?? defaultDir ?? null);

	const graph = $derived(
		await graphView({ type, id, deg, dir, thumbs, types, backend: active_backend })
	);

	let mermaid_ready = false;
	const render_mermaid = async (source: string) => {
		const [{ default: mermaid }, { default: elkLayouts }] = await Promise.all([
			import('mermaid'),
			import('@mermaid-js/layout-elk')
		]);
		if (!mermaid_ready) {
			mermaid.initialize({ maxTextSize: 1000000, startOnLoad: false, theme: 'base' });
			mermaid.registerLayoutLoaders(elkLayouts);
			mermaid_ready = true;
		}
		return (await mermaid.render('Relations', source)).svg;
	};
	const mermaid_svg = $derived(browser && graph.mermaid ? render_mermaid(graph.mermaid) : null);

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

{#if !graph.empty}
	{#key page.url.search}
		<form method="GET">
			<table>
				<tbody>
					<tr>
						<th><label for="deg">{m.just_grassy_mantis_slurp()}</label></th>
						<td>
							<input
								type="number"
								id="deg"
								name="deg"
								value={graph.deg}
								min="1"
								max={graph.max_distance || 1}
							/>
							/ {graph.max_distance}
						</td>
					</tr>
					<tr>
						<th><label for="dir">{m.fair_aware_salmon_twist()}</label></th>
						<td>
							<select id="dir" name="dir" value={graph.dir}
								><option value="LR">{m.top_front_ray_treasure()}</option><option value="TB"
									>{m.stout_jumpy_ox_feel()}</option
								></select
							>
						</td>
					</tr>
					{#if type === 'work'}
						<tr>
							<th><label for="thumbs">{m.heroic_ideal_orangutan_aid()}</label></th>
							<td>
								<input type="hidden" name="thumbs" value="0" />
								<input type="checkbox" id="thumbs" name="thumbs" value="1" checked={thumbs} />
							</td>
						</tr>
					{/if}
					<tr>
						<th>
							<label for="types"
								>{m.mild_loud_shad_enchant({ type: m.mellow_upper_finch_drip(), name: '' })}</label
							>
						</th>
						<td>
							<select multiple id="types" name="types">
								{#each enumValues(RelationTypes) as t, i (i)}
									<option
										value={t}
										selected={(types ?? enumValues(RelationTypes)).includes(t)}
										class="type-label">{RelationNames[t]()}</option
									>
								{/each}
							</select>
						</td>
					</tr>
				</tbody>
			</table>
			<input type="submit" />
		</form>
	{/key}

	{#if graph.svg}
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
			{@html graph.svg}
		</div>
	{:else if mermaid_svg}
		{#await mermaid_svg}
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
		{m.sunny_light_duck_surge()}
	{/if}
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
