<script lang="ts">
	import Section from '$lib/Section.svelte';
	import WikiEditor from '$lib/WikiEditor.svelte';
	import { dirtyEnhance } from '$lib/dirty';

	let { data } = $props();
</script>

<Section title={data.page_slug} type="Wiki edit">
	<form method="POST" use:dirtyEnhance>
		<WikiEditor wiki_page={data.wiki_page} withTitle />
		<input type="submit" value="Save" />
	</form>
</Section>
