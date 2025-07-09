<script lang="ts">
	import { m } from '$lib/paraglide/messages.js';

	import Section from '$lib/Section.svelte';
	import WorkCard from '$lib/WorkCard.svelte';

	let { data } = $props();
</script>

<svelte:head>
	<title>{m.fine_late_chicken_quiz()}</title>
	<meta name="description" content={m.glad_born_mouse_taste()} />
	<meta property="og:site_name" content="otodb.net" />
</svelte:head>

<Section title={m.fine_late_chicken_quiz()}>
	<p>{m.silly_main_reindeer_chop()}</p>
	<hr class="my-3" />
	<div class="grid grid-cols-[repeat(auto-fill,minmax(192px,1fr))] gap-x-4 gap-y-4">
		{#each data.random as w, i (i)}
			<WorkCard work={w} />
		{/each}
	</div>
</Section>
