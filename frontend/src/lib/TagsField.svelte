<script lang="ts">
	import { onMount } from 'svelte';
	import client from './api';
	import { clickOutside, debounce } from './ui';
	import { m } from './paraglide/messages';

	interface Props {
		value: string[];
		class: string;
		type: 'work' | 'song';
	}
	let { value = $bindable([]), type, ...props }: Props = $props();

	const endpoint = type === 'work' ? '/api/tag/search' : '/api/tag/song_tag_search';

	let textarea: HTMLTextAreaElement;
	let suggestions = $state<any[]>([]);

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

	const search = debounce(async () => {
		const query = getWordAtPos(textarea.value, textarea.selectionStart).word;
		if (query === '') {
			suggestions = [];
			return;
		}
		const { data } = await client.GET(endpoint, {
			params: { query: { query, limit: 10, resolve_aliases: false } }
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

	onMount(() => {
		if (value) {
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
			onOutclick={() => {
				suggestions = [];
			}}
		>
			{#each suggestions as t, i (i)}
				<li
					class="bg-otodb-bg-fainter hover:bg-otodb-bg-faint flex w-full justify-between gap-10 px-2 py-1"
				>
					<a
						class="max-w-60 cursor-pointer"
						href={null}
						onclick={() => {
							textarea.value = replaceWordAtPos(
								textarea.value,
								textarea.selectionStart,
								t.aliased_to ? t.aliased_to.slug : t.slug + ' '
							);
							suggestions = [];
							updateValue();
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
					<span>{t.n_instance}</span>
				</li>
			{/each}
		</ul>
	{/if}
</span>

<style>
	ul {
		background-color: var(--otodb-color-bg-primary);
		z-index: 1;
	}
</style>
