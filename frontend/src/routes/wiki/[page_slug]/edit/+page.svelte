<script lang="ts">
	import Section from '$lib/Section.svelte';
	import WikiEditor from '$lib/WikiEditor.svelte';
	import { dirtyEnhance } from '$lib/dirty';
	import { m } from '$lib/paraglide/messages.js';

	let { data } = $props();
</script>

<Section title={data.head.title} type={m.curly_zesty_pelican_aim()} menuLinks={data.menuLinks}>
	<form method="POST" use:dirtyEnhance>
		<WikiEditor wiki_page={data.wiki_page} withTitle />
		<input type="submit" value="Save" />
	</form>
</Section>
