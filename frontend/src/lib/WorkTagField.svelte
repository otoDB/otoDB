<script lang="ts">
	import client from "./api";
	import { clickOutside, debounce } from "./ui";

    interface Props {
        value: string;
    }
    let { value = $bindable(''), ...props}: Props = $props();
    
    let suggestions: string[] = $state([]);

    const search = async () => {
        if (value === '') { suggestions = []; return; }
        const { data } =  await client.GET('/api/tag/search', {
            params: { query: { query: value, limit: 10 } }
        });
        if (!data) return;
        suggestions = data.items.map(tag => tag.slug);
    };

</script>

<span role="none">
    <input type="text" oninput={debounce(search)} bind:value={value} {...props}>
    <ul class="absolute" use:clickOutside onOutclick={() => { suggestions = []; }}>
        {#each suggestions as t}
            <li><a href={null} onclick={() => { value = t; suggestions = []; }}>{t}</a></li>
        {/each}
    </ul>
</span>

<style>
    ul {
        background-color: var(--otodb-bg-color);
    }
</style>
