<script lang="ts">
	import Section from "../../Section.svelte";
    import * as m from '$lib/paraglide/messages.js';
	import type { PageProps } from "./$types";
	import { enhance } from "$app/forms";

    let { data, form }: PageProps = $props();
</script>

<svelte:head>
    <title>New work source{data.title ? ' for ' + data.title : ''}</title>
</svelte:head>

<Section title="New work source{data.title ? ' for ' + data.title : ''}">
<p>
Currently accepted sites:
</p>
<ul>
    <li>YouTube</li>
    <li>Niconico</li>
    <li>Bilibili</li>
    <li>SoundCloud</li>
</ul>
<form method="POST" use:enhance>
    {#if form?.failed}<p class="error">Failed!</p>{/if}
    <table>
    <tbody>
        <tr>
            <th><label for="url">URL</label></th>
            <td><input type="text" name="url" value={form?.url ?? ''}></td>
        </tr>
        <tr>
            <th><label for="origin">Is this an official upload?</label></th>
            <td><input type="checkbox" name="origin" checked={form?.origin ?? !data.title}></td>
        </tr>
    </tbody>
    </table>
    <input type="submit"/>
</form>
</Section>
