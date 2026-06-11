<script lang="ts">
	import { goto, invalidateAll } from '$app/navigation';
	import client from '$lib/api.js';
	import { dirtyClick } from '$lib/dirty';
	import { buildEntityRoutes } from '$lib/enums.js';
	import { isSOV, isSVO } from '$lib/enums/language.js';
	import { routeNames } from '$lib/enums/route.js';
	import { hasUserLevel } from '$lib/enums/userLevel.js';
	import Pager from '$lib/Pager.svelte';
	import { m } from '$lib/paraglide/messages';
	import { getLocale } from '$lib/paraglide/runtime';
	import { Levels, PostCategory } from '$lib/schema.js';
	import Section from '$lib/Section.svelte';
	import RowChange from './RowChange.svelte';

	let { data } = $props();

	const works = $derived(new Map((data.refs?.works ?? []).map((w) => [w.id, w])));
	const labels = $derived(data.refs?.labels ?? {});
	const deletedRows = $derived(data.refs?.deleted_rows ?? {});
	const rowContext = $derived(data.refs?.row_context ?? {});
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
				await client.POST('/api/history/rollback', {
					fetch,
					params: { query: { revision_id: data.revision.id } }
				});
				await invalidateAll();
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

	<ul class="my-5">
		{#each data.routes as { route, entities }, i (i)}
			<li>{routeNames[route]()}</li>
			<li class="ml-2 list-none">
				<ul>
					{#each entities as { ent_type, ent_id, rows }, j (j)}
						<li>
							<a href={buildEntityRoutes(ent_type, ent_id)}>
								{buildEntityRoutes(ent_type, ent_id)}
							</a>
						</li>
						<li class="list-none">
							{#each rows as row (row.target_type + ':' + row.target_id)}
								<RowChange
									{...row}
									{ent_type}
									{ent_id}
									{works}
									{labels}
									{deletedRows}
									{rowContext}
								/>
							{/each}
						</li>
					{/each}
				</ul>
			</li>
		{/each}
	</ul>
	<Pager n_count={data.changes.count} page={data.page} page_size={data.batch_size} />
</Section>
