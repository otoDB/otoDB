<script lang="ts">
	import Section from '$lib/Section.svelte';

	let { data, children } = $props();
</script>

<Section title="Moderation" menuLinks={data.links}>
	{@render children()}
</Section>
