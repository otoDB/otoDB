<script lang="ts">
	import client from '$lib/api';
	import { m } from '$lib/paraglide/messages';
	import TagSuggestionResults from '$lib/TagSuggestionResults.svelte';
	import { clickOutside, debounce } from '$lib/ui';
	import { getTagDisplaySlug } from '$lib/ui.js';

	interface Props {
		value: string[];
		class?: string;
		type: 'work' | 'song';
		name?: string;
	}
	let { value = $bindable([]), type, ...props }: Props = $props();

	const endpoint = type === 'work' ? '/api/tag/search' : '/api/tag/song_tag_search';

	let textarea: HTMLTextAreaElement;
	let suggestions = $state<any[]>([]);
	let lastQuery = $state('');

	const getWordAtPos = (str: string, pos: number) => {
		let start = [...str.slice(0, pos)].reverse().join('').search(/\s/g);
		let end = str.slice(pos).search(/\s/g);
		start = start === -1 ? 0 : pos - start;
		end = end === -1 ? str.length : pos + end;
		return { word: str.slice(start, end), start, end };
	};

	const replaceWordAtPos = (str: string, pos: number, replacement: string) => {
		const { start, end } = getWordAtPos(str, pos);
		return str.slice(0, start) + replacement + str.slice(end);
	};

	const splitToken = (word: string): { prefix: string; query: string } | null => {
		let i = 0;
		while (i < word.length && '-^('.includes(word[i])) i++;
		const prefix = word.slice(0, i);
		const query = word.slice(i);
		if (!query) return null;
		if (/[:[\]|)]/.test(query)) return null;
		return { prefix, query };
	};

	const search = debounce(async () => {
		const word = getWordAtPos(textarea.value, textarea.selectionStart).word;
		const parsed = splitToken(word);
		if (!parsed) {
			suggestions = [];
			lastQuery = '';
			return;
		}
		if (parsed.query === lastQuery) return;
		lastQuery = parsed.query;
		const { data } = await client.GET(endpoint, {
			params: { query: { query: parsed.query, limit: 10, resolve_aliases: false } }
		});
		if (!data) return;
		suggestions = data.items;
	});

	const updateValue = () => {
		value = [
			...new Set(
				textarea.value
					.split(' ')
					.map((s) => s.trim())
					.filter((str) => str.length !== 0)
			)
		];
	};

	const selectTag = (tag: any) => {
		const word = getWordAtPos(textarea.value, textarea.selectionStart).word;
		const parsed = splitToken(word);
		const prefix = parsed?.prefix ?? '';
		textarea.value = replaceWordAtPos(
			textarea.value,
			textarea.selectionStart,
			prefix + getTagDisplaySlug(tag.aliased_to || tag) + ' '
		);
		suggestions = [];
		updateValue();
		textarea.focus();
	};

	$effect(() => {
		if (!textarea) return;
		const current = new Set(
			textarea.value
				.split(' ')
				.map((s) => s.trim())
				.filter(Boolean)
		);
		const target = new Set(value);
		if (current.size !== target.size || ![...target].every((v) => current.has(v))) {
			textarea.value = value.join(' ');
		}
	});
</script>

<span role="none">
	<textarea
		onkeyup={() => {
			updateValue();
			search();
		}}
		placeholder={m.petty_fuzzy_fox_ask()}
		onclick={search}
		bind:this={textarea}
		{...props}
	></textarea>
	{#if suggestions.length}
		<ul
			class="absolute z-1 list-none"
			use:clickOutside
			onoutclick={() => {
				suggestions = [];
			}}
		>
			<TagSuggestionResults
				{suggestions}
				onselect={selectTag}
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
