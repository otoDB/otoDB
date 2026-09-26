<script lang="ts">
	import { m } from '$lib/paraglide/messages.js';
	import Section from '$lib/Section.svelte';
	import WikiView from '$lib/WikiView.svelte';

	let { data } = $props();
</script>

<Section title={data.head.title} type={m.curly_zesty_pelican_aim()} menuLinks={data.menuLinks}>
	<WikiView wiki_page={data.wiki_page} />
</Section>
