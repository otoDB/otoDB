<script lang="ts">
	import Section from "$lib/Section.svelte";
	import type { PageProps } from "./$types";
    import { m } from '$lib/paraglide/messages.js';
	import WorkTagsField from "$lib/WorkTagsField.svelte";
	import client from "$lib/api";
	import { goto } from "$app/navigation";
	import { base } from "$app/paths";

    let tags = $state([]), selected = $state('');

    const submit = async () => {
        const { error } = await client.POST('/api/tag/alias', { fetch, params: { query: { into_tag: selected } }, body: tags});
        if (!error)
            goto(`${base}/tag/${selected}`);
    };
</script>

<svelte:head>
    <title>Alias Tags</title>
</svelte:head>

<Section title="Alias Tags">
Start by giving a space-delimited list of tags.
<WorkTagsField class="w-full" bind:value={tags}/>
{#if tags.length}
into
<form onsubmit={submit}>
    <select name="" bind:value={selected}>
        {#each tags as t}
        <option value={t}>{t}</option>
        {/each}
    </select>
    <input type="submit" disabled={selected === ''}>
</form>
{/if}
</Section>
