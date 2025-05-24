<script lang="ts">
	import { invalidateAll } from '$app/navigation';
	import { commentClient, type CommentModels } from './api';
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

	const post = (reply_to: number) => async (e: SubmitEvent) => {
		e.preventDefault();
		const comment = new FormData(e.target).get('comment')?.toString();
		if (comment) {
			await commentClient.POST(model, pk, comment, reply_to, user, fetch);
			document.querySelectorAll('.reply-checkbox').forEach((e) => (e.checked = false));
			invalidateAll();
		}
	};

	const can_comment = user && user.level >= UserLevel.MEMBER;
</script>

{#snippet reply(reply_to: number)}
	<form onsubmit={post(reply_to)}>
		<textarea class="block w-full" name="comment"></textarea>
		<input type="submit" value={m.inner_solid_toad_zap()} />
	</form>
{/snippet}

{#snippet comment(data, this_component, depth: number)}
	<div class="comment">
		<h4><a href="/profile/{data.user_name}">{data.user_name}</a> @ {data.time}</h4>
		<p>{data.comment}</p>
		<!-- TODO: design decision -- allow deeper nested comments? check COMMENTS_XTD_MAX_THREAD_LEVEL on backend -->
		{#if can_comment && depth < 3}
			<label class="reply">
				{m.kind_brief_earthworm_dash()}
				<input type="checkbox" class="reply-checkbox" />
				{@render reply(data.id)}
			</label>
		{/if}
	</div>
	{#if data.children?.length}
		<div class="ml-3">
			{#each data.children as child, i (i)}
				{@render this_component(child, this_component, depth + 1)}
			{/each}
		</div>
	{/if}
{/snippet}

<div>
	{#if comments.length}
		{#each comments as c, i (i)}
			{@render comment(c, comment, 0)}
		{/each}
	{:else}
		{m.new_basic_dove_love()}
	{/if}
	{#if can_comment}
		<h4>{m.mild_loud_shad_enchant({ type: m.weak_safe_cat_mix(), name: '' })}</h4>
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
