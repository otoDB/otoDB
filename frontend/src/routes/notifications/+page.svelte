<script lang="ts">
	import Section from '$lib/Section.svelte';
	import type { PageProps } from './$types';
	import { m } from '$lib/paraglide/messages.js';
	import Pager from '$lib/Pager.svelte';
	import { CommentModelRoutes } from '$lib/enums';
	import { goto, invalidateAll } from '$app/navigation';
	import client from '$lib/api';

	let { data }: PageProps = $props();

	const dismiss = async (id: number, dismissed: boolean, target: string) => {
		if (!dismissed)
			await client.PUT('/api/profile/notification', {
				fetch,
				params: { query: { notif_id: id } }
			});
		goto(target, { invalidateAll: true });
	};
</script>

<svelte:head>
	<title>{m.free_keen_wren_exhale()}</title>
</svelte:head>

<Section title={m.free_keen_wren_exhale()}>
	<table class="w-full">
		<tbody>
			{#each data.notifications.items as n, i (i)}
				<tr>
					{#if n.revision}
						<td class={{ 'opacity-40': n.dismissed }}
							>An entity you are subscribed to was modified in a revision.</td
						><td
							><button
								class={{ 'opacity-40': n.dismissed }}
								onclick={() =>
									dismiss(n.id, n.dismissed, `/revision/${n.revision}`)}
								>{m.arable_direct_swan_glow()} #{n.revision}</button
							></td
						>
					{:else if n.comment}
						<td class={{ 'opacity-40': n.dismissed }}>New reply.</td><td
							><button
								class={{ 'opacity-40': n.dismissed }}
								onclick={() =>
									dismiss(
										n.id,
										n.dismissed,
										`/${CommentModelRoutes[n.comment[0]]}/${n.comment[1]}`
									)}>View</button
							></td
						>
					{/if}
					<td
						>{#if n.dismissed}<button
								onclick={async () => {
									await client.DELETE('/api/profile/notification', {
										fetch,
										params: { query: { notif_id: n.id } }
									});
									invalidateAll();
								}}>Delete</button
							>{/if}</td
					>
				</tr>
			{/each}
		</tbody>
	</table>
	{#if data.notifications?.count}
		<Pager n_count={data.notifications.count} page={data.page} page_size={data.batch_size} />
	{/if}
</Section>
