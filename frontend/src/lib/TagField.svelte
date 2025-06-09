<script lang="ts">
	import client from './api';
	import { clickOutside, debounce } from './ui';

	interface Props {
		value: string;
		type: 'work' | 'song';
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
			params: { query: { query: value, limit: 10 } }
		});
		if (!data) return;
		suggestions = data.items;
	};
</script>

<span role="none">
	<input type="text" oninput={debounce(search)} bind:value {...props} />
	{#if suggestions.length}
		<ul
			class="absolute list-none"
			use:clickOutside
			onOutclick={() => {
				suggestions = [];
			}}
		>
			{#each suggestions as t, i (i)}
				<li class="bg-[var(--otodb-fainter-bg)] px-2 py-1 hover:bg-[var(--otodb-faint-bg)]">
					<a
						class="cursor-pointer"
						href={null}
						onclick={() => {
							value = t.slug;
							suggestions = [];
						}}
						>{t.name}
						{#if t.slug !== t.name}<address class="inline">
								({t.slug}<!-- TODO extend lang prefs to song tags -->{#if type === 'work'}{[
										'',
										...t.lang_prefs
									]
										.map((p) => p.tag)
										.join(', ')}{/if})
							</address>{/if}</a
					>
				</li>
			{/each}
		</ul>
	{/if}
</span>

<style>
	ul {
		background-color: var(--otodb-bg-color);
	}
</style>
