<script lang="ts">
	import Pager from '$lib/Pager.svelte';
	import { EntityModelRoutes } from '$lib/enums';
	import { m } from '$lib/paraglide/messages';
	import Section from '$lib/Section.svelte';
	import { timeAgo } from '$lib/ui';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
</script>

<Section title={data.title} type={m.grand_merry_fly_succeed()} menuLinks={data.links}>
	<a href="/post/new?category=3&entity=w{data.id}">{m.antsy_aloof_horse_grace()}</a>
	{#if data.threads.items.length}
		<table class="w-full table-fixed">
			<thead>
				<tr>
					<th class="text-left">{m.large_factual_octopus_exhale()}</th>
					<th class="w-32 text-left">{m.crisp_red_canary_tickle()}</th>
					<th class="w-64 text-right">{m.super_agent_pigeon_aim()}</th>
				</tr>
			</thead><tbody>
				{#each data.threads.items as post, i (i)}
					{@const otherEntities =
						post.entities?.filter(
							(e) => !(e.entity === 'mediawork' && String(e.id) === String(data.id))
						) ?? []}
					<tr>
						<td>
							<a href="/post/{post.id}">{post.title}</a>
							{#if otherEntities.length}
								<span class="text-otodb-content-fainter block text-xs">
									{#each otherEntities as { id, entity }, j (j)}
										{#if j > 0},
										{/if}
										<a href="/{EntityModelRoutes[entity]}/{id}"
											>{EntityModelRoutes[entity]}/{id}</a
										>
									{/each}
								</span>
							{/if}
						</td>
						<td
							><a href="/profile/{post.added_by.username}">{post.added_by.username}</a
							></td
						>
						<td class="text-right"
							><time title={new Date(post.modified).toLocaleString()}
								>{timeAgo(post.modified)}</time
							></td
						>
					</tr>
				{/each}
			</tbody>
		</table>
		<Pager n_count={data.threads.count} page={data.page} page_size={data.batch_size} />
	{/if}
</Section>
