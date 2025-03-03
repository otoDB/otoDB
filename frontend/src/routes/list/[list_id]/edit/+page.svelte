<script lang="ts">
    import Section from "../../../Section.svelte";
	import type { PageProps } from "./$types";
    import * as m from '$lib/paraglide/messages.js';
	import { enhance } from "$app/forms";
	import WorkField from "$lib/WorkField.svelte";

    let { data, form }: PageProps = $props();

    let list = $state(data.list), entries = $state(data.entries.items);
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
    <form method="POST" use:enhance>
        <table><tbody>
            {#each entries as entry, i}
            <tr><th>{i+1}</th><td>
                <WorkField value={entry.work}/>
            </td><td><textarea value={entry.description}></textarea></td></tr>
            {/each}
        </tbody></table>
        <input type="submit">
    </form>
</Section>
