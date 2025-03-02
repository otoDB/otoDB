<script lang="ts">
	import Section from "../../Section.svelte";
	import type { PageProps } from "./$types";
    import * as m from '$lib/paraglide/messages.js';
	import WorkField from "$lib/WorkField.svelte";

    let { data }: PageProps = $props();
</script>

<svelte:head>
    <title>Merge</title>
</svelte:head>

<Section title="Merge">
<form method="POST">
    <table><tbody>
        <tr><th></th>
            <td>
                <WorkField/>
            </td>
            <td>Keep Left</td><td>Keep Right</td>
            <td>
                <WorkField/>
            </td>
            <th></th></tr>
        <tr><th>Title</th>
            <td><input type="text" disabled="works[0].id <= 0 || selecting.title != 0" x-model="works[0].title"></td>
            <td><input type="radio" disabled="works[0].id <= 0" checked="selecting.title == 0"></td>
            <td><input type="radio" disabled="works[1].id <= 0" checked="selecting.title == 1"></td>
            <td><input type="text" disabled="works[1].id <= 0 || selecting.title != 1" x-model="works[1].title"></td>
            <th>Title</th></tr>
        <tr><th>Description</th>
            <td><textarea disabled="works[0].id <= 0 || selecting.description != 0" x-model="works[0].description"></textarea></td>
            <td><input type="radio" disabled="works[0].id <= 0" checked="selecting.description == 0"></td>
            <td><input type="radio" disabled="works[1].id <= 0" checked="selecting.description == 1"></td>
            <td><textarea disabled="works[1].id <= 0 || selecting.description != 1" x-model="works[1].description"></textarea></td>
            <th>Description</th></tr>
        <tr><th>Thumbnail</th>
            <td><input type="text" disabled="works[0].id <= 0 || selecting.thumbnail != 0" x-model="works[0].thumbnail"><img style="width: 15rem;" :src="works[0].thumbnail" :alt="works[0].title"></td>
            <td><input type="radio" disabled="works[0].id <= 0" checked="selecting.thumbnail == 0"></td>
            <td><input type="radio" disabled="works[1].id <= 0" checked="selecting.thumbnail == 1"></td>
            <td><input type="text" disabled="works[1].id <= 0 || selecting.thumbnail != 1" x-model="works[1].thumbnail"><img style="width: 15rem;" :src="works[1].thumbnail" :alt="works[1].title"></td>
            <th>Thumbnail</th></tr>
        <tr><th>Rating</th>
            <td><select disabled="works[0].id <= 0 || selecting.rating != 0" x-model="works[0].rating">
                <option value="0">General</option><option value="1">Sensitive</option><option value="2">Explicit</option>
            </select></td>
            <td><input type="radio" disabled="works[0].id <= 0" checked="selecting.rating == 0"></td>
            <td><input type="radio" disabled="works[1].id <= 0" checked="selecting.rating == 1"></td>
            <td><select disabled="works[1].id <= 0 || selecting.rating != 1" x-model="works[1].rating">
                <option value="0">General</option><option value="1">Sensitive</option><option value="2">Explicit</option>
            </select></td>
            <th>Rating</th></tr>
    </tbody></table>
    <input type="submit"/>
</form>
</Section>
