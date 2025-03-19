<script lang="ts">
	import { invalidateAll } from '$app/navigation';
	import { base } from '$app/paths';
	import { commentClient, type CommentModels } from './api';

    interface Props {
        comments: any,
        user: App.Locals['user'] | null,
        model: CommentModels,
        pk: number,
    }

    const { comments, user = null, model, pk }: Props = $props();

    let reply_form;

    let reply_to = $state();
    const reply_to_post = (comment) => {
        reply_to = comment;
        reply_form.scrollIntoView();
    }
  
    const post = async (e: SubmitEvent) => {
        e.preventDefault();
        const comment = (new FormData(e.target)).get('comment')?.toString();
        if (comment) {
            await commentClient.POST(model, pk, comment, reply_to?.id ?? 0, user, fetch);
            reply_form.querySelector('textarea[name="comment"]')!.value = '';
            invalidateAll();
            reply_to = null;
        }
    };
</script>

{#snippet comment(data, this_component)}
<div class="comment">
    <h4><a href="{base}/profile/{data.user_name}">{data.user_name}</a> @ {data.time}</h4>
    <p>{data.comment}</p>
    <a href={null} onclick={() => reply_to_post(data)}>Reply</a>
</div>
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
{#if user}
<div bind:this={reply_form} class="border-t-1 p-2">
{#if !reply_to}
<h4>Posting new comment:</h4>
{:else}
<h4>Replying to {reply_to.user_name}: "{reply_to.comment}":</h4>
{/if}
<form onsubmit={post}>
    <textarea name="comment"></textarea>
    <input type="submit">
</form>
</div>
{/if}
</div>

<style>
div.comment {
    background-color: var(--otodb-bg-color);
    padding: .2rem .25rem;
    margin: .5rem 0;
}
</style>
