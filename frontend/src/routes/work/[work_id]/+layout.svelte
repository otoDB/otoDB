<script lang="ts">
	import { m } from '$lib/paraglide/messages';
	let { data, children } = $props();
</script>

<svelte:head>
	<title
		>{m.mild_loud_shad_enchant({ type: m.grand_merry_fly_succeed(), name: data.title })}</title
	>
</svelte:head>

{@render children()}
