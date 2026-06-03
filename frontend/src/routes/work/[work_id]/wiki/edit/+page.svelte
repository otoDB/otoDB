<script lang="ts">
	import Section from '$lib/Section.svelte';
	import WikiEditor from '$lib/WikiEditor.svelte';
	import { dirtyEnhance } from '$lib/dirty';
	import { m } from '$lib/paraglide/messages';

	let { data } = $props();
</script>

<Section title={data.title} type={m.grand_merry_fly_succeed()} menuLinks={data.links}>
	<form method="POST" use:dirtyEnhance>
		<WikiEditor wiki_page={data.wiki_page} />
		<input type="submit" value="Save" />
	</form>
</Section>
