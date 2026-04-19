<script lang="ts">
	import Section from '$lib/Section.svelte';

	import { m } from '$lib/paraglide/messages.js';
	import Pager from '$lib/Pager.svelte';
	import { buildEntityRoutes, type EntityModelType } from '$lib/enums';
	import ActionTimestamp from '$lib/ActionTimestamp.svelte';

	let { data } = $props();
</script>

<Section title={m.same_broad_haddock_pinch()}>
	<table>
		<tbody>
			{#each data.comments?.items as c, i (i)}
				{@const link = buildEntityRoutes(c.entity_type as EntityModelType, c.entity_id)}
				<tr>
					<td>
						<a href={link}>
							{link}
						</a>
					</td>
					<td>
						<a href="/profile/{c.user.username}">{c.user.username}</a>
					</td>
					<td>
						{c.comment}
					</td>
					<td>
						<ActionTimestamp date={c.submit_date} />
					</td>
				</tr>
			{/each}
		</tbody>
	</table>
	{#if data.comments?.count}
		<Pager n_count={data.comments.count} page={data.page} page_size={data.batch_size} />
	{/if}
</Section>
