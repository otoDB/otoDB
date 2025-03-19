<script lang="ts">
	import { m } from "$lib/paraglide/messages";
	import Section from "$lib/Section.svelte";
	import WorkTag from "$lib/WorkTag.svelte";
	import WorkTagsField from "$lib/WorkTagsField.svelte";

    let { data } = $props();
</script>

<Section title={m.mild_loud_shad_enchant({ type: m.grand_merry_fly_succeed(), name: data.title })} menuLinks={data.links}>
<table><thead>
<tr><th>Tag</th><th>Rating</th><th>Action</th></tr>
</thead><tbody>
{#each data.tags as tag}
    <tr>
        <td><WorkTag {tag}/></td>
        <td></td>
        <td>
            <input type="checkbox" name="rating">
            <input type="checkbox" name="rating">
            <input type="checkbox" name="rating">
        </td>
    </tr>
{/each}
</tbody></table>

<h3>Add tags</h3>
<form action="">
    <WorkTagsField />
    <input type="submit">
</form>
</Section>

<style>
input[name="rating"] {
    appearance: none;
    background-color: var(--otodb-bg-color);
    border: 1px var(--otodb-content-color) solid;
    width: 1rem;
    height: 1rem;
    &:checked {
        background-color: var(--otodb-faint-content);
    }
}
</style>
