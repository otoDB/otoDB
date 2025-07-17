<script lang="ts">
	import { m } from '$lib/paraglide/messages';
	let { data, children } = $props();
</script>

<svelte:head>
	<title
		>{m.mild_loud_shad_enchant({
			type: m.dull_plain_angelfish_cuddle(),
			name: data.tag.name
		})}</title
	>
    <meta property="og:title" content={data.tag.name} />
	<meta name="twitter:title" content={data.tag.name} />

	<link rel="canonical" href={`https://otodb.net/tag/song/${data.tag.slug}`} />
	<meta property="og:url" content={`https://otodb.net/tag/song/${data.tag.slug}`} />
</svelte:head>

{@render children()}
