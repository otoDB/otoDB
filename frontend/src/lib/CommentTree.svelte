<script lang="ts">
	import { invalidateAll } from '$app/navigation';
	import client, { makeCommentTree, type CommentModels } from './api';
	import { UserLevel } from './enums';
	import { m } from './paraglide/messages';

	interface Props {
		comments: any;
		// eslint-disable-next-line no-undef
		user: App.Locals['user'] | null;
		model: CommentModels;
		pk: number;
	}

	const { comments, user = null, model, pk }: Props = $props();

	const tree = $derived(makeCommentTree(comments));

	const post = (reply_to: number) => async (e: SubmitEvent) => {
		e.preventDefault();
		const comment = new FormData(e.target).get('comment')?.toString();
		if (comment) {
			await client.POST('/api/comment/comment', {
				params: { query: { model, pk, comment, parent_id: reply_to }, fetch }
			});
			document.querySelectorAll('.reply-toggle').forEach((e) => (e.checked = false));
			e.target.querySelector('textarea').value = '';
			invalidateAll();
		}
	};

	const can_comment = user && user.level >= UserLevel.MEMBER;

	const delete_comment = async (comment_id) => {
		await client.DELETE('/api/comment/comment', {
			fetch,
			params: { query: { comment_id, model, pk } }
		});
		invalidateAll();
	};
</script>

{#snippet reply(reply_to: number)}
	<form onsubmit={post(reply_to)} class="reply-form align-start gap-1">
		<textarea class="block min-h-15 w-full" name="comment"></textarea>
		<input type="submit" class="h-15 p-3" value={m.inner_solid_toad_zap()} />
	</form>
{/snippet}

{#snippet comment(data, this_component, depth: number)}
	<div class="comment">
		<!-- TODO: design decision -- allow deeper nested comments? check COMMENTS_XTD_MAX_THREAD_LEVEL on backend -->
		<div class="float-right flex gap-2">
			{#if can_comment && depth < 3}
				<label class="bg-otodb-bg-primary hover:bg-otodb-bg-fainter border-1">
					{m.kind_brief_earthworm_dash()}
					<input type="checkbox" class="reply-toggle hidden" value={false} />
				</label>
			{/if}
			{#if user && (user.level >= UserLevel.ADMIN || data.user.username === user.username)}
				<button onclick={() => delete_comment(data.id)}>{m.even_alert_grebe_taste()}</button
				>
			{/if}
		</div>
		<div class="mb-3 flex items-end gap-2 align-bottom">
			<p>#{data.index}</p>
			<h4><a href="/profile/{data.user.username}">{data.user.username}</a></h4>
			<address class="text-otodb-content-fainter text-xs">
				{data.time.toLocaleString()}
			</address>
		</div>
		<p>{data.comment}</p>
	</div>
	<div class="ml-3">
		{@render reply(data.id)}
		{#each data.children as child, i (i)}
			{@render this_component(child, this_component, depth + 1)}
		{/each}
	</div>
{/snippet}

<div>
	{#if tree.length}
		{#each tree as c, i (i)}
			{@render comment(c, comment, 0)}
		{/each}
	{:else}
		{m.new_basic_dove_love()}
	{/if}
	{#if can_comment}
		<h4 class="mb-2">{m.mild_loud_shad_enchant({ type: m.weak_safe_cat_mix(), name: '' })}</h4>
		{@render reply(0)}
	{/if}
</div>

<style>
	form.reply-form {
		display: none;
	}
	h4 + form.reply-form {
		display: flex;
	}
	div.comment {
		background-color: var(--otodb-color-bg-primary);
		padding: 0.5rem 1rem 0.8rem 1rem;
		margin: 0.5rem 0;
		&:has(input.reply-toggle:checked) + div > form.reply-form {
			display: flex;
		}
	}
</style>
