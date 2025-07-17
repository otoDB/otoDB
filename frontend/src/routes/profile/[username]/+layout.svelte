<script lang="ts">
	import { m } from '$lib/paraglide/messages';
	let { data, children } = $props();
</script>

<svelte:head>
	<title
		>{m.mild_loud_shad_enchant({
			type: m.fuzzy_crazy_cobra_lead(),
			name: data.profile.username
		})}</title
	>
    <meta property="og:title" content={data.profile.username} />
	<meta name="twitter:title" content={data.profile.username} />

	<link rel="canonical" href={`https://otodb.net/profile/${data.profile.username}`} />
	<meta property="og:url" content={`https://otodb.net/profile/${data.profile.username}`} />
</svelte:head>

{@render children()}
