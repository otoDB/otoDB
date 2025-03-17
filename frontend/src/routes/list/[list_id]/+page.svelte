<script lang="ts">
	import { base } from "$app/paths";
import Section from "../../Section.svelte";
	import type { PageProps } from "./$types";
    import { m } from '$lib/paraglide/messages.js';

    let { data }: PageProps = $props();
</script>

<svelte:head>
    <title>{m.mild_loud_shad_enchant({ type: m.stale_loose_squid_cut(), name: data.list.name})}</title>
</svelte:head>

<Section title={m.mild_loud_shad_enchant({ type: m.stale_loose_squid_cut(), name: data.list.name})}>
    <h3>By: <a href="{base}/profile/{data.list?.author.username}">{data.list?.author.username}</a></h3>
    <p class="whitespace-pre-wrap">{data.list.description}</p>
    {#if data.list?.author.username == data.user?.username }
    <a href="{base}/list/{data.list.id}/edit">Edit this list...</a>
    <a href="{base}/list/{data.list.id}/delete" data-sveltekit-preload-data="tap">Delete this list...</a>
    {/if}
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

<Section title={m.same_broad_haddock_pinch()}>
    include 'comments.html' with object=view_user
</Section>
