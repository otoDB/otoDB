<script lang="ts">
	import { m } from '$lib/paraglide/messages.js';
	import Section from '$lib/Section.svelte';
	import BarChart from '$lib/stats/BarChart.svelte';
	import { bucketByMonth, type ChartBar } from '$lib/stats/history';

	let { data } = $props();

	const buckets = $derived(bucketByMonth(data.history));

	// Years span a dozen bars each, so labelling every month would be unreadable:
	// only January carries a label, plus the first bucket when the series starts
	// partway through a year.
	const bars = $derived(
		buckets.map(({ month, total }, i): ChartBar => {
			const [year, monthOfYear] = month.split('-');
			return {
				value: total,
				label: i === 0 || monthOfYear === '01' ? year : undefined,
				title: m.sunny_smug_walrus_lift({ total, month })
			};
		})
	);
</script>

<Section title={m.proud_bold_gecko_thrive()}>
	<p class="mb-4">{m.mellow_zesty_stork_bloom()}</p>
	<BarChart {bars} ariaLabel={m.proud_bold_gecko_thrive()} />
</Section>
