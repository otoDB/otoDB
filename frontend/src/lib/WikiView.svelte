<script lang="ts">
	import LangSwitch from '$lib/LangSwitch.svelte';
	import WorkTag from '$lib/WorkTag.svelte';
	import client from '$lib/api.js';
	import { languages, resolveLanguageKeyById } from '$lib/enums/language';
	import { hydrate, renderMarkdown } from '$lib/markdown';
	import { m } from '$lib/paraglide/messages';
	import { getLocale } from '$lib/paraglide/runtime';
	import { LanguageTypes, type components } from '$lib/schema';
	import { mount, unmount } from 'svelte';

	let { wiki_page }: { wiki_page: components['schemas']['WikiPageMDSchema'][] } = $props();

	const localizedPages = $derived(wiki_page.filter((p) => p.lang !== LanguageTypes.N_A));
	const fallbackPage = $derived(wiki_page.find((p) => p.lang === LanguageTypes.N_A) ?? null);

	let wikiView = $derived.by<keyof typeof languages | null>(() => {
		const userLang = languages[getLocale()].id;
		const exact = localizedPages.find((p) => p.lang === userLang);
		if (exact) return resolveLanguageKeyById(exact.lang);
		if (localizedPages[0]) return resolveLanguageKeyById(localizedPages[0].lang);
		return null;
	});

	const currentPage = $derived.by(() => {
		const view = wikiView;
		if (!view) return fallbackPage;
		return localizedPages.find((p) => p.lang === languages[view].id) ?? fallbackPage;
	});

	let contentEl = $state<HTMLElement>();

	$effect(() => {
		if (currentPage && contentEl) {
			const tags = Array.from(contentEl.querySelectorAll('otodb-worktag'))
				.filter((e) => e.hasAttribute('slug'))
				.map((el) =>
					client
						.GET('/api/tag/tag', {
							fetch,
							params: {
								query: {
									tag_slug: el.getAttribute('slug')!
								}
							}
						})
						.then((r) => mount(WorkTag, { target: el, props: { tag: r.data! } }))
				);
			return () => {
				tags.forEach((p) => p.then(unmount));
			};
		}
	});
</script>

{#if localizedPages.length > 0 && wikiView}
	<div class="float-right clear-left my-2">
		<LangSwitch
			availableLanguages={localizedPages.map((p) => resolveLanguageKeyById(p.lang))}
			bind:value={wikiView as keyof typeof languages}
		/>
	</div>
{/if}
{#if currentPage && currentPage.page}
	<div
		bind:this={contentEl}
		class="prose prose-neutral prose-sm dark:prose-invert prose-p:max-w-4xl prose-ul:max-w-4xl prose-ol:max-w-4xl prose-blockquote:max-w-4xl prose-headings:max-w-4xl max-w-none"
		{@attach (node) => {
			void currentPage;
			return hydrate(node);
		}}
	>
		<!-- eslint-disable-next-line svelte/no-at-html-tags -->
		{@html renderMarkdown(currentPage.page)}
	</div>
{:else}
	<p>{m.tame_dirty_goldfish_flow()}</p>
{/if}
