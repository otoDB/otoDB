<script lang="ts">
	import client from '$lib/api';
	import DisplayText from '$lib/DisplayText.svelte';
	import { m } from '$lib/paraglide/messages';
	import type { components } from '$lib/schema';
	import { clickOutside, debounce } from '$lib/ui';
	import { getDisplayText } from '$lib/ui.js';
	import WorkThumbnail from '$lib/WorkThumbnail/WorkThumbnail.svelte';
	import { tick } from 'svelte';

	let self: HTMLElement;
	let search_input: HTMLInputElement | null = null;

	export async function focus() {
		await tick();
		search_input?.focus();
	}

	let input: string = $state('');
	type Work = components['schemas']['ThinWorkSchema'];
	interface Props {
		value: Work | null | undefined;
		oninput?: (element: HTMLSpanElement, v: Work | null) => void;
		name?: string;
	}
	let { value = $bindable(undefined), oninput = undefined, name }: Props = $props();

	let suggestions: Work[] = $state([]);
	let locked_in = $state(false);
	let selectedIndex = $state(0);

	$effect(() => {
		void suggestions;
		selectedIndex = 0;
	});

	const selectWork = (v: Work) => {
		value = v;
		input = getDisplayText(v.title, '');
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
			selectWork(suggestions[selectedIndex]);
		} else if (e.key === 'Escape') {
			suggestions = [];
		}
	};

	const search = async () => {
		if (input === '') {
			suggestions = [];
			return;
		}
		const { data } = await client.GET('/api/work/search', {
			params: { query: { query: input, limit: 10 } }
		});
		if (!data) return;
		suggestions = data.items;
	};

	$effect(() => {
		if (value) {
			input = getDisplayText(value.title, '');
			locked_in = true;
		} else {
			locked_in = false;
			input = '';
		}
	});
</script>

<span role="none" bind:this={self}>
	<input
		type="text"
		oninput={debounce(search)}
		onkeydown={handleKeyDown}
		disabled={locked_in}
		bind:value={input}
		bind:this={search_input}
	/>
	<input type="text" hidden value={value?.id ?? '-1'} {name} />
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
		<a target="_blank" href="/work/{value?.id}"
			><WorkThumbnail
				class="aspect-video w-56"
				thumbnail={value?.thumbnail}
				alt={getDisplayText(value?.title)}
			/></a
		>
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
							><WorkThumbnail
								class="aspect-video w-20"
								thumbnail={v.thumbnail}
								alt={getDisplayText(v.title)}
							/></td
						>
						<td
							><a
								class="cursor-pointer"
								href={`/work/${v.id}`}
								onclick={(e) => {
									if (e.button !== 0) return;
									e.preventDefault();
									selectWork(v);
								}}><DisplayText value={v.title} /> ({v.id})</a
							>
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	{/if}
</span>
