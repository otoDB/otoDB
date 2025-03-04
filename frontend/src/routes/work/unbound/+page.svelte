<script lang="ts">
	import Section from "../../Section.svelte";
	import type { PageProps } from "./$types";
    import * as m from '$lib/paraglide/messages.js';
	import { Platform, WorkOrigin } from "$lib/enums";
	import { base } from "$app/paths";
	import UnboundSourceActions from "./UnboundSourceActions.svelte";
	import RefreshButton from "../RefreshButton.svelte";

    let { data }: PageProps = $props();
</script>

<svelte:head>
    <title>Pending sources</title>
</svelte:head>

<Section title="Pending sources" menuLinks={data.links}>
<ul>
    {#each data.sources as src}
    <li>
        <span>
            <h3><a href="{src.url}" target="_blank" rel="noopener noreferrer">{src.title}</a></h3>
            <h4>Requested by: <a href="{base}/profile/{src.added_by.username}">{src.added_by.username}</a></h4>
            <h4>{Platform[src.platform]} {src.published_date}</h4>
            <h4>Claimed origin: {WorkOrigin[src.work_origin]()}</h4>
            <RefreshButton source={src}/>
            <UnboundSourceActions source={src} />
        </span>
        <span>
            <a href={src.url} target="_blank" rel="noopener noreferrer"><img src={src.thumbnail} alt={src.title} class="w-50 float-right clear-both"></a>
        </span>
    </li>
    {:else}
    <li>There are no pending sources.</li>
    {/each}
</ul>
</Section>

<style>
    ul > li {
        display: flex;
        background-color: var(--otodb-fainter-bg);
        justify-content: space-between;
    }
</style>
