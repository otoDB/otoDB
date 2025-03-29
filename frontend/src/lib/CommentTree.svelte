<script lang="ts">
	import { invalidateAll } from '$app/navigation';
	import { commentClient, type CommentModels } from './api';

	interface Props {
		comments: any;
		// eslint-disable-next-line no-undef
		user: App.Locals['user'] | null;
		model: CommentModels;
		pk: number;
	}

	const { comments, user = null, model, pk }: Props = $props();

	const post = (reply_to: number) => async (e: SubmitEvent) => {
		e.preventDefault();
		const comment = new FormData(e.target).get('comment')?.toString();
		if (comment) {
			await commentClient.POST(model, pk, comment, reply_to, user, fetch);
			invalidateAll();
		}
	};
</script>

{#snippet reply(reply_to: number)}
	<form onsubmit={post(reply_to)}>
		<textarea class="block" name="comment"></textarea>
		<input type="submit" />
	</form>
{/snippet}

{#snippet comment(data, this_component)}
	<div class="comment">
		<h4><a href="/profile/{data.user_name}">{data.user_name}</a> @ {data.time}</h4>
		<p>{data.comment}</p>
		{#if user}
			<label class="reply">
				Reply
				<input type="checkbox" />
				{@render reply(data.id)}
			</label>
		{/if}
	</div>
	{#if data.children?.length}
		<div class="ml-3">
			<!-- eslint-disable-next-line svelte/require-each-key -->
			{#each data.children as child}
				{@render this_component(child, this_component)}
			{/each}
		</div>
	{/if}
{/snippet}

<div>
	{#if comments.length}
		<!-- eslint-disable-next-line svelte/require-each-key -->
		{#each comments as c}
			{@render comment(c, comment)}
		{/each}
	{/if}
	{#if user}
		<h4>Post a new comment:</h4>
		{@render reply(0)}
	{/if}
</div>

<style>
	div.comment {
		background-color: var(--otodb-bg-color);
		padding: 0.2rem 0.25rem;
		margin: 0.5rem 0;
	}
	label.reply {
		border: 1px solid var(--otodb-faint-content);
		> input {
			display: none;
			& + form {
				background-color: var(--otodb-faint-bg);
				display: none;
				position: absolute;
				padding: 0.1rem;
				border: 1px solid var(--otodb-faint-content);
			}
			&:checked + form {
				display: unset;
			}
		}
	}
</style>
