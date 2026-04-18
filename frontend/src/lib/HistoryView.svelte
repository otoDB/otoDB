<script lang="ts">
	import { resolveRouteKeyById, Route } from '$lib/enums/Route';
	import { m } from './paraglide/messages';
	import type { components } from './schema';
	import TimeAgo from '$lib/TimeAgo.svelte';
	interface Props {
		revisions: components['schemas']['RevisionSchema'][];
		user: components['schemas']['UserStatusSchema'] | null;
	}
	let { revisions }: Props = $props();
</script>

<table class="w-full table-auto text-center">
	<tbody>
		<tr>
			<th>Version</th><th>Revision</th><th>Action</th><th>{m.fuzzy_crazy_cobra_lead()}</th><th
				>{m.super_agent_pigeon_aim()}</th
			><th>{m.weary_spicy_fly_attend()}</th>
		</tr>
		{#each revisions as rev, i (i)}
			<tr
				><td>{rev.index}</td><td><a href="/revision/{rev.id}">#{rev.id}</a></td><td
					>{rev.route !== null && rev.route !== undefined
						? Route[resolveRouteKeyById(rev.route)].title()
						: ''}</td
				><td>
					<a href="/profile/{rev.user}">{rev.user}</a>
				</td><td>
					<TimeAgo date={rev.date} />
				</td><td>
					{rev.message}
				</td>
			</tr>
		{/each}
	</tbody>
</table>
