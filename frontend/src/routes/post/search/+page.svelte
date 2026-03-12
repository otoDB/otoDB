<script lang="ts">
	import Section from '$lib/Section.svelte';
	import type { PageProps } from './$types';
	import { m } from '$lib/paraglide/messages.js';
	import { EntityModelRoutes, PostCategories } from '$lib/enums';
	import { timeAgo } from '$lib/ui';
	import Pager from '$lib/Pager.svelte';

	let { data }: PageProps = $props();
</script>

<Section
	title={m.just_salty_anaconda_nourish()}
	type={m.mean_top_antelope_love()}
	menuLinks={data.links}
>
	<form target="_self" method="get">
		<label class="block"
			>{m.plane_awful_bobcat_spark()}
			<select name="category" value={data.category ?? -1}>
				<option value={-1}>{m.keen_soft_crow_relish()}</option>
				{#each PostCategories as c, i (i)}
					<option value={i}>{c()}</option>
				{/each}
			</select>
		</label>
		<input
			type="text"
			name="query"
			placeholder="{m.mean_top_antelope_love()}..."
			value={data.query}
		/>
		<input type="submit" />
	</form>
	<hr class="my-5" />

	<table class="w-full table-fixed">
		<thead>
			<tr>
				<th class="text-left">{m.large_factual_octopus_exhale()}</th>
				<th class="w-32 text-left">{m.plane_awful_bobcat_spark()}</th>
				<th class="w-32 text-left">{m.crisp_red_canary_tickle()}</th>
				<th class="w-64 text-right">{m.super_agent_pigeon_aim()}</th>
			</tr>
		</thead><tbody>
			{#each data.results.items as post, i (i)}
				<tr>
					<td>
						<a href="/post/{post.id}">{post.title}</a>
						{#if post.entities?.length}
							<span class="text-otodb-content-fainter block text-xs">
								{#each post.entities as { id, entity }, j (j)}
									{#if j > 0},
									{/if}
									<a href="/{EntityModelRoutes[entity]}/{id}"
										>{EntityModelRoutes[entity]}/{id}</a
									>
								{/each}
							</span>
						{/if}
					</td>
					<td>{PostCategories[post.category]()}</td>
					<td><a href="/profile/{post.added_by.username}">{post.added_by.username}</a></td
					>
					<td class="text-right">
						<time title={new Date(post.modified).toLocaleString()}
							>{timeAgo(post.modified)}</time
						>
					</td>
				</tr>
			{/each}
		</tbody>
	</table>
	<Pager n_count={data.results.count} page={data.page} page_size={data.batch_size} />
</Section>
