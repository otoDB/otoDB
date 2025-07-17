<script lang="ts">
	import client from './api';
	import { m } from './paraglide/messages';
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
			}}>{m.quick_happy_trout_amuse()}</button
		>
		<a target="_blank" href="/work/{value?.id}" class="underline">
			<img class="w-56" src={value?.thumbnail} alt={value?.title} />
		</a>
	{/if}
	{#if suggestions.length}
		<table
			class="absolute z-1 px-1"
			use:clickOutside
			onOutclick={() => {
				suggestions = [];
			}}
		>
			<tbody>
				{#each suggestions as v, i (i)}
					<tr class="w bg-otodb-fainter-bg hover:bg-otodb-faint-bg p-1">
						<td><img class="w-20" src={v.thumbnail} alt={v.title} /></td>
						<td
							><a
								class="cursor-pointer"
								href={null}
								onclick={() => {
									value = v;
									input = v.title;
									suggestions = [];
									locked_in = true;
									if (oninput) oninput(self, v);
								}}>{v.title} ({v.id})</a
							>
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	{/if}
</span>

<style>
	ul {
		background-color: var(--otodb-bg-color);
		z-index: 10;
	}
</style>
