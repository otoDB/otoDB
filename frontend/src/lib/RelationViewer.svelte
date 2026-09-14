<script lang="ts" generics="T extends 'work' | 'song'">
	import { enumValues, SongRelationNames, WorkRelationNames } from '$lib/enums.js';
	import { m } from '$lib/paraglide/messages.js';
	import { SongRelationTypes, WorkRelationTypes } from '$lib/schema';
	interface Props {
		svg: string;
		type: T extends 'work' ? 'work' : 'song';
		direction?: 'TB' | 'LR';
		max_distance: number;
		degree?: number;
		show_thumbs?: boolean;
		allowed_types?: (T extends 'work' ? WorkRelationTypes : SongRelationTypes)[];
	}
	let { svg, direction, type, max_distance, degree, show_thumbs, allowed_types }: Props = $props();

	const RelationTypes = $derived(type === 'work' ? WorkRelationTypes : SongRelationTypes);
	const RelationNames = $derived(type === 'work' ? WorkRelationNames : SongRelationNames);

	let svgContainer = $state<HTMLDivElement | undefined>(undefined);

	function svgMouseOver(event: Event) {
		if (!svgContainer) return;
		// Hovering a node lights up every edge sharing its rel_<id> class
		const node = (event.target as HTMLElement).closest('g.node[class*="rel_"]');
		const rel = node && [...node.classList].find((c) => c.startsWith('rel_'));
		if (rel)
			svgContainer.querySelectorAll(`g.edge.${rel}`).forEach((e) => e.classList.add('highlighted'));
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

<form method="GET">
	<table>
		<tbody>
			<tr>
				<th><label for="rel_deg">{m.just_grassy_mantis_slurp()}</label></th>
				<td>
					<input
						type="number"
						id="rel_deg"
						name="rel_deg"
						value={Math.max(Math.min(degree ?? 1, max_distance), 1)}
						min="1"
						max={max_distance}
					/>
					/ {max_distance}
				</td>
			</tr>
			<tr>
				<th><label for="rel_dir">{m.fair_aware_salmon_twist()}</label></th>
				<td>
					<select id="rel_dir" name="rel_dir" value={direction}
						><option value="LR">{m.top_front_ray_treasure()}</option><option value="TB"
							>{m.stout_jumpy_ox_feel()}</option
						></select
					>
				</td>
			</tr>
			{#if type === 'work'}
				<tr>
					<th><label for="rel_show_thumbs">{m.heroic_ideal_orangutan_aid()}</label></th>
					<td>
						<input
							type="checkbox"
							id="rel_show_thumbs"
							name="rel_show_thumbs"
							value="true"
							checked={show_thumbs}
						/>
						<input type="hidden" name="rel_show_thumbs" value="false" />
					</td>
				</tr>
			{/if}
			<tr>
				<th>
					<label for="rel_allowed_types"
						>{m.mild_loud_shad_enchant({ type: m.mellow_upper_finch_drip(), name: '' })}</label
					>
				</th>
				<td>
					<select multiple id="rel_allowed_types" name="rel_allowed_types" value={allowed_types}>
						{#each enumValues(RelationTypes) as t, i (i)}
							<option value={t} class="type-label">{RelationNames[t]()}</option>
						{/each}
					</select>
				</td>
			</tr>
		</tbody>
	</table>
	<input type="submit" />
</form>

<div
	class="gv-graph"
	bind:this={svgContainer}
	onmouseover={svgMouseOver}
	onfocus={svgMouseOver}
	onmouseout={svgMouseOut}
	onblur={svgMouseOut}
	role="presentation"
>
	<!-- eslint-disable-next-line svelte/no-at-html-tags -->
	{@html svg}
</div>

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
</style>
