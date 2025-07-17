<script lang="ts">
	import { m } from './paraglide/messages';
	let { fetchNextBatch, results = $bindable([]), maxCount } = $props();

	let fetching = $state(false);
	const getNextBatch = async () => {
		if (fetching) return;
		fetching = true;
		const { data: d } = await fetchNextBatch();
		results = results.concat(d!.items);
		fetching = false;
	};
</script>

{#if results.length < maxCount}
	<button
		disabled={fetching}
		class={['center mx-auto mt-5 block p-2', { 'text-otodb-fainter-content': fetching }]}
		onclick={getNextBatch}>{m.red_pink_bear_play()}</button
	>
{/if}
