<script lang="ts">
	import type { ComponentProps } from 'svelte';
	import client, { getTagDisplaySlug } from './api';
	import TagSuggestionResults from './TagSuggestionResults.svelte';
	import { clickOutside, debounce } from './ui';

	interface Props {
		value: string;
		type: 'work' | 'song';
		resolve_aliases?: boolean;
	}
	let { value = $bindable(''), type, ...props }: Props = $props();

	const endpoint = $derived.by(() => {
		switch (type) {
			case 'work':
				return '/api/tag/search';
			case 'song':
				return '/api/tag/song_tag_search';
		}
	});

	let suggestions: ComponentProps<typeof TagSuggestionResults>['suggestions'] = $state([]);

	const search = async () => {
		if (value === '') {
			suggestions = [];
			return;
		}
		const { data } = await client.GET(
			(() => {
				switch (type) {
					case 'work':
					case 'song':
						// return '/api/tag/search' as const;
						return '/api/tag/song_tag_search';
				}
			})(),
			{
				params: {
					query: {
						query: value,
						limit: 10,
						resolve_aliases: props.resolve_aliases ?? true
					}
				}
			}
		);
		console.dir(data);
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
			onOutclick={() => {
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
