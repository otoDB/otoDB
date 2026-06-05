<script lang="ts">
	import Section from '$lib/Section.svelte';
	import WikiView from '$lib/WikiView.svelte';

	let { data } = $props();
</script>

<Section title={data.title} type="Wiki" menuLinks={data.menuLinks}>
	<WikiView wiki_page={data.wiki_page} />
</Section>
