<script lang="ts">
	let {
		events,
		isEditor = false,
		showTarget = true
	}: {
		events: {
			items: {
				event_type: number;
				event_id: number;
				work_id: number | null;
				source_id: number | null;
				by: { id: number; username: string } | null;
				reason: string;
				status: number | null;
				event_at: string;
			}[];
			count: number;
		} | null;
		isEditor?: boolean;
		showTarget?: boolean;
	} = $props();

	const eventLabels: Record<number, string> = {
		0: 'Flagged',
		1: 'Appealed',
		2: 'Disapproved',
		3: 'Approved',
		4: 'Mod Action'
	};

	const modActionCategoryLabels: Record<number, string> = {
		1: 'Delisted',
		10: 'Source Approved',
		11: 'Source Rejected'
	};

	const getEventLabel = (event: { event_type: number; status: number | null }) => {
		if (event.event_type === 4 && event.status !== null) {
			return modActionCategoryLabels[event.status] ?? 'Mod Action';
		}
		return eventLabels[event.event_type] ?? event.event_type;
	};
</script>

{#if events?.items?.length}
	<table class="w-full">
		<thead>
			<tr>
				<th>Event</th>
				{#if showTarget}
					<th>Target</th>
				{/if}
				<th>Reason</th>
				<th>By</th>
				<th>Date</th>
			</tr>
		</thead>
		<tbody>
			{#each events.items as event (event.event_id + event.event_type)}
				<tr>
					<td>{getEventLabel(event)}</td>
					{#if showTarget}
						<td>
							{#if event.work_id}
								<a href="/work/{event.work_id}">Work #{event.work_id}</a>
							{/if}
							{#if event.source_id}
								{#if event.work_id},
								{/if}
								<a href="/source/{event.source_id}">Source #{event.source_id}</a>
							{/if}
							{#if !event.work_id && !event.source_id}
								-
							{/if}
						</td>
					{/if}
					<td class="max-w-xs truncate">{event.reason || '-'}</td>
					<td>
						{#if event.by}
							<a href="/profile/{event.by.username}">{event.by.username}</a>
						{:else}
							-
						{/if}
					</td>
					<td>{new Date(event.event_at).toLocaleDateString()}</td>
				</tr>
			{/each}
		</tbody>
	</table>
{:else}
	<p>No moderation history.</p>
{/if}
