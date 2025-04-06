<script lang="ts">
	import client from './api';
	import { clickOutside, debounce } from './ui';

	interface Props {
		value: string;
		type: 'work' | 'song';
	}
	let { value = $bindable(''), type, ...props }: Props = $props();

	const endpoint = type === 'work' ? '/api/tag/search' : '/api/tag/song_tag_search';

	let suggestions: string[] = $state([]);

	const search = async () => {
		if (value === '') {
			suggestions = [];
			return;
		}
		const { data } = await client.GET(endpoint, {
			params: { query: { query: value, limit: 10 } }
		});
		if (!data) return;
		suggestions = data.items.map((tag) => tag.slug);
	};
</script>

<span role="none">
	<input type="text" oninput={debounce(search)} bind:value {...props} />
	<ul
		class="absolute"
		use:clickOutside
		onOutclick={() => {
			suggestions = [];
		}}
	>
		{#each suggestions as t, i (i)}
			<li>
				<a
					href={null}
					onclick={() => {
						value = t;
						suggestions = [];
					}}>{t}</a
				>
			</li>
		{/each}
	</ul>
</span>

<style>
	ul {
		background-color: var(--otodb-bg-color);
	}
</style>
