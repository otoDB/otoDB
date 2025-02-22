<script lang="ts">
	import Section from "../../Section.svelte";
	import SectionMenu from "../../SectionMenu.svelte";
    import * as m from '$lib/paraglide/messages.js';
	import { base } from "$app/paths";
    
    let { data } = $props();
</script>

<svelte:head>
	<title>{m.mild_loud_shad_enchant({ type: m.empty_legal_chicken_taste(), name: data.tag.name })}</title>
</svelte:head>

<Section title={m.mild_loud_shad_enchant({ type: m.empty_legal_chicken_taste(), name: data.tag.name })}>
    {#snippet menu()}
    <SectionMenu links={data.links} />
    {/snippet}

    <div>
        <span>{m.empty_legal_chicken_taste()}</span>
        {#each data.tree as node, i} > <a href={node.slug}>{node.name}</a> > {:else} > {/each}
        <span>{data.tag.name}</span>
    </div>

    <h2>{m.mild_loud_shad_enchant({type: m.plane_awful_bobcat_spark(), name: data.tag.category})}</h2>
    
    {#if data.tag.aliases.length}
    <h3>Also known as: {#each data.tag.aliases as alias, i}{alias}{#if i + 1 != data.tag.aliases.length}, {/if}{/each}.</h3>
    {/if}

    <hr>

    {#if data.wiki_page}
    {@html data.wiki_page}
    {:else}
    <p>
        This tag does not yet have a wiki page. <a href="#TODO">Go create one...</a>
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
    <table>
        <thead><tr><th>Thumbnail</th><th>Title</th><th>Rating</th><th>Tags</th></tr></thead><tbody>
            {#each data.works.items as work}
            <tr>
                <td><img src={work.thumbnail} alt={work.title} style="width:10rem;"></td>
                <td><a href="{base}/work/{work.id}">{work.title} </a></td>
                <td>{work.rating} </td>
                <td>{work.tags.map(t => t.name).join(', ')}</td>
            </tr>
            {/each}
        </tbody>
    </table>
    {:else}
    <p>This tag is an orphan.</p>
    {/if}
</Section>

<Section title={m.same_broad_haddock_pinch()}>
    include 'comments.html' with object=tag 
</Section>
   