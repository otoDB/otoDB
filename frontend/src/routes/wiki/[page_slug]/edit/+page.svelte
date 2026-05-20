<script lang="ts">
	import Section from '$lib/Section.svelte';
	import { dirtyEnhance } from '$lib/dirty';
	import { languages } from '$lib/enums/language';
	import { renderMarkdown } from '$lib/markdown';
	import { m } from '$lib/paraglide/messages';
	import { getLocale, locales } from '$lib/paraglide/runtime';

	let { data } = $props();

	let title = $state(data.wiki_page.find((p) => p.title)?.title ?? '');
	let wikiView = $state(getLocale());
	let mds = $state(
		Object.fromEntries(
			locales.map((lang) => [
				lang,
				data.wiki_page.find((p) => p.lang === languages[lang].id)?.page ?? ''
			])
		)
	);
	let edited_md = $state(Object.fromEntries(locales.map((lang) => [lang, false])));

	let previewHtml = $derived(renderMarkdown(mds[wikiView] ?? ''));
</script>

<Section title={data.page_slug} type="Wiki edit">
	<form method="POST" use:dirtyEnhance>
		<table class="mb-3">
			<tbody>
				<tr>
					<th><label for="title">Title</label></th>
					<td><input id="title" type="text" name="title" bind:value={title} required /></td>
				</tr>
			</tbody>
		</table>

		<div class="my-2">
			{#each locales as locale, i (i)}
				<label class="wiki-lang-tab">
					<input type="radio" bind:group={wikiView} value={locale} />
					{languages[locale]
						.name}{#if edited_md[locale]}{m.great_clean_beaver_amuse()}{m.awful_house_liger_expand({
							content: '*'
						})}{/if}
				</label>
			{/each}
		</div>

		<input
			type="hidden"
			name="wiki_pages"
			value={JSON.stringify(
				locales
					.filter((lang) => edited_md[lang])
					.map((lang) => ({ lang: languages[lang].id, md: mds[lang] }))
			)}
		/>

		<div class="grid grid-cols-2 gap-3">
			<textarea
				onchange={() => {
					edited_md[wikiView] = true;
				}}
				bind:value={mds[wikiView]}
			></textarea>
			<div class="prose prose-neutral prose-sm dark:prose-invert">
				<!-- eslint-disable-next-line svelte/no-at-html-tags -->
				{@html previewHtml}
			</div>
		</div>
		<input type="submit" value="Save" />
	</form>
</Section>

<style>
	label.wiki-lang-tab {
		padding: 0.2rem 0.5rem;
		display: inline-block;
		background-color: var(--otodb-color-bg-primary);
		border: 1px solid var(--otodb-color-content-primary);
		&:hover {
			background-color: var(--otodb-color-bg-fainter);
		}
		&:active {
			background-color: var(--otodb-color-bg-faint);
		}
		& > input {
			display: none;
		}
		&:has(> input:checked) {
			background-color: var(--otodb-color-content-primary);
			border: 1px solid var(--otodb-color-bg-primary);
			color: var(--otodb-color-bg-primary);
		}
	}
</style>
