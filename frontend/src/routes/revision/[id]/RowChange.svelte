<script lang="ts">
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
		works: components['schemas']['SlimWorkSchema'][];
		labels: Record<string, string>;
		deletedRows: Record<string, components['schemas']['OldColumnSchema'][]>;
		rowContext: Record<string, components['schemas']['OldColumnSchema'][]>;
	}
	const {
		target_type,
		tg_id,
		target_id,
		rcs,
		ent_type,
		ent_id,
		works,
		labels,
		deletedRows,
		rowContext
	}: Props = $props();

	const isOwnEntity = $derived(target_type === ent_type && tg_id === ent_id);
	const deletedChange = $derived(rcs.find((c) => c.deleted));
	const restoredChange = $derived(rcs.find((c) => c.restored));
	const allCreated = $derived(rcs.length > 0 && rcs.every((c) => c.created));
	const byColumn = $derived(
		new Map(rcs.filter((c) => c.target_column).map((c) => [c.target_column!, c] as const))
	);
	const isRelation = $derived(target_type === 'workrelation' || target_type === 'songrelation');

	const oldRow = $derived(deletedRows[`${target_type}:${target_id}`] ?? []);
	const oldByColumn = $derived(new Map(oldRow.map((e) => [e.column, e] as const)));

	// Current values of columns the revision did not touch (relation-like rows only)
	const context = $derived(rowContext[`${target_type}:${target_id}`] ?? []);
	const contextByColumn = $derived(new Map(context.map((e) => [e.column, e] as const)));
	const hasCol = (col: string) => byColumn.has(col) || contextByColumn.has(col);

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

{#snippet targetPrefix()}
	{#if !isOwnEntity}
		<div class="text-otodb-content-fainter">{target_type} #{tg_id}</div>
	{/if}
{/snippet}

{#if deletedChange}
	<div class="my-2">
		{@render targetPrefix()}
		{#if isRelation && oldByColumn.has('A') && oldByColumn.has('B')}
			<div class="flex items-center gap-1">
				<span>−</span>
				<del class="flex items-center gap-2 p-1 opacity-70">
					<Value
						targetType={target_type}
						column="A"
						value={oldByColumn.get('A')?.value}
						ref={oldByColumn.get('A')?.ref}
						card
						{works}
						{labels}
					/>
					<span>—{displayValue(target_type, 'relation', oldByColumn.get('relation')?.value)}→</span>
					<Value
						targetType={target_type}
						column="B"
						value={oldByColumn.get('B')?.value}
						ref={oldByColumn.get('B')?.ref}
						card
						{works}
						{labels}
					/>
				</del>
			</div>
		{:else}
			<del>{m.quick_calm_mole_vanish()}</del>
			{#if oldRow.length}
				<table>
					<tbody>
						{#each oldRow as entry (entry.column)}
							<tr>
								<td>−</td>
								<td>{columnLabel(entry.column)}</td>
								<td>
									<del>
										<Value
											targetType={target_type}
											column={entry.column}
											value={entry.value}
											ref={entry.ref}
											{works}
											{labels}
										/>
									</del>
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			{/if}
		{/if}
	</div>
{:else if restoredChange}
	<div class="my-2">
		{@render targetPrefix()}
		<span>{m.warm_civil_heron_return({ id: restoredChange.target_value ?? '?' })}</span>
	</div>
{:else if isRelation && hasCol('A') && hasCol('B')}
	<div class="my-2">
		{@render targetPrefix()}
		{#if allCreated}
			<div class="flex items-center gap-1">
				<span>+</span>
				<ins class="flex items-center gap-2 p-1">
					<Value
						targetType={target_type}
						column="A"
						value={byColumn.get('A')?.target_value}
						ref={byColumn.get('A')?.ref}
						card
						{works}
						{labels}
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
						{works}
						{labels}
					/>
				</ins>
			</div>
		{:else}
			<div class="flex items-center gap-2">
				{@render relationSlot('A')}
				<div class="flex flex-col items-center">
					{#if byColumn.has('relation')}
						<DiffValue change={byColumn.get('relation')!} {works} {labels} />
					{:else}
						<span
							>{displayValue(target_type, 'relation', contextByColumn.get('relation')?.value)}</span
						>
					{/if}
					<span>→</span>
				</div>
				{@render relationSlot('B')}
			</div>
		{/if}
	</div>
{:else}
	<div class="my-2">
		{@render targetPrefix()}
		<table>
			<tbody>
				{#each rcs.filter((c) => c.target_column) as c, k (k)}
					<DiffRows change={c} label={columnLabel(c.target_column!)} {works} {labels} />
				{/each}
				<!-- Columns the revision didn't touch, shown for context -->
				{#each context.filter((e) => !byColumn.has(e.column)) as entry (entry.column)}
					<tr>
						<td></td>
						<td>{columnLabel(entry.column)}</td>
						<td>
							<Value
								targetType={target_type}
								column={entry.column}
								value={entry.value}
								ref={entry.ref}
								{works}
								{labels}
							/>
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
{/if}

{#snippet relationSlot(col: string)}
	{#if byColumn.has(col)}
		<DiffValue change={byColumn.get(col)!} card {works} {labels} />
	{:else}
		<Value
			targetType={target_type}
			column={col}
			value={contextByColumn.get(col)?.value}
			ref={contextByColumn.get(col)?.ref}
			card
			{works}
			{labels}
		/>
	{/if}
{/snippet}

<style>
	ins,
	del {
		border-radius: var(--radius-xs);
		text-decoration: none;
	}

	ins {
		background-color: var(--otodb-color-ins);
	}

	del {
		background-color: var(--otodb-color-del);
	}

	div:has(> ins) > span {
		color: var(--otodb-color-ins);
	}

	div:has(> del) > span {
		color: var(--otodb-color-del);
	}

	tr:has(> td > del) > td:first-child {
		color: var(--otodb-color-del);
	}
</style>
