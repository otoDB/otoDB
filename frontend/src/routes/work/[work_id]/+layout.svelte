<script lang="ts">
	import { m } from '$lib/paraglide/messages';
	import { getDisplayText } from '$lib/api';
	let { data, children } = $props();
</script>

<svelte:head>
	<title
		>{m.mild_loud_shad_enchant({
			type: m.grand_merry_fly_succeed(),
			name: getDisplayText(data.title)
		})}</title
	>
	<meta name="twitter:card" content="summary_large_image" />

	<meta property="og:title" content={getDisplayText(data.title)} />
	<meta name="twitter:title" content={getDisplayText(data.title)} />

	<link rel="canonical" href={`https://otodb.net/work/${data.id}`} />
	<meta property="og:url" content={`https://otodb.net/work/${data.id}`} />

	{#if data.rating <= 1}
		<meta property="og:image" content={data.thumbnail} />
		<meta name="twitter:image" content={data.thumbnail} />
	{/if}
</svelte:head>

{@render children()}
