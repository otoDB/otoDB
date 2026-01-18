<script lang="ts">
	import Section from '$lib/Section.svelte';
	import type { PageProps } from './$types';
	import { m } from '$lib/paraglide/messages.js';
	import client from '$lib/api';
	import LoadMoreButton from '$lib/LoadMoreButton.svelte';
	import { PostCategories } from '$lib/enums';

	let { data }: PageProps = $props();
	let results = $derived(data.results!.items);

	const fetchNextBatch = () =>
		client.GET('/api/list/search', {
			fetch,
			params: {
				query: {
					query: data.query,
					categry: data.category,
					limit: data.batch_size,
					offset: results.length
				}
			}
		});
</script>

<svelte:head>
	<title
		>{m.mild_loud_shad_enchant({
			type: m.mean_top_antelope_love(),
			name: m.just_salty_anaconda_nourish()
		})}</title
	>
</svelte:head>

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
			{#each results as post, i (i)}
				<tr>
					<td><a href="/post/{post.id}">{post.title}</a></td>
					<td>{PostCategories[post.category]()}</td>
					<td><a href="/profile/{post.added_by.username}">{post.added_by.username}</a></td
					>
					<td>{new Date(post.modified).toDateString()}</td>
				</tr>
			{/each}
		</tbody>
	</table>
	<LoadMoreButton bind:results maxCount={data.results!.count} {fetchNextBatch} />
</Section>
