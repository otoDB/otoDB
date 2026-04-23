<script lang="ts">
	import client from '$lib/api';
	import { m } from '$lib/paraglide/messages';
	import type { components } from '$lib/schema';
	import { clickOutside, debounce } from '$lib/ui';

	let self: HTMLElement;

	let input: string = $state('');
	interface Props {
		value: components['schemas']['SongSchema'] | null | undefined;
		// eslint-disable-next-line @typescript-eslint/no-unsafe-function-type
		oninput?: Function;
	}
	let { value = $bindable(undefined), oninput = undefined, ...props }: Props = $props();

	let suggestions: components['schemas']['SongSchema'][] = $state([]);
	let locked_in = $state(false);

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
		<a target="_blank" href="/tag/{value?.work_tag}">{value?.title}</a>
	{:else}
		<input type="text" oninput={debounce(search)} disabled={locked_in} bind:value={input} />
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
					<tr class="w bg-otodb-bg-fainter hover:bg-otodb-bg-faint p-1">
						<td
							><a
								class="cursor-pointer"
								href={`/tag/${v.work_tag}`}
								onclick={(e) => {
									if (e.button !== 0) return;
									e.preventDefault();
									value = v;
									input = v.title;
									suggestions = [];
									locked_in = true;
									if (oninput) oninput(self, v);
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
