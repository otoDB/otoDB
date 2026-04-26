<script lang="ts">
	import { m } from '$lib/paraglide/messages';
	import Time from '$lib/Time.svelte';
	import { ParaglideMessage } from '@inlang/paraglide-js-svelte';

	interface Props {
		date: string | Date;
		user: null | { username: string };
	}

	const { date, user }: Props = $props();
</script>

<span>
	{#if user}
		<ParaglideMessage message={m.free_tiny_badger_breathe} inputs={{}}>
			{#snippet username()}
				<a href="/profile/{user.username}">{user.username}</a>
			{/snippet}
			{#snippet time()}
				<Time format="relative" {date} />
			{/snippet}
		</ParaglideMessage>
	{:else}
		<ParaglideMessage message={m.light_sunny_kitten_slide} inputs={{}}>
			{#snippet time()}
				<Time format="relative" {date} />
			{/snippet}
		</ParaglideMessage>
	{/if}
</span>
