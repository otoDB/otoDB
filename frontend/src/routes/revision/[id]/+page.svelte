<script lang="ts">
	import { goto } from '$app/navigation';
	import client from '$lib/api.js';
	import { dirtyClick } from '$lib/dirty';
	import { buildEntityRoutes } from '$lib/enums.js';
	import { isSOV, isSVO } from '$lib/enums/language.js';
	import { routeNames } from '$lib/enums/route.js';
	import { hasUserLevel } from '$lib/enums/userLevel.js';
	import { m } from '$lib/paraglide/messages';
	import { getLocale } from '$lib/paraglide/runtime';
	import { Levels, PostCategory } from '$lib/schema.js';
	import Section from '$lib/Section.svelte';
	import { callSavingToast } from '$lib/toast';
	import { setRevisionRefs } from './refs';
	import RowChange from './RowChange.svelte';

	let { data } = $props();

	// Keyed once here so child components can resolve a single work by id (O(1))
	// instead of receiving and scanning the whole array at every level.
	const worksById = $derived(
		Object.fromEntries((data.changes.works ?? []).map((w) => [w.id, w] as const))
	);

	// Shared via context (reactive getters) so leaf components resolve refs
	// without these maps being threaded through every intermediate component.
	setRevisionRefs({
		get works() {
			return worksById;
		},
		get labels() {
			return data.changes.labels;
		}
	});

	let diffLayout = $state<'inline' | 'split'>('inline');

	// Per-entity expand/collapse, defaulting open; keyed by route+entity index.
	let entityOpen = $state<Record<string, boolean>>({});
	const entityKey = (i: number, j: number) => `${i}:${j}`;
	const allKeys = $derived(
		data.routes.flatMap((r, i) => r.entities.map((_, j) => entityKey(i, j)))
	);
	const allExpanded = $derived(allKeys.length > 0 && allKeys.every((k) => entityOpen[k] ?? true));
	const toggleAll = () => {
		const target = !allExpanded;
		for (const k of allKeys) entityOpen[k] = target;
	};
</script>

<Section title="{m.arable_direct_swan_glow()} #{data.revision.id}">
	<h3>
		{#if isSVO(getLocale())}
			{m.curly_safe_lynx_fond()}
		{/if}
		<a href="/profile/{data.revision.user}">{data.revision.user}</a>
		{#if isSOV(getLocale())}
			{m.curly_safe_lynx_fond()}
		{/if}
	</h3>
	{#if data.revision.message}<h4 class="my-5">{data.revision.message}</h4>{/if}
	{#if hasUserLevel(data.user?.level, Levels.Mod) && data.revision.id !== '1'}<button
			class="my-5"
			{@attach dirtyClick(async () => {
				if (!confirm('Are you sure?')) return;
				const p = client.POST('/api/history/rollback', {
					fetch,
					params: { query: { revision_id: data.revision.id } }
				});
				callSavingToast(p);
				const { error } = await p;
				if (!error) await goto('/revision');
			})}>Revert changes made in this revision</button
		>{/if}
	{#if data.user && data.user.username !== data.revision.user}
		<button
			onclick={() =>
				goto(
					`/thread/new?category=${PostCategory.Gardening}&entity=@${data.revision.user}&title=${m.silly_quiet_fireant_quell({ id: data.revision.id })}`
				)}>{m.frail_loose_gecko_play({ user: data.revision.user })}</button
		>
	{/if}

	{#if data.routes.length}
		<menu
			class="my-2 flex list-none justify-start gap-2"
			aria-label={m.fluffy_icy_bobcat_believe()}
		>
			<li>
				<button
					type="button"
					class="flex items-center gap-1 p-1"
					aria-pressed={allExpanded}
					onclick={toggleAll}
				>
					<span
						class={[
							'size-4',
							allExpanded
								? 'icon-[gravity-ui--chevrons-collapse-vertical]'
								: 'icon-[gravity-ui--chevrons-expand-vertical]'
						]}
						aria-hidden="true"
					></span>
					<span class="grid">
						<span class={['col-start-1 row-start-1', !allExpanded && 'invisible']}>
							{m.game_slow_crab_fade()}
						</span>
						<span class={['col-start-1 row-start-1', allExpanded && 'invisible']}>
							{m.sleek_factual_antelope_belong()}
						</span>
					</span>
				</button>
			</li>
			<li>
				<button
					type="button"
					class="flex items-center gap-1 p-1"
					aria-pressed={diffLayout === 'split'}
					onclick={() => (diffLayout = diffLayout === 'inline' ? 'split' : 'inline')}
				>
					<span
						class={[
							'size-4',
							diffLayout === 'inline'
								? 'icon-[gravity-ui--layout-columns]'
								: 'icon-[gravity-ui--layout-rows]'
						]}
						aria-hidden="true"
					></span>
					<span class="grid">
						<span class={['col-start-1 row-start-1', diffLayout !== 'inline' && 'invisible']}>
							{m.caring_elegant_gadfly_tear()}
						</span>
						<span class={['col-start-1 row-start-1', diffLayout === 'inline' && 'invisible']}>
							{m.antsy_stout_gorilla_borrow()}
						</span>
					</span>
				</button>
			</li>
		</menu>
	{/if}

	<ul class="my-5 flex list-none flex-col gap-8">
		{#each data.routes as { route, entities }, i (i)}
			<li>
				<h3 class="mb-3 font-bold">
					{routeNames[route]()}
				</h3>
				<ul class="flex list-none flex-col gap-3">
					{#each entities as { ent_type, ent_id, rows }, j (j)}
						<li>
							<details
								class="entity"
								open={entityOpen[entityKey(i, j)] ?? true}
								ontoggle={(e) => (entityOpen[entityKey(i, j)] = e.currentTarget.open)}
							>
								<summary>
									<a
										href={buildEntityRoutes(ent_type, ent_id)}
										onclick={(e) => e.stopPropagation()}
									>
										{buildEntityRoutes(ent_type, ent_id)}
									</a>
								</summary>
								<table class="changes">
									<colgroup>
										<col class="c-ind" />
										<col class="c-field" />
										<col />
									</colgroup>
									<tbody>
										{#each rows as row (row.target_type + ':' + row.target_id)}
											<RowChange
												{...row}
												{ent_type}
												{ent_id}
												layout={diffLayout}
												deletedRows={data.changes.deleted_rows}
												rowContext={data.changes.row_context}
											/>
										{/each}
									</tbody>
								</table>
							</details>
						</li>
					{/each}
				</ul>
			</li>
		{/each}
	</ul>
</Section>

<style>
	details.entity {
		margin: 0;
		padding: 0;
		border: 1px solid var(--otodb-color-content-faint);
	}

	details.entity > summary {
		padding: 0.25rem 0.5rem;
	}

	details.entity[open] > summary {
		margin-bottom: 0;
		border-bottom: 1px solid var(--otodb-color-content-faint);
	}

	table.changes {
		width: 100%;
		table-layout: fixed;
	}

	table.changes > colgroup > .c-ind {
		width: 1.75rem;
	}

	table.changes > colgroup > .c-field {
		width: 10rem;
	}

	/* Center the +/- indicator */
	table.changes :global(td.ind) {
		text-align: center;
	}

	/* Long unbroken values must wrap rather than overflow the fixed columns */
	table.changes :global(td) {
		overflow-wrap: anywhere;
	}
</style>
