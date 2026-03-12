<script lang="ts">
	import Section from '$lib/Section.svelte';
	import type { PageProps } from './$types';
	import { m } from '$lib/paraglide/messages.js';
	import { PostCategories } from '$lib/enums';
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

	<table class="w-full">
		<thead>
			<tr>
				<th>{m.large_factual_octopus_exhale()}</th>
				<th>{m.plane_awful_bobcat_spark()}</th>
				<th>{m.crisp_red_canary_tickle()}</th>
				<th>{m.super_agent_pigeon_aim()}</th>
			</tr>
		</thead><tbody>
			{#each data.results.items as post, i (i)}
				<tr>
					<td><a href="/post/{post.id}">{post.title}</a></td>
					<td>{PostCategories[post.category]()}</td>
					<td><a href="/profile/{post.added_by.username}">{post.added_by.username}</a></td
					>
					<td
						><time title={new Date(post.modified).toLocaleString()}
							>{timeAgo(post.modified)}</time
						></td
					>
				</tr>
			{/each}
		</tbody>
	</table>
	<Pager n_count={data.results.count} page={data.page} page_size={data.batch_size} />
</Section>
