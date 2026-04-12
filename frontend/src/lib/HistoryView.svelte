<script lang="ts">
	import { resolveRouteKeyById, Route } from '$lib/enums/Route';
	import { m } from './paraglide/messages';
	import type { components } from './schema';
	import { timeAgo } from './ui';
	interface Props {
		revisions: components['schemas']['RevisionSchema'][];
		user: components['schemas']['UserStatusSchema'] | null;
	}
	let { revisions, user = null }: Props = $props();
	// const rollback = async (entry) => {
	// 	await client.POST('/api/history/rollback', {
	// 		fetch,
	// 		params: { query: { history_id: entry.id, model: entry.model } }
	// 	});
	// 	invalidateAll();
	// };
</script>

<table class="w-full table-auto text-center">
	<tbody>
		<tr>
			<th>Version</th><th>Revision</th><th>Action</th><th>{m.fuzzy_crazy_cobra_lead()}</th><th
				>{m.super_agent_pigeon_aim()}</th
			><th>{m.weary_spicy_fly_attend()}</th>
			<!-- {#if user && user.level >= UserLevel.ADMIN}<th>{m.legal_mean_slug_link()}</th>{/if} -->
		</tr>
		{#each revisions as rev, i (i)}
			<tr
				><td>{rev.index}</td><td><a href="/revision/{rev.id}">#{rev.id}</a></td><td
					>{rev.route !== null && rev.route !== undefined
						? Route[resolveRouteKeyById(rev.route)].title
						: ''}</td
				><td>
					<a href="/profile/{rev.user}">{rev.user}</a>
				</td><td>
					<time title={new Date(rev.date).toLocaleString()}>{timeAgo(rev.date)}</time>
				</td><td>
					{rev.message}
				</td>
				<!-- {#if user && user.level >= UserLevel.ADMIN}<td
						><button onclick={() => rollback(entry)}>{m.legal_mean_slug_link()}</button
						></td
					>{/if} -->
			</tr>
		{/each}
	</tbody>
</table>
