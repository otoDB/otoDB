<script lang="ts">
	import { m } from '$lib/paraglide/messages';
	import { getLocale } from '$lib/paraglide/runtime';
	import TimeAgo from '$lib/TimeAgo.svelte';

	interface Props {
		date: string | Date;
		user: null | { username: string };
	}

	const { date, user }: Props = $props();
</script>

<span>
	{m.plain_plain_manatee_treasure()}
	:
	<TimeAgo {date}></TimeAgo>
	{#if user}
		<a href="/profile/{user.username}">{user.username}</a>
	{/if}
</span>
