<script lang="ts">
	import { base } from "$app/paths";
	import Section from "../../../Section.svelte";
	import SectionMenu from "../../../SectionMenu.svelte";
	import type { PageProps } from "./$types";
    import * as m from '$lib/paraglide/messages.js';

    let { data }: PageProps = $props();
</script>

<svelte:head>
    <title>{m.mild_loud_shad_enchant({ type: m.fuzzy_crazy_cobra_lead(), name: data.profile.username})}</title>
</svelte:head>

<Section title={m.mild_loud_shad_enchant({ type: m.fuzzy_crazy_cobra_lead(), name: data.profile.username})}>
    {#snippet menu()}
    <SectionMenu links={data.links} />
    {/snippet}
    <ul>
        {#each data.lists as list}
        <li><a href="{base}/list/{list.id}">{list.name}</a></li>
        {:else}
        <li>This user has no lists!</li>
        {/each}
    </ul>
</Section>

