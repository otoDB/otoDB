<script lang="ts">
	import { env } from '$env/dynamic/public';
	import { turnstile } from '@battlefieldduck/turnstile-svelte';

	type Props = {
		action: string;
	};

	const { action }: Props = $props();

	const siteKey = env.PUBLIC_TURNSTILE_SITE_KEY;
</script>

{#if siteKey}
	<div {@attach turnstile({ sitekey: siteKey, action })}></div>
{/if}
