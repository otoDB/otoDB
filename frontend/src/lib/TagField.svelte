<script lang="ts">
	import client from '$lib/api';
	import TagSuggestionResults from '$lib/TagSuggestionResults.svelte';
	import { clickOutside, debounce } from '$lib/ui';
	import { getTagDisplaySlug } from '$lib/ui.js';
	import type { components } from './schema';

	interface Props {
		value: string;
		type: 'work' | 'song';
		name?: string;
	}
	let { value = $bindable(''), type, ...props }: Props = $props();

	let suggestions:
		| components['schemas']['TagWorkSearchResultSchema'][]
		| components['schemas']['TagSongSearchResultSchema'][] = $state([]);

	let controller: AbortController | undefined;

	const search = async () => {
		controller?.abort();
		if (value === '') {
			suggestions = [];
			return;
		}
		controller = new AbortController();
		const { signal } = controller;
		try {
			const { data } =
				type === 'work'
					? await client.GET('/api/tag/search', {
							params: {
								query: {
									query: value,
									limit: 10,
									order: 'count',
									autocomplete: true
								}
							},
							signal
						})
					: await client.GET('/api/tag/song_tag_search', {
							params: { query: { query: value, limit: 10, autocomplete: true } },
							signal
						});
			if (signal.aborted || !data) return;
			suggestions = data.items;
		} catch (e) {
			if (signal.aborted) return;
			throw e;
		}
	};
</script>

<span role="none">
	<input type="text" oninput={debounce(search)} bind:value {...props} />
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
				onselect={(t) => {
					value = getTagDisplaySlug(t.aliased_to || t);
					suggestions = [];
				}}
				onclose={() => (suggestions = [])}
				{type}
			/>
		</ul>
	{/if}
</span>

<style>
	ul {
		background-color: var(--otodb-color-bg-faint);
	}
</style>
