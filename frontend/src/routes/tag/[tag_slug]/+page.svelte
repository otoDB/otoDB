<script lang="ts">
	import Section from "../../Section.svelte";
    import * as m from '$lib/paraglide/messages.js';
    import { WorkTagCategory } from "$lib/enums";
    import WorkCard from "$lib/WorkCard.svelte";

    let { data } = $props();
</script>

<svelte:head>
	<title>{m.mild_loud_shad_enchant({ type: m.empty_legal_chicken_taste(), name: data.tag.name })}</title>
</svelte:head>

<Section title={m.mild_loud_shad_enchant({ type: m.empty_legal_chicken_taste(), name: data.tag.name })}
    menuLinks={data.links}>

    <div>
        <span>{m.empty_legal_chicken_taste()}</span>
        {#each data.tree as node, i} > <a href={node.slug}>{node.name}</a> > {:else} > {/each}
        <span>{data.tag.name}</span>
    </div>

    <h2>{m.mild_loud_shad_enchant({type: m.plane_awful_bobcat_spark(), name: WorkTagCategory[data.tag.category]()})}</h2>
    
    {#if data.tag.aliases.length}
    <h3>Also known as: {#each data.tag.aliases as alias, i}{alias}{#if i + 1 != data.tag.aliases.length}, {/if}{/each}.</h3>
    {/if}

    <hr>

    {#if data.wiki_page}
    {@html data.wiki_page}
    {:else}
    <p>
        This tag does not yet have a wiki page.
    </p>
    {/if}
</Section>

{#if data.tag.song}
<Section title="Song: {data.tag.song.title}">
    <table><tbody>
        <tr><th>{m.large_factual_octopus_exhale()}</th><td>{data.tag.song.title}</td></tr>
        <tr><th>BPM</th><td>{data.tag.song.bpm}</td></tr>
        <tr><th>{m.crisp_red_canary_tickle()}</th><td>{data.tag.song.author}</td></tr>
    </tbody></table>
</Section>
{/if}

{#if data.tag.children.length}
<Section title={m.weird_nimble_fireant_climb()}>
    <ul>
        {#each data.tag.children as tag} 
        <li><a href={tag.slug}>{tag.name}</a></li>
        {/each}
    </ul>
</Section>
{/if}

<Section title="Works tagged with {data.tag.name}">
    {#if data.works.items.length}
    <div class="flex flex-wrap gap-3">
        {#each data.works.items as work}
        <WorkCard {work} />
        {/each}
    </div>
    {:else}
    <p>This tag is an orphan.</p>
    {/if}
</Section>

<Section title={m.same_broad_haddock_pinch()}>
    include 'comments.html' with object=tag 
</Section>
