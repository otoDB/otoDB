<script lang="ts">
	import Section from "../../../Section.svelte";
	import SectionMenu from "../../../SectionMenu.svelte";
    import * as m from '$lib/paraglide/messages.js';
    
    let { data } = $props();
</script>

<svelte:head>
	<title>{m.mild_loud_shad_enchant({ type: m.grand_merry_fly_succeed(), name: data.title })}</title>
</svelte:head>

<Section title={m.mild_loud_shad_enchant({ type: m.grand_merry_fly_succeed(), name: data.title })}>
    {#snippet menu()}
    <SectionMenu links={data.links} />
    {/snippet}
    {#if data.relations_html}
    {@html data.relations_html}
    {:else}
    <p>This work does not have any relations.</p>
    {/if}
</Section>
