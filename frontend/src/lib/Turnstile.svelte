<script lang="ts">
	import { page } from '$app/state';
	import { env } from '$env/dynamic/public';
	import { turnstile } from '@battlefieldduck/turnstile-svelte';

	type Props = {
		action: string;
	};

	const { action }: Props = $props();

	const siteKey = env.PUBLIC_TURNSTILE_SITE_KEY;
</script>

{#if siteKey}
	{#key page.form}
		<div {@attach turnstile({ sitekey: siteKey, action })}></div>
	{/key}
{/if}
