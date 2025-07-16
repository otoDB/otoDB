<script lang="ts">
	import { m } from './paraglide/messages';
	let { fetchNextBatch, results = $bindable([]), maxCount } = $props();

	let fetching = $state(false);
	const getNextBatch = async () => {
		fetching = true;
		const { data: d } = await fetchNextBatch();
		results = results.concat(d!.items);
		fetching = false;
	};
</script>

{#if !fetching && results.length < maxCount}
	<button class="center mx-auto mt-5 block p-2" onclick={getNextBatch}
		>{m.red_pink_bear_play()}</button
	>
{/if}
