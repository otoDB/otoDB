<script lang="ts">
	import { m } from '$lib/paraglide/messages';
	import { getLocale } from '$lib/paraglide/runtime';
	import { ParaglideMessage } from '@inlang/paraglide-js-svelte';

	interface Props {
		date: string | Date;
		user?: { username: string } | null;
		action?: string;
	}

	const { date, user, action }: Props = $props();

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

{#snippet Time()}
	<time title={parsedDate.toLocaleString()} class="whitespace-nowrap">{text}</time>
{/snippet}

{#if user && action}
	<ParaglideMessage
		message={m.free_tiny_badger_breathe}
		inputs={{ user: user.username, verb: action }}
	>
		{#snippet link({ options })}
			<a href="/profile/{options.name}">{options.name}</a>
		{/snippet}
		{#snippet time()}
			{@render Time()}
		{/snippet}
	</ParaglideMessage>
{:else if action}
	<ParaglideMessage message={m.lazy_clean_kangaroo_chop} inputs={{ verb: action }}>
		{#snippet time()}
			{@render Time()}
		{/snippet}
	</ParaglideMessage>
{:else}
	{@render Time()}
{/if}
