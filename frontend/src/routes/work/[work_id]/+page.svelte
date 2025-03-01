<script lang="ts">
	import Section from "../../Section.svelte";
	import CollapsibleText from "./CollapsibleText.svelte";
    import * as m from '$lib/paraglide/messages.js';
	import { Platform, Rating, WorkOrigin, WorkStatus } from '$lib/enums';
	import WorkTag from "$lib/WorkTag.svelte";
	import { base } from "$app/paths";
    
    let { data } = $props();
</script>

<svelte:head>
	<title>{m.mild_loud_shad_enchant({ type: m.grand_merry_fly_succeed(), name: data.title })}</title>
</svelte:head>

<Section title={m.mild_loud_shad_enchant({ type: m.grand_merry_fly_succeed(), name: data.title })}
  menuLinks={data.links}>
    <div id="infobox">
      <img src={data.thumbnail} alt={data.title}>
      <div>
        <table>
        <tbody>
            <tr><th>{m.large_factual_octopus_exhale()}</th><td>{data.title}</td></tr>
            <tr><th>{m.clear_lucky_peacock_pick()}</th><td>{@html data.description}</td></tr>
            <tr><th>{m.good_dark_bumblebee_spur()}</th><td>{Rating[data.rating]()}</td></tr>
        </tbody>
        </table>
{#if data.user}
        <h2>{m.watery_sunny_seal_heal()}</h2>
        <table>
        <tbody>
            <tr>
                <th>{m.stale_loose_squid_cut()}</th>
                <td>
                    <button>Add/Remove...</button>
                </td>
            </tr>
        </tbody>
        </table>
{/if}
        </div>
        <ul id="work-tags">
            {#each data.tags as tag}
                <li><WorkTag {tag}/></li>
            {/each}
        </ul>
    </div>
</Section>

<Section title={m.extra_brave_tapir_skip()}
    menuLinks={[
        { pathname: `work/add?for_work=${data.id}`, title: m.helpful_away_jay_succeed() }
        ]}>
    <table class="w-full">
        <thead><tr>
            <th>{m.large_factual_octopus_exhale()}</th>
            <th>{m.clear_lucky_peacock_pick()}</th>
            <th>{m.sour_swift_sparrow_spin()}</th>
            <th>{m.super_agent_pigeon_aim()}</th>
            <th>{m.large_polite_otter_thrive()}</th>
            <th>{m.civil_trick_oryx_clap()}</th>
            <th>{m.big_dry_seahorse_succeed()}</th>
            <th>{m.noisy_moving_newt_belong()}</th>
{#if data.user}
            <th>{m.mushy_proof_hornet_dig()}</th>
{/if}
        </tr></thead>
    <tbody>
        {#each data.sources as src}
        <tr>
            <td class="whitespace-nowrap">{src.title}</td>
            <td><CollapsibleText text={src.description}></CollapsibleText></td>
            <td>{Platform[src.platform]}</td><td>{src.published_date}</td>
            <td class="whitespace-nowrap">{WorkOrigin[src.work_origin]()}</td><td class="whitespace-nowrap">{WorkStatus[src.work_status]()}</td>
            <td>{src.work_width}x{src.work_height}</td><td class="whitespace-nowrap"><a href={src.url} target="_blank" rel="noopener noreferrer">{m.noisy_moving_newt_belong()}</a></td>
{#if data.user}
            <td><button type="submit" class="whitespace-nowrap">{m.mushy_proof_hornet_dig()}</button></td>
{/if}
        </tr>
        {/each}
      </tbody>
    </table>
</Section>
<Section title={m.same_broad_haddock_pinch()}>
     include 'comments.html' with object=work 
</Section>

<style>
#infobox {
    display: grid;
    grid-template-columns: 1fr 2fr;
    column-gap: 2rem;
    align-items: center;
}
#work-tags {
    grid-column: 1 / span 2;
    border-top: var(--otodb-faint-content) 1px solid;
    margin-top: 2rem;
    padding-top: 1rem;
    display: flex;
    gap: .3rem 1rem;
    flex-wrap: wrap;
    list-style: none;
    &> li {
        margin: 0;
    }
}
th {
        white-space: nowrap;
}
</style>
