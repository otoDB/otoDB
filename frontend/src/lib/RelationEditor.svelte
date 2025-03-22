<script lang="ts">
	import { invalidate } from "$app/navigation";
	import client from "./api";
	import { SongRelationTypes, WorkRelationTypes } from "./enums";
	import type { components } from './schema';
	import SongField from "./SongField.svelte";
	import WorkCard from "./WorkCard.svelte";
	import WorkField from "./WorkField.svelte";

interface Props {
    this_id: number;
    obj_type: 'work' | 'song';
    init_relations: [components['schemas']['RelationSchema'][], {id: number}[]];
}

let { this_id, init_relations, obj_type }: Props = $props()

const endpoint = obj_type === 'work' ? '/api/work/relation' : '/api/tag/song_relation';

let relations: { swapped: boolean, item: any | null, relation: number }[] = $state(init_relations[0].filter(({ A__id, B__id }) => A__id === this_id || B__id === this_id).map(({ A__id, B__id, relation }) => ({
        swapped: A__id === this_id,
        item: init_relations[1].find(e => e.id === (A__id === this_id ? B__id : A__id)),
        relation
    })));
    const delete_relation = (i: number) => async () => {
        await client.DELETE(endpoint, { fetch, params: { query: { A: relations[i].item.id!, B: this_id }}});
        relations.splice(i, 1);
    };
    const post_relation = (i: number) => async () => {
        const r = relations[i];
        relations = relations.filter((rel, j) => rel.item.id !== r.item.id || j === i);
        if (r.item.id) {
            await client.POST(endpoint, { fetch, body: {
                A__id: !r.swapped ? r.item.id : this_id!,
                B__id: r.swapped ? r.item.id : this_id!,
                relation: r.relation
            }});
        }
        invalidate(`/${obj_type === 'song' ? 'tag' : 'work'}/`)
    };
    const swap_relation = (i: number) => async () => {
        relations[i].swapped = !relations[i].swapped;
        await post_relation(i)();
    };
    let new_item = $state(null);
    const add_new_item = async () => {
        if (new_item) {
            relations.push({ swapped: false, item: new_item, relation: 0 });
            await (post_relation(relations.length - 1))();
            new_item = null;
        }
    };
</script>

<div class="grid grid-cols-2 gap-3 w-fit">
    {#if obj_type === 'work'}
    <WorkField bind:value={new_item}/>
    {:else if obj_type === 'song'}
    <SongField bind:value={new_item}/>
    {/if}
    <button onclick={add_new_item} disabled={!new_item}>Add</button>
</div>
<table><tbody>
{#each relations as relation, i}
<tr>
    <td>{#if !relation.swapped}{#if obj_type === 'work'}<WorkCard work={relation.item}/>{:else if obj_type === 'song'}<a href="/tag/{relation.item.work_tag}">{relation.item.title}</a>{/if}{:else}This {#if obj_type === 'work'}work{:else if obj_type === 'song'}song{/if}{/if}</td>
    <td>is a</td>
    <td><select name="relation" bind:value={relation.relation} onchange={post_relation(i)}>
        {#each obj_type === 'work' ? WorkRelationTypes : SongRelationTypes as rel, j}
        <option value={j}>{rel()}</option>
        {/each}
    </select></td>
    <td>of</td><td>{#if relation.swapped}{#if obj_type === 'work'}<WorkCard work={relation.item}/>{:else if obj_type === 'song'}<a href="/tag/{relation.item.work_tag}">{relation.item.title}</a>{/if}{:else}this {#if obj_type === 'work'}work{:else if obj_type === 'song'}song{/if}{/if}</td>
    <td><button type="button" onclick={swap_relation(i)}>Swap</button></td>
    <td><button type="button" onclick={delete_relation(i)}>Delete</button></td>
</tr>
{/each}
</tbody></table>
