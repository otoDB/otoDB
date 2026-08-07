<script lang="ts">
	import { niceTicks, type ChartBar } from './history';

	let { bars, ariaLabel }: { bars: ChartBar[]; ariaLabel: string } = $props();

	// One SVG user unit is one CSS pixel: the viewBox width follows the element's own
	// width instead of being fixed, so the axis text keeps its 12px size at every
	// container width rather than shrinking with the chart. Nothing has been laid out
	// yet when the server renders — and the first client render matches it — so the
	// fallback is what SSR and Storybook draw before the measurement lands.
	const FALLBACK_WIDTH = 1000;
	const HEIGHT = 220;
	const PAD = { top: 8, right: 8, bottom: 22, left: 56 };
	const plotHeight = HEIGHT - PAD.top - PAD.bottom;

	let measuredWidth = $state(0);
	const width = $derived(measuredWidth || FALLBACK_WIDTH);
	const plotWidth = $derived(width - PAD.left - PAD.right);

	const ticks = $derived(niceTicks(Math.max(0, ...bars.map((b) => b.value))));
	const ceiling = $derived(ticks[ticks.length - 1]);

	const slot = $derived(plotWidth / Math.max(1, bars.length));
	const barWidth = $derived(Math.max(1, slot * 0.8));

	const y = (value: number) => PAD.top + plotHeight - (value / ceiling) * plotHeight;
	const x = (index: number) => PAD.left + index * slot + (slot - barWidth) / 2;
</script>

<div bind:clientWidth={measuredWidth} class="w-full">
	<svg
		viewBox="0 0 {width} {HEIGHT}"
		height={HEIGHT}
		class="text-otodb-content-primary block w-full"
		role="img"
		aria-label={ariaLabel}
	>
		{#each ticks as tick (tick)}
			<line
				x1={PAD.left}
				x2={width - PAD.right}
				y1={y(tick)}
				y2={y(tick)}
				stroke="currentColor"
				stroke-width="1"
				opacity="0.25"
			/>
			<text
				x={PAD.left - 8}
				y={y(tick) + 4}
				text-anchor="end"
				font-size="12"
				fill="currentColor"
				opacity="0.7">{tick}</text
			>
		{/each}

		{#each bars as bar, i (i)}
			<rect
				x={x(i)}
				y={y(bar.value)}
				width={barWidth}
				height={PAD.top + plotHeight - y(bar.value)}
				class="fill-otodb-highlight-primary"
			>
				<title>{bar.title}</title>
			</rect>
			{#if bar.label}
				<text
					x={x(i) + barWidth / 2}
					y={HEIGHT - 6}
					text-anchor="middle"
					font-size="12"
					fill="currentColor"
					opacity="0.7">{bar.label}</text
				>
			{/if}
		{/each}
	</svg>
</div>
