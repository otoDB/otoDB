<script lang="ts">
	import { onMount } from 'svelte';
	import client from './api';
	import { clickOutside, debounce } from './ui';

	interface Props {
		value: any[];
		type: 'work' | 'song';
	}
	let { value = $bindable([]), type, ...props }: Props = $props();

	const endpoint = type === 'work' ? '/api/tag/search' : '/api/tag/song_tag_search';

	let textarea: HTMLTextAreaElement;
	let suggestions: string[] = $state([]);

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
			params: { query: { query, limit: 10 } }
		});
		if (!data) return;
		suggestions = data.items.map((tag) => tag.slug);
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
		if (value) textarea.value = value.join(' ');
	});
</script>

<span role="none">
	<textarea
		onkeyup={() => {
			updateValue();
			search();
		}}
		onclick={search}
		bind:this={textarea}
		{...props}
	></textarea>
	<ul
		class="absolute"
		use:clickOutside
		onOutclick={() => {
			suggestions = [];
		}}
	>
		{#each suggestions as t}
			<li>
				<a
					href={null}
					onclick={() => {
						textarea.value = replaceWordAtPos(
							textarea.value,
							textarea.selectionStart,
							t + ' '
						);
						suggestions = [];
						updateValue();
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
