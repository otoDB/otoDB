<script lang="ts">
	import { m } from '$lib/paraglide/messages';
	let { data, children } = $props();
</script>

<svelte:head>
	<title
		>{m.mild_loud_shad_enchant({
			type: m.empty_legal_chicken_taste(),
			name: data.display_name
		})}</title
	>
    <meta property="og:title" content={data.display_name} />
	<meta name="twitter:title" content={data.display_name} />

	<link rel="canonical" href={`https://otodb.net/tag/${data.tag.slug}`} />
	<meta property="og:url" content={`https://otodb.net/tag/${data.tag.slug}`} />
</svelte:head>

{@render children()}
