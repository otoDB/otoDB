<script lang="ts">
	import Section from "$lib/Section.svelte";
    import { m } from '$lib/paraglide/messages.js';
    import { WorkTagCategory } from "$lib/enums";
	import { enhance } from "$app/forms";
	import type { PageProps } from "./$types";
	import WorkTagField from "$lib/WorkTagField.svelte";

    let { data, form }: PageProps = $props();
    let category = $state(form?.category ?? data.tag?.category);
</script>

<svelte:head>
	<title>{m.mild_loud_shad_enchant({ type: m.empty_legal_chicken_taste(), name: data.tag.name })}</title>
</svelte:head>

<Section title={m.mild_loud_shad_enchant({ type: m.empty_legal_chicken_taste(), name: data.tag.name })}
    menuLinks={data.links}>
<form method="POST" use:enhance action="?/edit">
    {#if form?.failed}<p class="error">Failed!</p>{/if}
    <table>
    <tbody>
        <tr>
            <!-- disable if song -->
            <th><label for="category">{m.plane_awful_bobcat_spark()}</label></th>
            <td><select name="category" bind:value={category} disabled={data.tag?.category == 2}>
                {#each WorkTagCategory as cat, i}
                <option value={i}>{cat()}</option>
                {/each}
            </select></td>
        </tr>
        <tr>
            <th><label for="parent">Parent</label></th>
            <td><WorkTagField name="parent" value={form?.parent_slug ?? data.parent_slug ?? ''}/></td>
        </tr>
    </tbody>
    </table>
    {#if data.tag?.category === 2}
    <p>To change the cateogry, <button formaction="?/delete_song">delete the associated song</button>.</p>
    {/if}
    {#if category === 2}
    <h2>Song Information</h2>
    <table><tbody>
        <tr><th><label for="song_title">Title</label></th><td><input type="text" name="song_title" value="{data.tag?.song?.title ?? ''}"></td></tr>
        <tr><th><label for="song_author">Author</label></th><td><input type="text" name="song_author" value={data.tag?.song?.author ?? ''}></td></tr>
        <tr><th><label for="song_bpm">BPM</label></th><td><input type="number" name="song_bpm" value={data.tag?.song?.bpm ?? 100}></td></tr>
    </tbody></table>
    {/if}
    <input type="submit"/>
</form>
</Section>

<Section title="Wiki page">
<form action="?/wiki_page" method="POST" use:enhance>
    <textarea required name="md" class="block w-full" value={data.wiki_page ?? ''}></textarea>
    <input type="submit"/>
</form>
</Section>
