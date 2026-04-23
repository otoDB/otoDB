<script lang="ts">
	import { m } from './paraglide/messages';
	import type { components } from './schema';

	let {
		events,
		showTarget = true
	}: {
		events: {
			items: components['schemas']['ModerationEventSchema'][];
			count: number;
		} | null;
		showTarget?: boolean;
	} = $props();

	const eventLabels: Record<number, string> = {
		0: m.tangy_busy_liger_burn(),
		1: m.brief_flat_bullock_dance(),
		2: m.stale_vexed_hare_pray(),
		3: m.spare_few_kudu_learn(),
		4: m.loud_heroic_chipmunk_gasp()
	};

	const modActionCategoryLabels: Record<number, string> = {
		1: m.quiet_upper_pig_yell(),
		10: m.ideal_aloof_racoon_blend(),
		11: m.silly_slimy_lemur_link()
	};

	const getEventLabel = (event: { event_type: number; status: number | null }) => {
		if (event.event_type === 4 && event.status !== null) {
			return modActionCategoryLabels[event.status] ?? m.loud_heroic_chipmunk_gasp();
		}
		return eventLabels[event.event_type] ?? event.event_type;
	};
</script>

{#if events?.items?.length}
	<table class="w-full">
		<thead>
			<tr>
				<th>{m.awake_aware_quail_bake()}</th>
				{#if showTarget}
					<th>{m.funny_muddy_skate_learn()}</th>
				{/if}
				<th>{m.weary_spicy_fly_attend()}</th>
				<th>{m.last_sleek_butterfly_quiz()}</th>
				<th>{m.super_agent_pigeon_aim()}</th>
			</tr>
		</thead>
		<tbody>
			{#each events.items as event (event.event_id)}
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
	<p>{m.gray_still_wolf_nurture()}</p>
{/if}
