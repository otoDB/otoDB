<script lang="ts">
	import Section from '$lib/Section.svelte';
	import { m } from '$lib/paraglide/messages.js';
	import { SVGViewer } from 'svelte-svg-viewer';
	let { data } = $props();
</script>

<Section
	title={m.mild_loud_shad_enchant({ type: m.grand_merry_fly_succeed(), name: data.title })}
	menuLinks={data.links}
>
	{#if data.relations_svg}
		<SVGViewer maxScale={10} height="600px" width="100%" svgClass="fill-transparent">
			<!-- eslint-disable-next-line svelte/no-at-html-tags -->
			{@html data.relations_svg}
		</SVGViewer>
	{:else}
		<p>{m.left_watery_jellyfish_grip()}</p>
	{/if}
</Section>
