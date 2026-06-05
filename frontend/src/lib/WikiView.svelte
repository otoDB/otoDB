<script lang="ts">
	import LangSwitch from '$lib/LangSwitch.svelte';
	import { languages, resolveLanguageKeyById } from '$lib/enums/language';
	import { renderMarkdown } from '$lib/markdown';
	import { m } from '$lib/paraglide/messages';
	import { getLocale } from '$lib/paraglide/runtime';
	import { LanguageTypes, type components } from '$lib/schema';

	let { wiki_page }: { wiki_page: components['schemas']['WikiPageMDSchema'][] } = $props();

	const localizedPages = $derived(wiki_page.filter((p) => p.lang !== LanguageTypes.N_A));
	const fallbackPage = $derived(wiki_page.find((p) => p.lang === LanguageTypes.N_A) ?? null);

	const initialView = $derived.by(() => {
		const userLang = languages[getLocale()].id;
		const exact = localizedPages.find((p) => p.lang === userLang);
		if (exact) return resolveLanguageKeyById(exact.lang);
		if (localizedPages[0]) return resolveLanguageKeyById(localizedPages[0].lang);
		return null;
	});

	let wikiView = $state.raw<keyof typeof languages | null>(initialView);

	$effect(() => {
		wikiView = initialView;
	});

	const currentPage = $derived.by(() => {
		const view = wikiView;
		if (!view) return fallbackPage;
		return localizedPages.find((p) => p.lang === languages[view].id) ?? fallbackPage;
	});

	const currentLangKey: keyof typeof languages | undefined = $derived(
		currentPage ? resolveLanguageKeyById(currentPage.lang) : undefined
	);
</script>

{#if localizedPages.length > 1 && wikiView}
	<div class="float-right clear-left my-2">
		<LangSwitch
			availableLanguages={localizedPages.map((p) => resolveLanguageKeyById(p.lang))}
			bind:value={wikiView as keyof typeof languages}
		/>
	</div>
{:else if currentLangKey}
	<div class="float-right clear-left my-2">
		<span class="lang-label">{languages[currentLangKey].name}</span>
	</div>
{/if}
{#if currentPage && currentPage.page}
	<div
		class="prose prose-neutral prose-sm dark:prose-invert prose-p:max-w-4xl prose-ul:max-w-4xl prose-ol:max-w-4xl prose-blockquote:max-w-4xl prose-headings:max-w-4xl max-w-none"
	>
		<!-- eslint-disable-next-line svelte/no-at-html-tags -->
		{@html renderMarkdown(currentPage.page)}
	</div>
{:else}
	<p>{m.tame_dirty_goldfish_flow()}</p>
{/if}

<style>
	.lang-label {
		padding: 0.2rem 0.5rem;
		display: inline-block;
		border: 1px solid var(--otodb-color-content-primary);
		background-color: var(--otodb-color-bg-faint);
	}
</style>
