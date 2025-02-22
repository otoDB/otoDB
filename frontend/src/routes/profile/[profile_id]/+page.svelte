<script lang="ts">
	import Section from "../../Section.svelte";
	import SectionMenu from "../../SectionMenu.svelte";
	import type { PageProps } from "./$types";
    import * as m from '$lib/paraglide/messages.js';

    let { data }: PageProps = $props();
</script>

<svelte:head>
    <title>{m.mild_loud_shad_enchant({ type: m.fuzzy_crazy_cobra_lead(), name: data.profile.username})}</title>
</svelte:head>

<Section title="{m.mild_loud_shad_enchant({ type: m.fuzzy_crazy_cobra_lead(), name: data.profile.username})}">
    {#snippet menu()}
    <SectionMenu links={data.links} />
    {/snippet}
    <p>E-mail: {data.profile.email}</p>
    <p>Joined on {data.profile.date_created}</p>
</Section>

<Section title={m.same_broad_haddock_pinch()}>
    include 'comments.html' with object=view_user
</Section>
