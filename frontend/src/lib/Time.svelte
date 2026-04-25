<script lang="ts">
	import { m } from '$lib/paraglide/messages';
	import { getLocale } from '$lib/paraglide/runtime';

	const MINUTE = 60;
	const HOUR = MINUTE * 60;
	const DAY = HOUR * 24;
	const WEEK = DAY * 7;
	const MONTH = DAY * 30;
	const YEAR = DAY * 365;

	interface Props {
		date: string | Date;
		format: 'relative' | 'absolute';
	}

	const { date, format }: Props = $props();

	const parsedDate = $derived(date instanceof Date ? date : new Date(date));

	const relative = $derived.by(() => {
		const diff = (parsedDate.getTime() - Date.now()) / 1000;
		const elapsed = Math.abs(diff);

		if (elapsed <= 1) return m.busy_hour_bee_gasp();

		const rtf = new Intl.RelativeTimeFormat(getLocale(), { numeric: 'always' });

		// prettier-ignore
		const [divisor, unit]: [number, Intl.RelativeTimeFormatUnit] =
			elapsed > YEAR   * 2 ? [YEAR,   'year']   :
			elapsed > MONTH  * 2 ? [MONTH,  'month']  :
			elapsed > WEEK   * 2 ? [WEEK,   'week']   :
			elapsed > DAY    * 1 ? [DAY,    'day']    :
			elapsed > HOUR   * 1 ? [HOUR,   'hour']   :
			elapsed > MINUTE * 2 ? [MINUTE, 'minute'] :
			                       [1,      'second'];

		return rtf.format(Math.trunc(diff / divisor), unit);
	});

	const short = $derived(
		new Intl.DateTimeFormat(getLocale(), { dateStyle: 'short', timeStyle: 'short' }).format(
			parsedDate
		)
	);

	const full = $derived(
		new Intl.DateTimeFormat(getLocale(), { dateStyle: 'full', timeStyle: 'long' }).format(
			parsedDate
		)
	);
</script>

{#if format === 'relative'}
	<time title={full} class="whitespace-nowrap">{relative}</time>
{:else}
	<time title={full} class="whitespace-nowrap">{short}</time>
{/if}
