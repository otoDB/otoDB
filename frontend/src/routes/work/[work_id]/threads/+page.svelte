<script lang="ts">
	import Pager from '$lib/Pager.svelte';
	import { m } from '$lib/paraglide/messages';
	import Section from '$lib/Section.svelte';
	import { timeAgo } from '$lib/ui';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
</script>

<Section title={data.title} type={m.grand_merry_fly_succeed()} menuLinks={data.links}>
	<a href="/post/new?category=3&entity=w{data.id}">{m.antsy_aloof_horse_grace()}</a>
	{#if data.threads.items.length}
		<table class="w-full">
			<thead>
				<tr>
					<th>{m.large_factual_octopus_exhale()}</th>
					<th>{m.crisp_red_canary_tickle()}</th>
					<th>{m.super_agent_pigeon_aim()}</th>
				</tr>
			</thead><tbody>
				{#each data.threads.items as post, i (i)}
					<tr>
						<td><a href="/post/{post.id}">{post.title}</a></td>
						<td
							><a href="/profile/{post.added_by.username}">{post.added_by.username}</a
							></td
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
		<Pager n_count={data.threads.count} page={data.page} page_size={data.batch_size} />
	{/if}
</Section>
