import type { Meta, StoryObj } from '@storybook/sveltekit';
import type { ComponentProps } from 'svelte';
import ActivityHeatmap from './ActivityHeatmap.svelte';
import type { ProfileActivity } from './types';

/**
 * The API returns a window rolling back from today (`start` = `end` − 364), so it starts and
 * ends mid-month rather than on a calendar year. A fixed pair of dates stands in for it here
 * so the stories render identically on every run.
 */
const START = '2025-08-08';
const END = '2026-08-07';
const WINDOW_DAYS = 365;
const MS_PER_DAY = 86_400_000;

const startTime = Date.parse(`${START}T00:00:00Z`);
const dayAt = (index: number) =>
	new Date(startTime + index * MS_PER_DAY).toISOString().slice(0, 10);

/**
 * A deterministic 0..1 value per day index, standing in for a seeded RNG — `Math.random()`
 * would make the stories non-reproducible.
 */
const noise = (index: number) => {
	let x = Math.imul(index + 1, 2654435761);
	x ^= x >>> 15;
	x = Math.imul(x, 2246822519);
	x ^= x >>> 13;
	return (x >>> 0) / 4294967296;
};

const buildActivity = (count: (value: number) => number): ProfileActivity => {
	const days = [];
	let total = 0;

	for (let index = 0; index < WINDOW_DAYS; index++) {
		const value = count(noise(index));
		if (value <= 0) continue;
		days.push({ date: dayAt(index), count: value });
		total += value;
	}

	return { start: START, end: END, total, days };
};

/** An active user: most days have contributions, spread over the whole range of levels. */
const dense = buildActivity((value) => (value < 0.12 ? 0 : 1 + Math.floor(value * 11)));

/** An occasional contributor: a handful of low-count days scattered across the year. */
const sparse = buildActivity((value) => (value < 0.9 ? 0 : 1 + Math.floor(value * 3)));

const meta = {
	component: ActivityHeatmap,
	args: { activity: dense }
} satisfies Meta<ComponentProps<typeof ActivityHeatmap>>;

export default meta;
type Story = StoryObj<ComponentProps<typeof ActivityHeatmap>>;

/** A year with contributions on most days. */
export const Dense: Story = {
	args: { activity: dense }
};

/** A year with only a few scattered contributions. */
export const Sparse: Story = {
	args: { activity: sparse }
};
