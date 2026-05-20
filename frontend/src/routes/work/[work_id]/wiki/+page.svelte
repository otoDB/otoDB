<script lang="ts">
	import LangSwitch from '$lib/LangSwitch.svelte';
	import Section from '$lib/Section.svelte';
	import { languages, resolveLanguageKeyById } from '$lib/enums/language';
	import { renderMarkdown } from '$lib/markdown';
	import { m } from '$lib/paraglide/messages';
	import { getLocale } from '$lib/paraglide/runtime';
	import { LanguageTypes, Levels } from '$lib/schema';

	let { data } = $props();

	const canEdit = $derived((data.user?.level ?? 0) > Levels.Restricted);

	const localizedPages = $derived(data.wiki_page.filter((p) => p.lang !== LanguageTypes.N_A));
	const fallbackPage = $derived(data.wiki_page.find((p) => p.lang === LanguageTypes.N_A) ?? null);

	const initialView = $derived.by(() => {
		const userLang = languages[getLocale()].id;
		const exact = localizedPages.find((p) => p.lang === userLang);
		if (exact) return resolveLanguageKeyById(exact.lang);
		if (localizedPages[0]) return resolveLanguageKeyById(localizedPages[0].lang);
		return null;
	});

	let wikiView = $state.raw<keyof typeof languages | null>(initialView);

	const currentPage = $derived.by(() => {
		const view = wikiView;
		if (!view) return fallbackPage;
		return localizedPages.find((p) => p.lang === languages[view].id) ?? fallbackPage;
	});
</script>

<Section title={data.title} type={m.grand_merry_fly_succeed()} menuLinks={data.links}>
	{#if localizedPages.length > 1 && wikiView}
		<div class="float-right clear-left my-2">
			<LangSwitch
				availableLanguages={localizedPages.map((p) => resolveLanguageKeyById(p.lang))}
				bind:value={wikiView as keyof typeof languages}
			/>
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
	{#if canEdit}
		<div class="mt-3">
			<a href="/work/{data.work_id}/wiki/edit">{m.male_known_pony_rise()}</a>
		</div>
	{/if}
</Section>
