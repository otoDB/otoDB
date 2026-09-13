<script lang="ts">
	import Section from '$lib/Section.svelte';

	import { m } from '$lib/paraglide/messages.js';
	import Pager from '$lib/Pager.svelte';
	import { buildEntityRoutes, type EntityModelType } from '$lib/enums';
	import Time from '$lib/Time.svelte';

	let { data } = $props();
</script>

<Section title={m.same_broad_haddock_pinch()}>
	<table class="w-full table-fixed">
		<colgroup>
			<col class="w-2/12" />
			<col class="w-2/12" />
			<col />
			<col class="w-2/12" />
		</colgroup>
		<tbody>
			{#each data.comments?.items as c, i (i)}
				{@const link = buildEntityRoutes(c.entity_type as EntityModelType, c.entity_id)}
				<tr>
					<td class="wrap-anywhere">
						<a href={link}>
							{link}
						</a>
					</td>
					<td class="wrap-anywhere">
						<a href="/user/{c.user.username}">{c.user.username}</a>
					</td>
					<td class="wrap-anywhere">
						{c.comment}
					</td>
					<td class="wrap-anywhere">
						<Time format="relative" date={c.submit_date} />
					</td>
				</tr>
			{/each}
		</tbody>
	</table>
	{#if data.comments?.count}
		<Pager n_count={data.comments.count} page_size={data.batch_size} />
	{/if}
</Section>
