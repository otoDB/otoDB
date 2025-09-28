<script lang="ts">
	import { m } from '$lib/paraglide/messages';
	let { data, children } = $props();
</script>

<svelte:head>
	<title
		>{m.mild_loud_shad_enchant({
			type: m.stale_loose_squid_cut(),
			name: data.list.name
		})}</title
	>
	<meta property="og:title" content={data.list.name} />
	<meta name="twitter:title" content={data.list.name} />

	<link rel="canonical" href={`https://otodb.net/list/${data.list.id}`} />
	<meta property="og:url" content={`https://otodb.net/list/${data.list.id}`} />
</svelte:head>

{@render children()}
