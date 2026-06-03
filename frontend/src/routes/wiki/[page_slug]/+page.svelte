<script lang="ts">
	import Section from '$lib/Section.svelte';
	import WikiView from '$lib/WikiView.svelte';
	import { m } from '$lib/paraglide/messages';
	import { Levels } from '$lib/schema';

	let { data } = $props();

	const title = $derived(data.wiki_page.find((p) => p.title)?.title ?? data.page_slug);

	const canEdit = $derived((data.user?.level ?? 0) >= Levels.Mod);

	const menuLinks = $derived(
		canEdit
			? [
					{ pathname: `wiki/${data.page_slug}`, title: m.curly_zesty_pelican_aim() },
					{ pathname: `wiki/${data.page_slug}/edit`, title: m.minor_crisp_cobra_list() }
				]
			: null
	);
</script>

<Section {title} type="Wiki" {menuLinks}>
	<WikiView wiki_page={data.wiki_page} />
</Section>
