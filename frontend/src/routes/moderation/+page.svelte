<script lang="ts">
	import WorkCard from '$lib/WorkCard.svelte';
	import Pager from '$lib/Pager.svelte';
	import { page } from '$app/state';
	import { invalidateAll } from '$app/navigation';
	import client from '$lib/api';

	let { data } = $props();

	const tabs = [
		{ key: 'all', label: 'All' },
		{ key: 'pending', label: 'Pending' },
		{ key: 'flagged', label: 'Flagged' },
		{ key: 'appealed', label: 'Appealed' },
		{ key: 'sources', label: 'Pending Sources' }
	];

	const approveSource = async (sourceId: number) => {
		await client.POST('/api/source/approve', {
			params: { query: { source_id: sourceId } }
		});
		invalidateAll();
	};

	const rejectSource = async (sourceId: number) => {
		const reason = prompt('Rejection reason:');
		if (reason === null) return;
		await client.POST('/api/source/reject', {
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
		<p>No pending sources.</p>
	{:else}
		<table class="w-full">
			<thead>
				<tr>
					<th>Source</th>
					<th>Work</th>
					<th>Added by</th>
					<th>Date</th>
					<th>Actions</th>
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
								Approve
							</button>
							<button
								class="border px-2 py-0.5"
								onclick={() => rejectSource(source.id)}
							>
								Reject
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
				base_url={page.url}
			/>
		{/if}
	{/if}
{:else if data.queue}
	{#if data.queue.items.length === 0}
		<p>Queue is empty.</p>
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
				base_url={page.url}
			/>
		{/if}
	{/if}
{/if}
