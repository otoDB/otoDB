<script lang="ts">
	import { m } from '$lib/paraglide/messages.js';

	import Section from '$lib/Section.svelte';
	import WorkCard from '$lib/WorkCard.svelte';

	let { data } = $props();
</script>

<svelte:head>
	<title>{m.fine_late_chicken_quiz()}</title>
	<meta name="description" content={m.glad_born_mouse_taste()} />
</svelte:head>

<Section title={m.fine_late_chicken_quiz()}>
	<p>{m.silly_main_reindeer_chop()}</p>
	<ul>
		<li>
			<a href="/post/2">{m.noble_fine_iguana_pull()}</a>
		</li>
	</ul>

	<hr class="my-4" />

	<div class="w-full">
		<h2 class="mb-4 px-4 text-2xl">{m.fuzzy_chunky_niklas_peek()}</h2>
		<div class="grid grid-cols-[repeat(auto-fill,minmax(192px,1fr))] gap-x-4 gap-y-4">
			{#each data.random as w, i (i)}
				<WorkCard work={w} />
			{/each}
		</div>
	</div>

	<hr class="my-4" />

	<div class="w-full">
		<h2 class="mb-4 px-4 text-2xl">{m.big_long_squirrel_kiss()}</h2>
		<div class="grid grid-cols-[repeat(auto-fill,minmax(192px,1fr))] gap-x-4 gap-y-4">
			{#each data.recent as w, i (i)}
				<WorkCard work={w} />
			{/each}
		</div>
	</div>
</Section>
