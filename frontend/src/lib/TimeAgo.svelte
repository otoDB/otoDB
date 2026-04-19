<script lang="ts">
	import { m } from '$lib/paraglide/messages';
	import { getLocale } from '$lib/paraglide/runtime';

	interface Props {
		date: string | Date;
	}

	const { date }: Props = $props();

	const parsedDate = $derived(date instanceof Date ? date : new Date(date));
	const text = $derived.by(() => {
		const MINUTE = 60;
		const HOUR = MINUTE * 60;
		const DAY = HOUR * 24;
		const WEEK = DAY * 7;
		const MONTH = DAY * 30;
		const YEAR = DAY * 365;

		const d = date instanceof Date ? date : new Date(date);
		const diff = (d.getTime() - Date.now()) / 1000;
		const elapsed = Math.abs(diff);

		if (elapsed <= 1) return m.busy_hour_bee_gasp();

		const rtf = new Intl.RelativeTimeFormat(getLocale(), { numeric: 'always' });

		// prettier-ignore
		const [divisor, unit]: [number, Intl.RelativeTimeFormatUnit] =
			elapsed > YEAR   * 2  ? [YEAR,   'year']   :
			elapsed > MONTH  * 2  ? [MONTH,  'month']  :
			elapsed > WEEK   * 2  ? [WEEK,   'week']   :
			elapsed > DAY    * 1  ? [DAY,    'day']    :
			elapsed > HOUR   * 1  ? [HOUR,   'hour']   :
			elapsed > MINUTE * 10 ? [MINUTE, 'minute'] :
								    [1,      'second']

		return rtf.format(Math.trunc(diff / divisor), unit);
	});
</script>

<time title={parsedDate.toLocaleString()} class="whitespace-nowrap">{text}</time>
