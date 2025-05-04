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
</svelte:head>

{@render children()}
