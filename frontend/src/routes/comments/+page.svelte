<script lang="ts">
	import Section from '$lib/Section.svelte';
	import type { PageProps } from './$types';
	import { m } from '$lib/paraglide/messages.js';
	import Pager from '$lib/Pager.svelte';
	import { CommentModelRoutes } from '$lib/enums';
	import { timeAgo } from '$lib/ui';

	let { data }: PageProps = $props();
</script>

<Section title={m.same_broad_haddock_pinch()}>
	<table>
		<tbody>
			{#each data.comments?.items as c, i (i)}
				<tr
					><td
						><a href="{CommentModelRoutes[c.entity_type]}/{c.entity_id}"
							>{CommentModelRoutes[c.entity_type]}/{c.entity_id}</a
						></td
					><td><a href="/profile/{c.user.username}">{c.user.username}</a></td><td
						>{c.comment}</td
					><td>{timeAgo(c.submit_date)}</td></tr
				>
			{/each}
		</tbody>
	</table>
	{#if data.comments?.count}
		<Pager n_count={data.comments.count} page={data.page} page_size={data.batch_size} />
	{/if}
</Section>
