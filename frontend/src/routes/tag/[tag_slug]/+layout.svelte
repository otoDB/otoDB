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
</svelte:head>

{@render children()}
