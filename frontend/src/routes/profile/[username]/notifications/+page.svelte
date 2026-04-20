<script lang="ts">
	import Section from '$lib/Section.svelte';
	import { goto, invalidateAll } from '$app/navigation';
	import Pager from '$lib/Pager.svelte';
	import client from '$lib/api';
	import { buildEntityRoutes } from '$lib/enums';
	import { m } from '$lib/paraglide/messages.js';
	import { NotificationReason } from '$lib/schema.js';

	let { data } = $props();

	const dismiss = async (id: number, dismissed: boolean, target: string) => {
		if (!dismissed)
			await client.PUT('/api/profile/notification', {
				fetch,
				params: { query: { notif_id: id } }
			});
		goto(target, { invalidateAll: true });
	};
</script>

<Section title={m.free_keen_wren_exhale()}>
	{#if data.notifications.count}
		<table class="w-full">
			<tbody>
				{#each data.notifications.items as n, i (i)}
					<tr>
						{#if n.revision}
							<td class={{ 'opacity-40': n.dismissed }}
								>{m.livid_real_platypus_borrow()}</td
							><td
								><button
									class={{ 'opacity-40': n.dismissed }}
									onclick={() =>
										dismiss(n.id, n.dismissed, `/revision/${n.revision}`)}
									>{m.arable_direct_swan_glow()} #{n.revision}</button
								></td
							>
						{:else if n.comment}
							<td class={{ 'opacity-40': n.dismissed }}
								>{m.curly_these_mule_ascend()}
							</td>
							<td>
								{#if n.comment}
									{@const route = buildEntityRoutes(n.comment[0], n.comment[1])}
									<button
										class={{ 'opacity-40': n.dismissed }}
										onclick={() => dismiss(n.id, n.dismissed, route)}
										>{route}
									</button>
								{/if}
							</td>
						{:else if n.post}
							<td class={{ 'opacity-40': n.dismissed }}
								>{n.reason === NotificationReason.Revision_Linked
									? m.aqua_safe_beetle_list()
									: n.reason === NotificationReason.Mention
										? m.vexed_polite_haddock_trim()
										: m.curly_these_mule_ascend()}</td
							><td
								><button
									class={{ 'opacity-40': n.dismissed }}
									onclick={() => dismiss(n.id, n.dismissed, `/post/${n.post}`)}
									>/post/{n.post}</button
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
									}}>{m.even_alert_grebe_taste()}</button
								>{/if}</td
						>
					</tr>
				{/each}
			</tbody>
		</table>
		{#if data.notifications?.count}
			<Pager
				n_count={data.notifications.count}
				page={data.page}
				page_size={data.batch_size}
			/>
		{/if}
	{:else}
		{m.wacky_weird_swallow_trust()}
	{/if}
</Section>
