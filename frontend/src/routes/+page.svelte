<script lang="ts">
	import { m } from '$lib/paraglide/messages.js';

	import Section from '$lib/Section.svelte';

	let { data } = $props();
</script>

<svelte:head>
	<title>{m.fine_late_chicken_quiz()}</title>
	<meta name="description" content="the otomad/ytpmv database" />
</svelte:head>

<Section title={m.fine_late_chicken_quiz()}>
	<p>{m.silly_main_reindeer_chop()}</p>
	<div>
		<h2>
			{m.mild_loud_shad_enchant({ type: m.fuzzy_chunky_niklas_peek(), name: '' })}<a
				href="/work/{data.random.id}">{data.random.title}</a
			>
		</h2>
		<img style="width:25rem;" src={data.random.thumbnail} alt={data.random.title} />
	</div>
</Section>
