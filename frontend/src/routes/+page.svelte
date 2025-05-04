<script lang="ts">
	import { m } from '$lib/paraglide/messages.js';

	import Section from '$lib/Section.svelte';
	import WorkCard from '$lib/WorkCard.svelte';

	let { data } = $props();
</script>

<svelte:head>
	<title>{m.fine_late_chicken_quiz()}</title>
	<meta name="description" content="the otomad/ytpmv database" />
</svelte:head>

<Section title={m.fine_late_chicken_quiz()}>
	<p>{m.silly_main_reindeer_chop()}</p>
	<div class="mt-2">
		<h2>
			{m.fuzzy_chunky_niklas_peek()}
		</h2>
		<div class="flex gap-2">
			{#each data.random as w, i (i)}
				<WorkCard work={w} />
			{/each}
		</div>
	</div>
</Section>
