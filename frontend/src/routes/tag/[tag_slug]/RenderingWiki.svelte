<script lang="ts">
	import LangSwitch from '$lib/LangSwitch.svelte';
	import { renderMarkdown } from '$lib/markdown';
	import { languages, resolveLanguageKeyById } from '$lib/enums/Languages.js';

	let {
		wiki,
		defaultLang
	}: {
		wiki: { lang: number; page: string }[];
		defaultLang: keyof typeof languages;
	} = $props();

	let availableLangs = $derived(wiki.map((v) => resolveLanguageKeyById(v.lang)));
	let selecting: keyof typeof languages = $state(defaultLang);

	let selectingWiki = $derived(
		wiki.find(({ lang }) => resolveLanguageKeyById(lang) === selecting)
	);
</script>

<div class="float-right clear-left my-2">
	<LangSwitch availableLanguages={availableLangs} bind:value={selecting} />
</div>

{#if selectingWiki}
	<div
		class="prose prose-neutral prose-sm dark:prose-invert prose-p:max-w-4xl prose-ul:max-w-4xl prose-ol:max-w-4xl prose-blockquote:max-w-4xl prose-headings:max-w-4xl max-w-none"
	>
		<!-- eslint-disable-next-line svelte/no-at-html-tags -->
		{@html renderMarkdown(selectingWiki.page)}
	</div>
{/if}

<!-- TODO: if no wiki page (defaultLang might be wrong), show something else? -->
