<script lang="ts">
	import { m } from '$lib/paraglide/messages';
	import { getLocale } from '$lib/paraglide/runtime';
	import type { ProfileActivity } from './types';

	interface Props {
		activity: ProfileActivity;
	}

	const { activity }: Props = $props();

	const MS_PER_DAY = 86_400_000;
	const DAYS_PER_WEEK = 7;

	/**
	 * A fixed Sunday, used only to render the weekday labels. Hard-coded rather than derived
	 * from the current date so the component stays deterministic.
	 */
	const REFERENCE_SUNDAY = Date.UTC(2024, 0, 7);

	/** Every date the component handles is a UTC midnight timestamp of an ISO `YYYY-MM-DD`. */
	const parseDay = (date: string) => Date.parse(`${date}T00:00:00Z`);

	const startTime = $derived(parseDay(activity.start));
	const endTime = $derived(parseDay(activity.end));

	/** Pad back to the Sunday on or before `start` so every column is a full week. */
	const gridStartTime = $derived(startTime - new Date(startTime).getUTCDay() * MS_PER_DAY);
	const weeks = $derived(Math.ceil(((endTime - gridStartTime) / MS_PER_DAY + 1) / DAYS_PER_WEEK));

	const counts = $derived(new Map(activity.days.map(({ date, count }) => [parseDay(date), count])));
	const maxCount = $derived(activity.days.reduce((max, { count }) => Math.max(max, count), 0));

	const level = (count: number) => {
		if (count === 0 || maxCount === 0) return 0;
		return Math.min(4, Math.max(1, Math.ceil((count / maxCount) * 4)));
	};

	const dayFormat = $derived(
		new Intl.DateTimeFormat(getLocale(), { dateStyle: 'long', timeZone: 'UTC' })
	);
	const monthFormat = $derived(
		new Intl.DateTimeFormat(getLocale(), { month: 'short', timeZone: 'UTC' })
	);
	const weekdayFormat = $derived(
		new Intl.DateTimeFormat(getLocale(), { weekday: 'short', timeZone: 'UTC' })
	);

	/** GitHub-style: only every other weekday is labelled, to keep the axis readable. */
	const weekdayLabels = $derived(
		Array.from({ length: DAYS_PER_WEEK }, (_, row) =>
			row % 2 === 1 ? weekdayFormat.format(REFERENCE_SUNDAY + row * MS_PER_DAY) : ''
		)
	);

	type Cell = { count: number; label: string } | null;

	const columns: { month: string; cells: Cell[] }[] = $derived.by(() => {
		const result: { month: string; cells: Cell[] }[] = [];
		let labelledMonth = -1;

		for (let week = 0; week < weeks; week++) {
			const weekStart = gridStartTime + week * DAYS_PER_WEEK * MS_PER_DAY;
			const cells = Array.from({ length: DAYS_PER_WEEK }, (_, row): Cell => {
				const time = weekStart + row * MS_PER_DAY;
				// Days before `start` (the leading pad) and after `end` are rendered as gaps.
				if (time < startTime || time > endTime) return null;

				const count = counts.get(time) ?? 0;
				return {
					count,
					label: m.warm_still_marmot_reflect({ count, date: dayFormat.format(time) })
				};
			});

			// A column carries a month label the first time that month appears along the top.
			const first = Math.max(weekStart, startTime);
			const monthIndex = first <= endTime ? new Date(first).getUTCMonth() : labelledMonth;
			const month = monthIndex === labelledMonth ? '' : monthFormat.format(first);
			labelledMonth = monthIndex;

			result.push({ month, cells });
		}

		return result;
	});
</script>

<p class="mb-2">{m.plain_swift_otter_gather({ count: activity.total })}</p>

<div class="flex gap-1 overflow-x-auto pb-1">
	<div class="text-otodb-content-fainter grid grid-rows-[1rem_repeat(7,0.75rem)] gap-[3px] text-xs">
		<span></span>
		{#each weekdayLabels as label, row (row)}
			<span class="flex items-center pr-1 leading-none">{label}</span>
		{/each}
	</div>

	<div
		class="grid [grid-auto-columns:0.75rem] grid-flow-col grid-rows-[1rem_repeat(7,0.75rem)] gap-[3px]"
	>
		{#each columns as column, week (week)}
			<span class="text-otodb-content-fainter relative text-xs">
				{#if column.month}
					<span class="absolute top-0 left-0 whitespace-nowrap">{column.month}</span>
				{/if}
			</span>
			{#each column.cells as cell, row (row)}
				{#if cell}
					<span class="cell" data-level={level(cell.count)} title={cell.label}></span>
				{:else}
					<span></span>
				{/if}
			{/each}
		{/each}
	</div>
</div>

<style>
	.cell {
		/* A hairline keeps empty days visible against the surrounding `bg-faint` panel. */
		outline: 1px solid color-mix(in oklab, var(--otodb-color-content-fainter) 20%, transparent);
		outline-offset: -1px;

		&[data-level='0'] {
			background-color: var(--otodb-color-bg-faint);
		}
		&[data-level='1'] {
			background-color: color-mix(in oklab, green 25%, var(--otodb-color-bg-faint));
		}
		&[data-level='2'] {
			background-color: color-mix(in oklab, green 45%, var(--otodb-color-bg-faint));
		}
		&[data-level='3'] {
			background-color: color-mix(in oklab, green 70%, var(--otodb-color-bg-faint));
		}
		&[data-level='4'] {
			background-color: color-mix(in oklab, green 95%, var(--otodb-color-bg-faint));
		}
	}
</style>
