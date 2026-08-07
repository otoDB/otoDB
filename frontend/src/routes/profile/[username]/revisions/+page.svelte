<script lang="ts">
	import { invalidateAll } from '$app/navigation';
	import { page } from '$app/state';
	import client from '$lib/api.js';
	import { dirtyClick } from '$lib/dirty';
	import { routeNames } from '$lib/enums/route.js';
	import { hasUserLevel } from '$lib/enums/userLevel.js';
	import Pager from '$lib/Pager.svelte';
	import { m } from '$lib/paraglide/messages.js';
	import { Levels } from '$lib/schema.js';
	import Section from '$lib/Section.svelte';
	import Time from '$lib/Time.svelte';
	import { callSavingToast } from '$lib/toast';

	let { data } = $props();

	let rollbackDate = $state('');
	const is_mod = $derived(hasUserLevel(data.user?.level, Levels.Mod));
	const username = $derived(data.profile.username);

	const rollbackSince = async (date: string, label: string) => {
		if (!date) return;
		if (!confirm(m.tame_swift_heron_plead({ username, label }))) return;
		const p = client.POST('/api/history/rollback_user', {
			fetch,
			params: { query: { username, date } }
		});
		callSavingToast(p);
		const { error } = await p;
		if (!error) await invalidateAll();
	};
</script>

<svelte:head>
	<meta name="robots" content="noindex" />
</svelte:head>

<Section title={data.profile.username} type={m.fuzzy_crazy_cobra_lead()} menuLinks={data.links}>
	{#if is_mod}
		<div class="my-4 flex items-center gap-2">
			<label>
				<input type="date" bind:value={rollbackDate} />
			</label>
			<button {@attach dirtyClick(() => rollbackSince(rollbackDate, rollbackDate))}
				>{m.lucky_brave_marten_glide()}</button
			>
		</div>
	{/if}
	{#if data.revisions?.items.length}
		<table class="w-full">
			<tbody>
				{#each data.revisions?.items as r, i (i)}
					<tr>
						<td>
							<a href="/revision/{r.id}">#{r.id}</a>
						</td>
						<td>{r.route ? routeNames[r.route]() : ''}</td>
						<td>
							<Time format="relative" date={r.date} />
						</td>
						{#if is_mod}
							<td>
								<button {@attach dirtyClick(() => rollbackSince(r.date, `#${r.id}`))}>
									{m.bold_keen_otter_vault()}
								</button>
							</td>
						{/if}
					</tr>
				{/each}
			</tbody>
		</table>
	{:else}
		<p>{m.spry_dizzy_mouse_roam()}</p>
	{/if}
	{#if data.revisions?.count}
		<Pager
			n_count={data.revisions.count}
			page_size={data.batch_size}
			base_url={page.url.toString()}
		/>
	{/if}
</Section>
