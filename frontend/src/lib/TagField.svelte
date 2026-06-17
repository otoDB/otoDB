<script lang="ts">
	import client from '$lib/api';
	import TagSuggestionResults from '$lib/TagSuggestionResults.svelte';
	import { clickOutside, debounce } from '$lib/ui';
	import { getTagDisplaySlug } from '$lib/ui.js';
	import type { ComponentProps } from 'svelte';

	interface Props {
		value: string;
		type: 'work' | 'song';
		name?: string;
	}
	let { value = $bindable(''), type, ...props }: Props = $props();

	let suggestions: ComponentProps<typeof TagSuggestionResults>['suggestions'] = $state([]);

	const search = async () => {
		if (value === '') {
			suggestions = [];
			return;
		}
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
						}
					})
				: await client.GET('/api/tag/song_tag_search', {
						params: { query: { query: value, limit: 10, autocomplete: true } }
					});
		if (!data) return;
		suggestions = data.items;
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
