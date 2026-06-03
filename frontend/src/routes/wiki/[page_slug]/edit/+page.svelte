<script lang="ts">
	import Section from '$lib/Section.svelte';
	import WikiEditor from '$lib/WikiEditor.svelte';
	import { dirtyEnhance } from '$lib/dirty';
	import { m } from '$lib/paraglide/messages';

	let { data } = $props();

	const title = $derived(data.wiki_page.find((p) => p.title)?.title ?? data.page_slug);

	const menuLinks = $derived([
		{ pathname: `wiki/${data.page_slug}`, title: m.curly_zesty_pelican_aim() },
		{ pathname: `wiki/${data.page_slug}/edit`, title: m.minor_crisp_cobra_list() }
	]);
</script>

<Section {title} type="Wiki edit" {menuLinks}>
	<form method="POST" use:dirtyEnhance>
		<WikiEditor wiki_page={data.wiki_page} withTitle />
		<input type="submit" value="Save" />
	</form>
</Section>
