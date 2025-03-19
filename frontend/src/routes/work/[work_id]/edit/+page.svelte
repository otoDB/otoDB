<script lang="ts">
	import Section from "$lib/Section.svelte";
    import { m } from '$lib/paraglide/messages.js';
	import { enhance } from "$app/forms";
	import type { PageProps } from "../$types";
	import { Platform, Rating, WorkOrigin, WorkRelationTypes } from "$lib/enums";
	import CollapsibleText from "../CollapsibleText.svelte";
	import WorkField from "$lib/WorkField.svelte";
	import client from "$lib/api";
	import type { components } from "$lib/schema";

    let { data, form }: PageProps = $props();
    let title: string = $state(form?.title ?? data.title!),
        description: string = $state(form?.description ?? data.description!),
        rating: number  = $state(form?.rating ?? data.rating!),
        thumbnail: string = $state(form?.thumbnail ?? data.thumbnail!);

    let relations: { swapped: boolean, work: components['schemas']['WorkSchema'] | null, relation: number }[] = $state(data.relations[0].map(({ A, B, relation }) => ({
        swapped: A.id === data.id,
        work: data.relations[1].find(e => e.id === (A.id === data.id ? B.id : A.id)),
        relation
    })));
    const delete_relation = (i: number) => async () => {
        await client.DELETE('/api/work/relation', { fetch, params: { query: { A: relations[i].work.id!, B: data.id! }}});
        relations.splice(i, 1);
    };
    const swap_relation = (i: number) => async () => {
        await client.POST('/api/work/relation', { fetch, body: {
            A: { id: relations[i].swapped ? relations[i].work.id! : data.id! },
            B: { id: !relations[i].swapped ? relations[i].work.id! : data.id! },
            relation: relations[i].relation
        }});
        relations[i].swapped = !relations[i].swapped;
    };
    const post_relation = (i: number) => async () => {
        const r = relations[i];
        relations = relations.filter((rel, j) => rel.work.id !== r.work.id || j === i);
        if (r.work.id) {
            await client.POST('/api/work/relation', { fetch, body: {
                A: { id: !r.swapped ? r.work.id! : data.id! },
                B: { id: r.swapped ? r.work.id! : data.id! },
                relation: r.relation
            }});
        }
        else
            await client.DELETE('/api/work/relation', { fetch, params: { query: { A: r.work.id!, B: data.id! }}});
    };
</script>

<svelte:head>
	<title>{m.mild_loud_shad_enchant({ type: m.grand_merry_fly_succeed(), name: data.title })}</title>
</svelte:head>

<Section title={m.mild_loud_shad_enchant({ type: m.grand_merry_fly_succeed(), name: data.title })}
  menuLinks={data.links}>
<form method="POST" use:enhance action="?/edit">
    {#if form?.failed}<p class="error">Failed!</p>{/if}
    <table class="inline">
    <tbody>
        <tr><th><label for="title">Title</label></th><td><input required type="text" name="title" bind:value={title}></td></tr>
        <tr><th><label for="description">Description</label></th><td><textarea name="description" bind:value={description}></textarea></td></tr>
        <tr><th><label for="rating">Rating</label></th><td><select name="rating" bind:value={rating}>
            {#each Rating as r, i}<option value={i}>{r()}</option>{/each}</select></td></tr>
        <tr><th><label for="thumbnail">Thumbnail</label></th><td><input type="text" required name="thumbnail" bind:value={thumbnail}></td></tr>
        <tr><th><label for="reason">Update Reason</label></th><td><input type="text" required name="reason" value={form?.reason ?? ''}></td></tr>
    </tbody>
    </table>
    <table class="inline">
        <thead><tr>
            <th></th>
            <th>{m.large_factual_octopus_exhale()}</th>
            <th>{m.clear_lucky_peacock_pick()}</th>
            <th>{m.sour_swift_sparrow_spin()}</th>
            <th>{m.large_polite_otter_thrive()}</th>
        </tr></thead>
    <tbody>
        {#each data.sources! as src}
        <tr>
            <td><button onclick={() => {
                title = src.title;
                description = src.description;
                thumbnail = src.thumbnail;
            }} type="button">&lt;&lt;</button></td>
            <td class="whitespace-nowrap">{src.title}</td>
            <td><CollapsibleText text={src.description}></CollapsibleText></td>
            <td>{Platform[src.platform]}</td>
            <td class="whitespace-nowrap">{WorkOrigin[src.work_origin]()}</td>
        </tr>
        {/each}
      </tbody>
    </table>
<br>
    <input type="submit"/>
</form>
</Section>

<Section title="Relations">
<button type="button" onclick={() => {relations.push({ swapped: false, work: null, relation: 0 })}}>Add Relation</button>
<table><tbody>
    {#each relations as relation, i}
    <tr>
        <td>{#if !relation.swapped}<WorkField bind:value={relation.work} oninput={post_relation(i)}/>{:else}This work{/if}</td>
        <td>is a</td>
        <td><select name="relation" bind:value={relation.relation} onchange={post_relation(i)}>
            {#each WorkRelationTypes as rel, j}
            <option value={j}>{rel()}</option>
            {/each}
        </select></td>
        <td>of</td><td>{#if relation.swapped}<WorkField bind:value={relation.work} oninput={post_relation(i)}/>{:else}this work{/if}</td>
        <td><button type="button" onclick={swap_relation(i)}>Swap</button></td>
        <td><button type="button" onclick={delete_relation(i)}>Delete</button></td>
    </tr>
    {/each}
</tbody></table>
</Section>
