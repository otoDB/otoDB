<script lang="ts">
	import { m } from '$lib/paraglide/messages';
	let { data, children } = $props();
</script>

<svelte:head>
	<title
		>{m.mild_loud_shad_enchant({
			type: m.stale_loose_squid_cut(),
			name: data.post.title
		})}</title
	>
	<meta property="og:title" content={data.post.title} />
	<meta name="twitter:title" content={data.post.title} />

	<link rel="canonical" href={`https://otodb.net/post/${data.post_id}`} />
	<meta property="og:url" content={`https://otodb.net/post/${data.post_id}`} />
</svelte:head>

{@render children()}
