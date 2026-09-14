<script lang="ts">
	import { m } from '$lib/paraglide/messages.js';
	import Section from '$lib/Section.svelte';
	import RelationViewer from '$lib/RelationViewer.svelte';
	let { data } = $props();
</script>

<Section type={m.grand_merry_fly_succeed()} title={data.title} menuLinks={data.links}>
	{#if data.works}
		<RelationViewer
			svg={data.svg}
			direction={data.direction}
			max_distance={data.max_distance}
			degree={data.degree}
			show_thumbs={data.show_thumbs}
			allowed_types={data.allowed_types}
			type="work"
		/>
	{:else}
		<p>{m.left_watery_jellyfish_grip()}</p>
	{/if}
</Section>
