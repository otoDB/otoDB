<script lang="ts">
    import Section from "../../../Section.svelte";
	import type { PageProps } from "./$types";
    import { m } from '$lib/paraglide/messages.js';
	import { enhance } from "$app/forms";
	import WorkField from "$lib/WorkField.svelte";
	import { debounce } from "$lib/ui";
	import client from "$lib/api";

    let { data, form }: PageProps = $props();

    let counter = data.entries?.items.length;

    let entries = $state(data.entries!.items.map((el, i) => Object.assign({}, el, {ui_id: i})));
    
    let entries_copy = [...entries]; // not $state on purpose

    let source: HTMLElement | null = $state(null), target: HTMLElement | null = $state(null);

    function dragenter(e) {
        target = e.target;

        const tgt = e.target!.closest('tr'),
            src = source?.closest('tr');

            
        if (src && tgt) {
            entries = entries_copy;
            const from = entries.findIndex(e => e.ui_id === +src.dataset.idx!), to = Array.from(tgt.parentNode.children).indexOf(tgt);
            entries.splice(to, 0, entries.splice(from, 1)[0]);
        }
    }
    
    function ondragstart(e) {
        source = e.target;
        e.dataTransfer!.effectAllowed = 'move';
    }

    function ondragend(e) {
        const src = source?.closest('tr');
        // FIXME this seems slow and unnecessary?
        const from = entries_copy.findIndex(e => e.ui_id === +src.dataset.idx!), to = entries.findIndex(e => e.ui_id === +src.dataset.idx!);
        client.PUT('/api/list/items', { fetch, params: { query: { list_id: data.list.id! } }, body: {
            move: [[from, to]],
            delete: [], insert_at: [], update_description: [], update_work: []
        }});
        
        source = null;
        target = null;
        entries_copy = [...entries];
    }

    async function update_description(el) {
        await client.PUT('/api/list/items', { fetch, params: { query: { list_id: data.list.id! } }, body: {
            update_description: [[+el.target.closest('tr').dataset.ridx, el.target.value]],
            move: [], delete: [], insert_at: [], update_work: []
        }});
    }

    async function update_work(el: HTMLElement, work) {
        if (work) {
            await client.PUT('/api/list/items', { fetch, params: { query: { list_id: data.list.id! } }, body: {
                update_work: [[+el.closest('tr')!.dataset.ridx!, work.id]],
                update_description: [], move: [], delete: [], insert_at: []
            }});
        }
    }
</script>

<svelte:head>
    <title>{m.mild_loud_shad_enchant({ type: m.stale_loose_squid_cut(), name: data.list.name})}</title>
</svelte:head>

<Section title={m.mild_loud_shad_enchant({ type: m.stale_loose_squid_cut(), name: data.list.name})}>
    <form use:enhance method="POST">
        <table><tbody>
            <tr><th><label for="name">Name</label></th><td><input type="text" name="name" value={form?.name ?? data.list?.name}></td></tr>
            <tr><th><label for="description">Description</label></th><td><textarea name="description" value={form?.description ?? data.list?.description}></textarea></td></tr>
        </tbody></table>
        <input type="submit">
    </form>
</Section>
<Section title="Entries">
    <table><tbody>
        {#each entries as entry, i (entry.ui_id)}
        <tr ondragenter={debounce(dragenter, 50)} data-idx={entry.ui_id} data-ridx={i}><th>{i+1}</th><td><div class="pl-5 pr-5 border select-none" draggable="true" {ondragstart} {ondragend} role="none">=</div></td><td>
            <WorkField value={entry.work} oninput={update_work}/>
        </td><td><textarea value={entry.description} oninput={debounce(update_description)}></textarea></td></tr>
        {/each}
    </tbody></table>
</Section>
