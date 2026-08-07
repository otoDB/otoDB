import type { Meta, StoryObj } from '@storybook/sveltekit';
import type { ComponentProps } from 'svelte';
import BarChart from './BarChart.svelte';
import type { ChartBar } from './history';

/** A rising series shaped like a cumulative count, one bar per month. */
const cumulative = (months: number, monthly: number): ChartBar[] =>
	Array.from({ length: months }, (_, i) => {
		const value = (i + 1) * monthly;
		return {
			value,
			label: i % 12 === 0 ? String(2019 + Math.floor(i / 12)) : undefined,
			title: `${value} works`
		};
	});

const meta = {
	component: BarChart,
	args: {
		bars: cumulative(90, 220),
		ariaLabel: 'Works over time'
	}
} satisfies Meta<ComponentProps<typeof BarChart>>;

export default meta;
type Story = StoryObj<ComponentProps<typeof BarChart>>;

/** The density the `/stats/works` page renders at: several years of monthly bars. */
export const Default: Story = {};

/** Few enough bars that each one is wide, which is how a single year reads. */
export const Sparse: Story = {
	args: {
		bars: cumulative(12, 180)
	}
};

/** Small values, where the axis has to pick a step of a few units rather than hundreds. */
export const SmallValues: Story = {
	args: {
		bars: cumulative(12, 1)
	}
};
