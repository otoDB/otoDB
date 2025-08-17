<script lang="ts">
	import client from './api';
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
	<input type="text" oninput={debounce(search)} bind:value {...props} />
	{#if suggestions.length}
		<ul
			class="absolute z-1 list-none"
			use:clickOutside
			onOutclick={() => {
				suggestions = [];
			}}
		>
			{#each suggestions as t, i (i)}
				<li class="bg-otodb-bg-fainter hover:bg-otodb-bg-faint px-2 py-1">
					<a
						class="cursor-pointer"
						href={null}
						onclick={() => {
							value = t.aliased_to ? t.aliased_to.slug : t.slug;
							suggestions = [];
						}}
						>{t.aliased_to ? `${t.name} → ${t.aliased_to.name}` : t.name}
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
		background-color: var(--otodb-color-bg-primary);
	}
</style>
