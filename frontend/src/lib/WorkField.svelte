<script lang="ts">
	import client from './api';
	import type { components } from './schema';
	import { clickOutside, debounce } from './ui';

	let self: HTMLElement;

	let input: string = $state('');
	interface Props {
		value: components['schemas']['WorkSchema'] | null | undefined;
		// eslint-disable-next-line @typescript-eslint/no-unsafe-function-type
		oninput: Function | undefined;
	}
	let { value = $bindable(undefined), oninput = undefined, ...props }: Props = $props();

	let suggestions: components['schemas']['WorkSchema'][] = $state([]);
	let locked_in = $state(false);

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
			input = value.title;
			locked_in = true;
		} else {
			locked_in = false;
			input = '';
		}
	});
</script>

<span role="none" bind:this={self}>
	<input type="text" oninput={debounce(search)} disabled={locked_in} bind:value={input} />
	<input type="number" hidden value={value?.id ?? -1} {...props} />
	{#if locked_in}
		<button
			type="button"
			onclick={() => {
				value = null;
				locked_in = false;
				if (oninput) oninput(self, null);
			}}>Change</button
		>
		<a target="_blank" href="/work/{value?.id}"
			><img class="w-56" src={value?.thumbnail} alt={value?.title} /></a
		>
	{/if}
	<ul
		class="absolute"
		use:clickOutside
		onOutclick={() => {
			suggestions = [];
		}}
	>
		<!-- eslint-disable-next-line svelte/require-each-key -->
		{#each suggestions as v}
			<li>
				<a
					href={null}
					onclick={() => {
						value = v;
						input = v.title;
						suggestions = [];
						locked_in = true;
						if (oninput) oninput(self, v);
					}}>{v.title}</a
				>
			</li>
		{/each}
	</ul>
</span>

<style>
	ul {
		background-color: var(--otodb-bg-color);
		z-index: 10;
	}
</style>
