<script lang="ts">
	import client from '$lib/api';
	import { m } from '$lib/paraglide/messages';
	import type { components } from '$lib/schema';
	import { clickOutside, debounce } from '$lib/ui';
	import { tick } from 'svelte';

	let self: HTMLElement;
	let search_input: HTMLInputElement | undefined = $state();

	export async function focus() {
		await tick();
		search_input?.focus();
	}

	let input: string = $state('');
	interface Props {
		value: components['schemas']['SongSchema'] | null | undefined;
		// eslint-disable-next-line @typescript-eslint/no-unsafe-function-type
		oninput?: Function;
	}
	let { value = $bindable(undefined), oninput = undefined, ...props }: Props = $props();

	let suggestions: components['schemas']['SongSchema'][] = $state([]);
	let locked_in = $state(false);
	let selectedIndex = $state(0);

	$effect(() => {
		void suggestions;
		selectedIndex = 0;
	});

	const selectSong = (v: (typeof suggestions)[number]) => {
		value = v;
		input = v.title;
		suggestions = [];
		locked_in = true;
		if (oninput) oninput(self, v);
	};

	const handleKeyDown = (e: KeyboardEvent) => {
		if (!suggestions.length) return;

		if (e.key === 'ArrowDown') {
			e.preventDefault();
			selectedIndex = (selectedIndex + 1) % suggestions.length;
		} else if (e.key === 'ArrowUp') {
			e.preventDefault();
			selectedIndex = selectedIndex <= 0 ? suggestions.length - 1 : selectedIndex - 1;
		} else if (e.key === 'Enter') {
			e.preventDefault();
			selectSong(suggestions[selectedIndex]);
		} else if (e.key === 'Escape') {
			suggestions = [];
		}
	};

	const search = async () => {
		if (input === '') {
			suggestions = [];
			return;
		}
		const { data } = await client.GET('/api/tag/song_search', {
			params: { query: { query: input, limit: 10, author: '' } }
		});
		if (!data) return;
		suggestions = data.items;
	};

	$effect(() => {
		if (value) {
			input = value.title;
			locked_in = true;
		} else {
			locked_in = false;
			input = '';
		}
	});
</script>

<span role="none" bind:this={self}>
	<input type="text" hidden value={value?.id ?? '-1'} {...props} />
	{#if locked_in}
		<button
			type="button"
			onclick={() => {
				value = null;
				locked_in = false;
				if (oninput) oninput(self, null);
				focus();
			}}>{m.quick_happy_trout_amuse()}</button
		>
		<a target="_blank" href="/tag/{value?.work_tag}">{value?.title}</a>
	{:else}
		<input
			type="text"
			oninput={debounce(search)}
			onkeydown={handleKeyDown}
			disabled={locked_in}
			bind:value={input}
			bind:this={search_input}
		/>
	{/if}
	{#if suggestions.length}
		<table
			class="absolute z-1 px-1"
			use:clickOutside
			onoutclick={() => {
				suggestions = [];
			}}
		>
			<tbody>
				{#each suggestions as v, i (i)}
					<tr
						class={['p-1', selectedIndex === i ? 'bg-otodb-bg-faint' : 'bg-otodb-bg-fainter']}
						onmouseenter={() => (selectedIndex = i)}
					>
						<td
							><a
								class="cursor-pointer"
								href={`/tag/${v.work_tag}`}
								onclick={(e) => {
									if (e.button !== 0) return;
									e.preventDefault();
									selectSong(v);
								}}>{v.title}</a
							>
						</td>
						<td>{v.author}</td>
					</tr>
				{/each}
			</tbody>
		</table>
	{/if}
</span>
