<script lang="ts">
	import { m } from '$lib/paraglide/messages.js';
	import Section from '$lib/Section.svelte';
	import RelationViewer from '$lib/RelationViewer.svelte';
	let { data } = $props();
</script>

<Section
	titleType={m.grand_merry_fly_succeed()}
	titleName={data.title}
	menuLinks={data.links}
>
	{#if data.works}
		<RelationViewer
			id={data.id}
			objects={data.works}
			relations={data.relations}
			defaultDir="TB"
			type="work"
		/>
	{:else}
		<p>{m.left_watery_jellyfish_grip()}</p>
	{/if}
</Section>
