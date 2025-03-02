<script lang="ts">
	import client from "./api";
	import type { components } from "./schema";
	import { debounce } from "./ui";

    let input: string = $state('');
    interface Props {
        value: components['schemas']['WorkSchema'] | null;
        oninput: Function | null;
    }
    let { value = $bindable(null), oninput = null, ...props}: Props = $props();
    
    let suggestions: any[] = $state([]);
    let locked_in = $state(false);

    const search = async () => {
        if (input === '') { suggestions = []; return; }
        const { data } =  await client.GET('/api/work/search', {
            params: { query: { query: input, limit: 10 } }
        });
        if (!data) return;
        suggestions = data.items;
    };

</script>

<svelte:window onclick={() => { suggestions = []; }}></svelte:window>

<span onclick={e => { e.stopPropagation(); }} role="none">
    <input type="text" oninput={debounce(search)} disabled={locked_in} bind:value={input}>
    <input type="number" hidden bind:value={value} {...props}>
    {#if locked_in}
        <img class="w-45" src={value.thumbnail} alt={value.title}>
        <button type="button" onclick={() => { value = null; locked_in = false; if (oninput) oninput(); }}>Change</button>
    {/if}
    <ul class="absolute">
        {#each suggestions as v}
            <li><a href={null} onclick={() => { value = v; input = v.title; suggestions = []; locked_in = true; if (oninput) oninput(); }}>{v.title}</a></li>
        {/each}
    </ul>
</span>

<style>
    ul {
        background-color: var(--otodb-bg-color);
    }
</style>
