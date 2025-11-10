<script lang="ts">
	import client, { getTagDisplaySlug } from './api';
	import TagSuggestionResults from './TagSuggestionResults.svelte';
	import { clickOutside, debounce } from './ui';

	interface Props {
		value: string;
		type: 'work' | 'song';
		resolve_aliases?: boolean;
	}
	let { value = $bindable(''), type, ...props }: Props = $props();

	const endpoint = type === 'work' ? '/api/tag/search' : '/api/tag/song_tag_search';

	let suggestions = $state([]);

	const search = async () => {
		if (value === '') {
			suggestions = [];
			return;
		}
		const { data } = await client.GET(endpoint, {
			params: {
				query: { query: value, limit: 10, resolve_aliases: props.resolve_aliases ?? true }
			}
		});
		if (!data) return;
		suggestions = data.items;
	};
</script>

<span role="none">
	<input type="text" oninput={debounce(search, type === 'work' ? 0 : 300)} bind:value {...props} />
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
