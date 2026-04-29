<script lang="ts">
	import Section from '$lib/Section.svelte';
	import { languages } from '$lib/enums/language.js';

	let { data } = $props();

	const formatSlug = (slug: string) =>
		slug
			.split('_')
			.map((w) => w.charAt(0).toUpperCase() + w.slice(1))
			.join(' ');
</script>

<Section title="Docs">
	<ul class="flex flex-col gap-2">
		{#each data.entries as { slug, langs } (slug)}
			<li class="flex items-baseline gap-3">
				<a href="/docs/{slug}">{formatSlug(slug)}</a>
				<span class="text-otodb-content-fainter text-xs">
					{langs.map((l) => languages[l].name).join(' / ')}
				</span>
			</li>
		{/each}
	</ul>
</Section>
