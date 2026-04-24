<script lang="ts">
	import Section from '$lib/Section.svelte';
	import { goto, invalidateAll } from '$app/navigation';
	import Pager from '$lib/Pager.svelte';
	import TimeAgo from '$lib/TimeAgo.svelte';
	import client from '$lib/api';
	import { buildEntityRoutes } from '$lib/enums';
	import { isSOV, isSVO } from '$lib/enums/language';
	import { routeNames } from '$lib/enums/route.js';
	import { m } from '$lib/paraglide/messages.js';
	import { getLocale } from '$lib/paraglide/runtime.js';
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

	const remove = async (id: number) => {
		await client.DELETE('/api/profile/notification', {
			fetch,
			params: { query: { notif_id: id } }
		});
		invalidateAll();
	};
</script>

<div
	class="grid grid-cols-[repeat(auto-fill,minmax(max(calc(50%-var(--spacing)*2),min(100%,576px)),1fr))] gap-x-4"
>
	<Section title={m.free_keen_wren_exhale()}>
		{#if data.nonsub_notifications?.count}
			<table class="w-full">
				<tbody>
					{#each data.nonsub_notifications.items as n, i (i)}
						<tr>
							{#if n.comment}
								{@const route = buildEntityRoutes(n.comment[0], n.comment[1])}
								<td class={{ 'opacity-40': n.dismissed }}
									>{m.curly_these_mule_ascend()}</td
								>
								<td class={{ 'opacity-40': n.dismissed }}>
									<button onclick={() => dismiss(n.id, n.dismissed, route)}
										>{route}
									</button>
								</td>
							{:else if n.post}
								<td class={{ 'opacity-40': n.dismissed }}
									>{n.reason === NotificationReason.Thread_Linked
										? m.aqua_safe_beetle_list()
										: n.reason === NotificationReason.Mention
											? m.vexed_polite_haddock_trim()
											: m.curly_these_mule_ascend()}</td
								>
								<td class={{ 'opacity-40': n.dismissed }}
									><button
										onclick={() =>
											dismiss(n.id, n.dismissed, `/post/${n.post}`)}
										>/post/{n.post}</button
									></td
								>
							{/if}
							<td class={{ 'opacity-40': n.dismissed }}
								><TimeAgo date={n.created_at} /></td
							>
							<td
								>{#if n.dismissed}<button onclick={() => remove(n.id)}
										>{m.even_alert_grebe_taste()}</button
									>{/if}</td
							>
						</tr>
					{/each}
				</tbody>
			</table>
			<Pager
				n_count={data.nonsub_notifications.count}
				page={data.page}
				page_size={data.batch_size}
			/>
		{:else}
			{m.wacky_weird_swallow_trust()}
		{/if}
	</Section>

	<Section title={m.house_patient_cuckoo_trust()}>
		{#if data.sub_notifications?.count}
			<table class="w-full">
				<tbody>
					{#each data.sub_notifications.items as n, i (i)}
						<tr>
							<td class={{ 'opacity-40': n.dismissed }}
								><button
									onclick={() =>
										dismiss(n.id, n.dismissed, `/revision/${n.revision}`)}
									>#{n.revision}</button
								>
							</td>
							<td class={{ 'opacity-40': n.dismissed }}
								>{typeof n.revision_route === 'number'
									? routeNames[n.revision_route]()
									: ''}</td
							>
							<td class={{ 'opacity-40': n.dismissed }}>
								{#if isSVO(getLocale())}
									{m.curly_safe_lynx_fond()}
								{/if}
								{#if n.revision_user}
									<a href="/profile/{n.revision_user}">{n.revision_user}</a>
								{/if}
								{#if isSOV(getLocale())}
									{m.curly_safe_lynx_fond()}
								{/if}
							</td>
							<td class={{ 'opacity-40': n.dismissed }}
								><TimeAgo date={n.created_at} /></td
							>
							<td
								>{#if n.dismissed}<button onclick={() => remove(n.id)}
										>{m.even_alert_grebe_taste()}</button
									>{/if}</td
							>
						</tr>
					{/each}
				</tbody>
			</table>
			<Pager
				n_count={data.sub_notifications.count}
				page={data.sub_page}
				page_size={data.batch_size}
				param_name="sub_page"
			/>
		{:else}
			{m.wacky_weird_swallow_trust()}
		{/if}
	</Section>
</div>
