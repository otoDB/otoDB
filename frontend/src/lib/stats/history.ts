/** One day on which at least one work was added, and the total it left behind. */
export type WorkHistoryPoint = {
	/** `YYYY-MM-DD`, in UTC. */
	date: string;
	/** Works in the database at the end of that day. */
	total: number;
};

export type MonthlyBucket = {
	/** `YYYY-MM`. */
	month: string;
	/** Works in the database at the end of the month. */
	total: number;
};

const monthOf = (date: string) => date.slice(0, 7);

const nextMonth = (month: string) => {
	const year = Number(month.slice(0, 4));
	const m = Number(month.slice(5, 7));
	return m === 12 ? `${year + 1}-01` : `${year}-${String(m + 1).padStart(2, '0')}`;
};

/**
 * Collapse the daily series into one bucket per month, filling in the months
 * where nothing was added so the bars stay evenly spaced in time. The running
 * total is carried across those empty months rather than dropping to zero.
 *
 * `points` must be ascending, which the endpoint guarantees.
 */
export function bucketByMonth(points: WorkHistoryPoint[]): MonthlyBucket[] {
	if (points.length === 0) return [];

	const last = monthOf(points[points.length - 1].date);

	const buckets: MonthlyBucket[] = [];
	let carried = 0;
	let i = 0;
	for (let month = monthOf(points[0].date); month <= last; month = nextMonth(month)) {
		while (i < points.length && monthOf(points[i].date) === month) carried = points[i++].total;
		buckets.push({ month, total: carried });
	}
	return buckets;
}

/** One bar of `BarChart.svelte`. */
export type ChartBar = {
	value: number;
	/** Drawn under the bar. Left out for bars that would crowd the axis. */
	label?: string;
	/** Hover/assistive text for the bar. */
	title: string;
};

/**
 * Tick values from zero to at least `max`, on a round step. The last tick is the
 * top of the chart's value axis, so it is always greater than zero.
 */
export function niceTicks(max: number): number[] {
	const safeMax = Math.max(1, max);
	const raw = safeMax / 4;
	const magnitude = 10 ** Math.floor(Math.log10(raw));
	// The last candidate is always >= raw, so `find` always hits. Rounded so the step
	// stays a whole number of works; under a magnitude of one every candidate rounds
	// away and the floor of 1 takes over.
	const candidates = [1, 2, 2.5, 5, 10].map((m) => m * magnitude);
	const step = Math.max(1, Math.round(candidates.find((s) => s >= raw) ?? magnitude));

	const ticks: number[] = [];
	for (let v = 0; v <= Math.ceil(safeMax / step) * step; v += step) ticks.push(v);
	return ticks;
}
