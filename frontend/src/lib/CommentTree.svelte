<script lang="ts">
	import { base } from '$app/paths';

    const { comments } = $props();
</script>

{#snippet comment(data, this_component)}
    <h4><a href="{base}/profile/{data.user_name}">{data.user_name}</a> @ {data.time}</h4>
    <p>{data.comment}</p>
    {#if data.children?.length}
    <div class="ml-3">
        {#each data.children as child}
            {@render this_component(child, this_component)}
        {/each}
    </div>
    {/if}
{/snippet}

<div>
{#if comments.length}
    {#each comments as c}
    {@render comment(c, comment)}
    {/each}
{:else}
    <h4>No comments!</h4>    
{/if}
</div>
