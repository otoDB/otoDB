<script lang="ts">
	import { m } from '$lib/paraglide/messages';
	import TimeAgo from '$lib/TimeAgo.svelte';

	interface Props {
		date: string | Date;
		user: null | { username: string };
	}

	const { date, user }: Props = $props();
</script>

<span>
	{#if user}
		<a href="/profile/{user.username}">
			{m.these_free_toucan_promise({ username: user.username })}
		</a>
	{:else}
		{m.misty_ideal_bumblebee_jest()}
	{/if}
	<TimeAgo {date} />
</span>
