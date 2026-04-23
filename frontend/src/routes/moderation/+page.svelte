<script lang="ts">
	import WorkCard from '$lib/WorkCard.svelte';
	import Pager from '$lib/Pager.svelte';
	import { page } from '$app/state';
	import { invalidateAll } from '$app/navigation';
	import client from '$lib/api';
	import { m } from '$lib/paraglide/messages.js';

	let { data } = $props();

	const tabs: { key: typeof data.tab; label: string }[] = [
		{ key: 'all', label: m.keen_soft_crow_relish() },
		{ key: 'pending', label: m.such_actual_okapi_dare() },
		{ key: 'flagged', label: m.tangy_busy_liger_burn() },
		{ key: 'appealed', label: m.brief_flat_bullock_dance() },
		{ key: 'sources', label: m.suave_gray_stork_type() }
	];

	const approveSource = async (sourceId: number) => {
		await client.POST('/api/upload/approve', {
			params: { query: { source_id: sourceId } }
		});
		invalidateAll();
	};

	const rejectSource = async (sourceId: number) => {
		const reason = prompt(m.honest_tangy_butterfly_dream());
		if (!reason?.trim()) {
			alert(m.fun_bland_llama_twirl({ thing: m.honest_tangy_butterfly_dream() }));
			return;
		}
		await client.POST('/api/upload/reject', {
			params: { query: { source_id: sourceId, reason } }
		});
		invalidateAll();
	};
</script>

<div class="mb-4 flex gap-2">
	{#each tabs as tab (tab.key)}
		<a
			href="?tab={tab.key}"
			class={[
				'border px-3 py-1',
				data.tab === tab.key ? 'bg-otodb-content-primary text-otodb-bg-primary' : ''
			]}
		>
			{tab.label}
		</a>
	{/each}
</div>

{#if data.tab === 'sources' && data.sources}
	{#if data.sources.items.length === 0}
		<p>{m.proud_orange_parrot_amuse()}</p>
	{:else}
		<table class="w-full">
			<thead>
				<tr>
					<th>{m.extra_brave_tapir_skip()}</th>
					<th>{m.grand_merry_fly_succeed()}</th>
					<th>{m.each_born_quail_gleam()}</th>
					<th>{m.super_agent_pigeon_aim()}</th>
					<th>{m.mild_full_sloth_work()}</th>
				</tr>
			</thead>
			<tbody>
				{#each data.sources.items as source (source.id)}
					<tr>
						<td>
							<a href={source.url} target="_blank" rel="noopener">
								{source.title || source.url}
							</a>
						</td>
						<td>
							{#if source.media}
								<a href="/work/{source.media}"
									>{source.media_title || `Work #${source.media}`}</a
								>
							{:else}
								-
							{/if}
						</td>
						<td
							><a href="/profile/{source.added_by.username}"
								>{source.added_by.username}</a
							></td
						>
						<td>{source.published_date ?? '-'}</td>
						<td class="flex gap-2">
							<button
								class="border px-2 py-0.5"
								onclick={() => approveSource(source.id)}
							>
								{m.lucky_bold_hornet_push()}
							</button>
							<button
								class="border px-2 py-0.5"
								onclick={() => rejectSource(source.id)}
							>
								{m.alive_blue_marlin_push()}
							</button>
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
		{#if data.sources.count}
			<Pager
				n_count={data.sources.count}
				page={data.page}
				page_size={data.batchSize}
				base_url={page.url.toString()}
			/>
		{/if}
	{/if}
{:else if data.queue}
	{#if data.queue.items.length === 0}
		<p>{m.elegant_these_chicken_bless()}</p>
	{:else}
		<div class="grid grid-cols-[repeat(auto-fill,minmax(192px,1fr))] gap-x-4 gap-y-4">
			{#each data.queue.items as work (work.id)}
				<WorkCard {work} />
			{/each}
		</div>
		{#if data.queue.count}
			<Pager
				n_count={data.queue.count}
				page={data.page}
				page_size={data.batchSize}
				base_url={page.url.toString()}
			/>
		{/if}
	{/if}
{/if}
