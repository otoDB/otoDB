<script lang="ts">
	import Section from '$lib/Section.svelte';
	import { m } from '$lib/paraglide/messages.js';
	import { EntityModelRoutes, PostCategories } from '$lib/enums';
	import { timeAgo } from '$lib/ui';

	let { data } = $props();
</script>

<Section title={m.just_salty_anaconda_nourish()} menuLinks={data.links}>
	{#each data.categories as c, i (i)}
		{#if c.length}
			<h2 class="mt-4 text-base">
				<a href="/post/search?category={i}">{PostCategories[i]()}</a>
			</h2>
			<table class="w-full">
				<thead>
					<tr
						><th>{m.large_factual_octopus_exhale()}</th>{#if i > 0}<th
								>{m.crisp_red_canary_tickle()}</th
							>{/if}<th>{m.super_agent_pigeon_aim()}</th></tr
					>
				</thead><tbody>
					{#each c as p, j (j)}
						<tr>
							<td>
								<a href="/post/{p.id}">{p.title}</a>
								{#if p.entities?.length}
									<span class="text-otodb-content-fainter block text-xs">
										{#each p.entities as { id, entity }, k (k)}
											{#if k > 0},
											{/if}
											<a href="/{EntityModelRoutes[entity]}/{id}"
												>{EntityModelRoutes[entity]}/{id}</a
											>
										{/each}
									</span>
								{/if}
							</td>{#if i > 0}
								<td
									><a href="/profile/{p.added_by.username}"
										>{p.added_by.username}</a
									></td
								>{/if}
							<td
								><time title={new Date(p.modified).toLocaleString()}
									>{timeAgo(p.modified)}</time
								></td
							>
						</tr>
					{/each}
				</tbody>
			</table>
		{/if}
	{/each}
</Section>
