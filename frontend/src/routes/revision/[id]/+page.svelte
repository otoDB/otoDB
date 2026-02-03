<script lang="ts">
	import { invalidateAll } from '$app/navigation';
	import client from '$lib/api.js';
	import { CommentModelRoutes, Route, UserLevel } from '$lib/enums.js';
	import Pager from '$lib/Pager.svelte';
	import { m } from '$lib/paraglide/messages';
	import { getLocale } from '$lib/paraglide/runtime';
	import Section from '$lib/Section.svelte';
	import { isSOV, isSVO } from '$lib/ui';

	let { data } = $props();
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
	{#if data.revision.actions.length}
		<ul class="my-5">
			{#each new Set(data.revision.actions.map((a) => a.route)) as r, i (i)}
				{Route[r]}
			{/each}
			{#each data.revision.actions as ent, i (i)}
				{#if Object.hasOwn(CommentModelRoutes, ent.ent_type)}
					<li>
						<a href="/{CommentModelRoutes[ent.ent_type]}/{ent.ent_id}">{ent.ent_id}</a>
					</li>
				{/if}
			{/each}
		</ul>
	{/if}
	{#if data.revision.message}<h4 class="my-5">{data.revision.message}</h4>{/if}
	{#if data.user?.level >= UserLevel.ADMIN && data.revision.id > 1}<button
			class="my-5"
			onclick={async () => {
				if (!confirm('Are you sure?')) return;
				await client.POST('/api/history/rollback', {
					fetch,
					params: { query: { revision_id: data.revision.id } }
				});
				invalidateAll();
			}}>Revert changes made in this revision</button
		>{/if}

	<pre>
		{#each data.changes.items as c, i (i)}{c.target_type} #{c.target_id} - {#if c.deleted}Deleted{:else}{c.target_column} -> {c.target_value}{/if}
		{/each}</pre>
	<Pager n_count={data.changes?.count} page={data.page} page_size={data.batch_size} />
</Section>
