<script lang="ts">
	import type { MessageLike } from '@inlang/paraglide-js-svelte';
	import { ParaglideMessage } from '@inlang/paraglide-js-svelte';
	import Time from '$lib/Time.svelte';

	interface Props {
		message: MessageLike<any, any, any>;
		date: Date | string;
	}

	const { message, date: dateValue }: Props = $props();
</script>

<ParaglideMessage {message} inputs={{}}>
	{#snippet date()}
		<Time format="absolute" date={dateValue} />
	{/snippet}
</ParaglideMessage>
