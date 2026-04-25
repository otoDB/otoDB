<script lang="ts">
	import { formatAbsolute, formatRelative } from '$lib/time';
	import { getLocale } from '$lib/paraglide/runtime';

	interface Props {
		date: string | Date;
	}

	const { date }: Props = $props();

	const parsedDate = $derived(date instanceof Date ? date : new Date(date));
	const text = $derived(formatAbsolute(parsedDate, getLocale()));
	const tooltip = $derived(formatRelative(parsedDate, getLocale()));
</script>

<time title={tooltip} class="whitespace-nowrap">{text}</time>
