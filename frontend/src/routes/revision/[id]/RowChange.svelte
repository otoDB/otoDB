<script lang="ts">
	import { buildEntityRoutes, isValidEntityModelType } from '$lib/enums.js';
	import { m } from '$lib/paraglide/messages';
	import type { components } from '$lib/schema';
	import DiffRows from './DiffRows.svelte';
	import DiffValue from './DiffValue.svelte';
	import Value from './Value.svelte';
	import { displayValue } from './displayValue';

	type RC = components['schemas']['RevisionChangeSchema'];

	interface Props {
		target_type: string;
		tg_id: string;
		target_id: string;
		rcs: RC[];
		ent_type: string;
		ent_id: string;
		deletedRows: Record<string, components['schemas']['OldColumnSchema'][]>;
		rowContext: Record<string, components['schemas']['OldColumnSchema'][]>;
		layout?: 'inline' | 'split';
		windowed?: boolean;
	}
	const {
		target_type,
		tg_id,
		target_id,
		rcs,
		ent_type,
		ent_id,
		deletedRows,
		rowContext,
		layout = 'inline',
		windowed = true
	}: Props = $props();

	const isOwnEntity = $derived(target_type === ent_type && tg_id === ent_id);
	// A wikipage has exactly one attachment (slug, tag, or work); a slugless one
	// has no /wiki/<id> page, so when nested reference its tag/work page instead.
	const wikiNested = $derived(target_type === 'wikipage' && !isOwnEntity);
	const ref = $derived(
		wikiNested ? { type: ent_type, id: ent_id } : { type: target_type, id: tg_id }
	);
	const tgHref = $derived(
		isValidEntityModelType(ref.type) ? buildEntityRoutes(ref.type, ref.id) : undefined
	);
	// Nested wikipages show their page path; others show the slug, or "#" + numeric id
	const tgLabel = $derived(
		wikiNested && tgHref ? tgHref : /^\d+$/.test(ref.id) ? `#${ref.id}` : ref.id
	);
	const deletedChange = $derived(rcs.find((c) => c.deleted));
	const restoredChange = $derived(rcs.find((c) => c.restored));
	const allCreated = $derived(rcs.length > 0 && rcs.every((c) => c.created));
	const byColumn = $derived(
		new Map(rcs.filter((c) => c.target_column).map((c) => [c.target_column!, c] as const))
	);

	const oldRow = $derived(deletedRows[`${target_type}:${target_id}`] ?? []);
	const oldByColumn = $derived(new Map(oldRow.map((e) => [e.column, e] as const)));

	// Current values of columns the revision did not touch (relation-like rows only)
	const context = $derived(rowContext[`${target_type}:${target_id}`] ?? []);
	const contextByColumn = $derived(new Map(context.map((e) => [e.column, e] as const)));
	const hasCol = (col: string) => byColumn.has(col) || contextByColumn.has(col);

	// Localized labels for tagworkparenthood's columns
	const columnLabel = (col: string) => {
		if (target_type !== 'tagworkparenthood') return col;
		return (
			{
				tag: m.tame_sharp_finch_hatch(),
				parent: m.away_crisp_blackbird_twist(),
				primary: m.neat_proud_swan_lead()
			}[col] ?? col
		);
	};
</script>

<!-- A related row (not the entity itself): a full-width header linking the object -->
{#snippet relHeader()}
	{#if !isOwnEntity}
		<tr class="rel">
			<th colspan="3">
				<span class="arrow" aria-hidden="true">↳</span>
				<span class="type font-mono">{target_type}</span>
				{#if tgHref}<a href={tgHref}>{tgLabel}</a>{:else}<span>{tgLabel}</span>{/if}
			</th>
		</tr>
	{/if}
{/snippet}

{#if deletedChange}
	{@render relHeader()}
	{#if oldByColumn.has('A') && oldByColumn.has('B')}
		<tr>
			<td class="ind">−</td>
			<td colspan="2">
				<del class="flex items-center gap-2 p-1 opacity-70">
					<Value
						targetType={target_type}
						column="A"
						value={oldByColumn.get('A')?.value}
						ref={oldByColumn.get('A')?.ref}
						card
					/>
					<span>—{displayValue(target_type, 'relation', oldByColumn.get('relation')?.value)}→</span>
					<Value
						targetType={target_type}
						column="B"
						value={oldByColumn.get('B')?.value}
						ref={oldByColumn.get('B')?.ref}
						card
					/>
				</del>
			</td>
		</tr>
	{:else}
		<tr class="note"><td colspan="3">{m.quick_calm_mole_vanish()}</td></tr>
		{#each oldRow as entry (entry.column)}
			<tr>
				<td class="ind">−</td>
				<td class="font-mono">{columnLabel(entry.column)}</td>
				<td>
					<del>
						<Value
							targetType={target_type}
							column={entry.column}
							value={entry.value}
							ref={entry.ref}
						/>
					</del>
				</td>
			</tr>
		{/each}
	{/if}
{:else if restoredChange}
	{@render relHeader()}
	<tr class="note">
		<td colspan="3">{m.warm_civil_heron_return({ id: restoredChange.target_value ?? '?' })}</td>
	</tr>
{:else if hasCol('A') && hasCol('B')}
	{@render relHeader()}
	{#if allCreated}
		<tr>
			<td class="ind">+</td>
			<td colspan="2">
				<ins class="flex items-center gap-2 p-1">
					<Value
						targetType={target_type}
						column="A"
						value={byColumn.get('A')?.target_value}
						ref={byColumn.get('A')?.ref}
						card
					/>
					<span
						>—{displayValue(target_type, 'relation', byColumn.get('relation')?.target_value)}→</span
					>
					<Value
						targetType={target_type}
						column="B"
						value={byColumn.get('B')?.target_value}
						ref={byColumn.get('B')?.ref}
						card
					/>
				</ins>
			</td>
		</tr>
	{:else}
		<tr>
			<td class="ind">±</td>
			<td colspan="2">
				<div class="flex items-center gap-2">
					{@render relationSlot('A')}
					<div class="flex flex-col items-center">
						{#if byColumn.has('relation')}
							<DiffValue change={byColumn.get('relation')!} />
						{:else}
							<span
								>{displayValue(
									target_type,
									'relation',
									contextByColumn.get('relation')?.value
								)}</span
							>
						{/if}
						<span>→</span>
					</div>
					{@render relationSlot('B')}
				</div>
			</td>
		</tr>
	{/if}
{:else}
	{@render relHeader()}
	{#each rcs.filter((c) => c.target_column) as c, k (k)}
		<DiffRows change={c} label={columnLabel(c.target_column!)} {layout} {windowed} />
	{/each}
	<!-- Columns the revision didn't touch, shown for context -->
	{#each context.filter((e) => !byColumn.has(e.column)) as entry (entry.column)}
		<tr>
			<td></td>
			<td class="font-mono">{columnLabel(entry.column)}</td>
			<td>
				<Value targetType={target_type} column={entry.column} value={entry.value} ref={entry.ref} />
			</td>
		</tr>
	{/each}
{/if}

{#snippet relationSlot(col: string)}
	{#if byColumn.has(col)}
		<DiffValue change={byColumn.get(col)!} card />
	{:else}
		<Value
			targetType={target_type}
			column={col}
			value={contextByColumn.get(col)?.value}
			ref={contextByColumn.get(col)?.ref}
			card
		/>
	{/if}
{/snippet}

<style>
	ins,
	del {
		border-radius: var(--radius-xs);
		text-decoration: none;
	}

	tr:has(> td > ins) > td.ind,
	tr:has(> td > del) > td.ind {
		border-radius: var(--radius-xs);
	}

	tr:has(> td > ins) > td.ind {
		background-color: var(--otodb-color-ins);
	}

	tr:has(> td > del) > td.ind {
		background-color: var(--otodb-color-del);
	}

	/* Relationship header: a related row in another table connected to the entity */
	tr.rel > th {
		text-align: left;
		font-weight: bold;
		background-color: var(--otodb-color-bg-fainter);
	}

	tr.rel .arrow,
	tr.rel .type {
		font-weight: normal;
	}

	tr.note > td {
		color: var(--otodb-color-content-fainter);
		font-style: italic;
	}
</style>
