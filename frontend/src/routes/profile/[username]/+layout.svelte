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
</svelte:head>

{@render children()}
