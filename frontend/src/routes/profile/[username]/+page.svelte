<script lang="ts">
	import Section from "../../Section.svelte";
	import type { PageProps } from "./$types";
    import * as m from '$lib/paraglide/messages.js';
	import { UserLevel } from "$lib/enums";

    let { data }: PageProps = $props();
</script>

<svelte:head>
    <title>{m.mild_loud_shad_enchant({ type: m.fuzzy_crazy_cobra_lead(), name: data.profile.username})}</title>
</svelte:head>

<Section title={m.mild_loud_shad_enchant({ type: m.fuzzy_crazy_cobra_lead(), name: data.profile.username})}
    menuLinks={data.links}>    
    <p>{UserLevel[data.profile?.level]}</p>
    <p>{m.mild_loud_shad_enchant({type: m.moving_funny_spider_feast(), name: data.profile.email})}</p>
    <p>Joined on {data.profile.date_created}</p>
</Section>

<Section title={m.same_broad_haddock_pinch()}>
    include 'comments.html' with object=view_user
</Section>
