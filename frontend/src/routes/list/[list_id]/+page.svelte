<script lang="ts">
	import { base } from "$app/paths";
import Section from "../../Section.svelte";
	import type { PageProps } from "./$types";
    import * as m from '$lib/paraglide/messages.js';

    let { data }: PageProps = $props();
</script>

<svelte:head>
    <title>{m.mild_loud_shad_enchant({ type: m.stale_loose_squid_cut(), name: data.list.name})}</title>
</svelte:head>

<Section title={m.mild_loud_shad_enchant({ type: m.stale_loose_squid_cut(), name: data.list.name})}>
    <p class="whitespace-pre-wrap">{data.list.description}</p>
</Section>
<Section title="Entries">
    <ol class="list-decimal">
    {#each data.entries.items as entry}
    <li>
        <div style="display: flex; gap: 1rem;align-items:flex-start;">
            <a href="{base}/work/{entry.work.id}"><img style="max-width:10rem" src={entry.work.thumbnail} alt={entry.work.title}></a>
            <div><a href="{base}/work/{entry.work.id}">{entry.work.title}</a><p>{entry.description}</p></div>
        </div>
    </li>
    {:else}
    <li>This list has no entries!</li>
    {/each}
    </ol>
</Section>

<Section title={m.mushy_proof_hornet_dig()}>
    include 'comments.html' with object=view_user
</Section>
