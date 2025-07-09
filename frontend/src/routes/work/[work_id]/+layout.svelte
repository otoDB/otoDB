<script lang="ts">
	import { m } from '$lib/paraglide/messages';
	let { data, children } = $props();
</script>

<svelte:head>
	<title
		>{m.mild_loud_shad_enchant({ type: m.grand_merry_fly_succeed(), name: data.title })}</title
	>
	<meta name="description" content={data.description} />
	<meta property="og:title" content={data.title} />
	<meta property="og:description" content={data.description} />
	<meta property="og:image" content={data.thumbnail} />
	<meta property="og:type" content="website" />
	<meta property="og:url" content={`https://otodb.net/work/${data.id}`} />
	<meta name="twitter:card" content="summary_large_image" />
	<meta name="twitter:title" content={data.title} />
	<meta name="twitter:description" content={data.description} />
	<meta name="twitter:image" content={data.thumbnail} />
	<meta name="theme-color" content="#ffffff" />
	<link rel="canonical" href={`https://otodb.net/work/${data.id}`} />
</svelte:head>

{@render children()}
