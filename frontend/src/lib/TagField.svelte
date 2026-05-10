<script lang="ts">
	import client from '$lib/api';
	import { m } from '$lib/paraglide/messages';
	import TagSuggestionResults from '$lib/TagSuggestionResults.svelte';
	import { clickOutside, debounce } from '$lib/ui';
	import { getTagDisplaySlug } from '$lib/ui.js';
	import type { ComponentProps } from 'svelte';

	type Props =
		| { value?: string; type: 'work' | 'song'; name?: string; class?: string }
		| { value?: string[]; type: 'work' | 'song'; name?: string; class?: string };

	let { value = $bindable(''), type, ...props }: Props = $props();

	let el: HTMLInputElement | HTMLTextAreaElement = $state() as HTMLInputElement;
	let suggestions: ComponentProps<typeof TagSuggestionResults>['suggestions'] = $state([]);
	let lastQuery = $state('');

	const slug_re = /[\p{L}\p{N}_\-]/v;

	const tagsFromText = (text: string) => [
		...new Set(
			text
				.split(' ')
				.map((s) => s.trim())
				.filter(Boolean)
		)
	];

	const wordAtCursor = () => {
		const str = el.value;
		const pos = el.selectionStart ?? str.length;
		let start = pos;
		let end = pos;
		while (start > 0 && slug_re.test(str[start - 1])) start--;
		while (end < str.length && slug_re.test(str[end])) end++;
		while (start < end && str[start] === '-') start++;
		return { word: str.slice(start, end), start, end };
	};

	const writeBack = () => {
		value = Array.isArray(value) ? tagsFromText(el.value) : el.value;
	};

	const search = debounce(async () => {
		const { word, start } = wordAtCursor();
		const before = el.value[start - 1];
		if (!word || before === ':' || before === '[' || before === ',') {
			suggestions = [];
			lastQuery = '';
			return;
		}
		if (word === lastQuery) return;
		lastQuery = word;
		const { data } =
			type === 'work'
				? await client.GET('/api/tag/search', {
						params: {
							query: { query: word, limit: 10, order: 'count', autocomplete: true }
						}
					})
				: await client.GET('/api/tag/song_tag_search', {
						params: { query: { query: word, limit: 10, autocomplete: true } }
					});
		if (data) suggestions = data.items;
	});

	const onInput = () => {
		writeBack();
		search();
	};

	const onSelect: ComponentProps<typeof TagSuggestionResults>['onselect'] = (tag) => {
		const slug = getTagDisplaySlug(tag.aliased_to || tag);
		if (Array.isArray(value)) {
			const { start, end } = wordAtCursor();
			el.value = el.value.slice(0, start) + slug + ' ' + el.value.slice(end);
		} else {
			el.value = slug;
		}
		suggestions = [];
		writeBack();
		el.focus();
	};

	$effect(() => {
		if (!el) return;
		if (Array.isArray(value)) {
			const cur = new Set(tagsFromText(el.value));
			const tgt = new Set(value);
			if (cur.size !== tgt.size || ![...tgt].every((v) => cur.has(v))) {
				el.value = value.join(' ');
			}
		} else if (el.value !== value) {
			el.value = value;
		}
	});
</script>

<span role="none">
	{#if Array.isArray(value)}
		<textarea
			bind:this={el}
			oninput={onInput}
			onclick={search}
			placeholder={m.petty_fuzzy_fox_ask()}
			{...props}
		></textarea>
	{:else}
		<input type="text" bind:this={el} oninput={onInput} {...props} />
	{/if}
	{#if suggestions.length}
		<ul class="absolute z-1 list-none" use:clickOutside onoutclick={() => (suggestions = [])}>
			<TagSuggestionResults
				{suggestions}
				onselect={onSelect}
				onclose={() => (suggestions = [])}
				{type}
				query={lastQuery}
			/>
		</ul>
	{/if}
</span>

<style>
	ul {
		background-color: var(--otodb-color-bg-primary);
		z-index: 1;
	}
</style>
