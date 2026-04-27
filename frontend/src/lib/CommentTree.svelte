<script lang="ts">
	import { enhance } from '$app/forms';
	import { invalidateAll } from '$app/navigation';
	import client from '$lib/api';
	import { makeCommentTree } from '$lib/CommentTree/makeCommentTree';
	import { hasUserLevel } from '$lib/enums/userLevel';
	import { renderMarkdown } from '$lib/markdown';
	import { m } from '$lib/paraglide/messages';
	import { Levels, ModelsWithComments } from '$lib/schema';
	import Time from '$lib/Time.svelte';
	import EditedBy from './EditedBy.svelte';

	interface Props {
		user: App.Locals['user'] | null;
		model: ModelsWithComments;
		pk: string;
		comments: Parameters<typeof makeCommentTree>[0];
	}

	const { comments, user = null, model, pk }: Props = $props();

	const tree = $derived(makeCommentTree(comments) ?? []);
	let drafts = $state<Record<string, string>>({});
	let previews = $state<Record<string, string>>({});
	let previewMode = $state<Record<string, boolean>>({});
	let editingId = $state<string | null>(null);
	let editingText = $state('');
	let editPreview = $state('');
	let editPreviewMode = $state(false);

	const EDIT_WINDOW_MS = 180 * 24 * 60 * 60 * 1000;

	const togglePreview = (reply_to: string) => {
		if (previewMode[reply_to]) {
			previewMode[reply_to] = false;
			return;
		}

		const comment = drafts[reply_to]?.trim();
		if (!comment) return;

		previews[reply_to] = renderMarkdown(comment);
		previewMode[reply_to] = true;
	};

	const toggleEditPreview = () => {
		if (editPreviewMode) {
			editPreviewMode = false;
			return;
		}

		const text = editingText.trim();
		if (!text) return;

		editPreview = renderMarkdown(text);
		editPreviewMode = true;
	};

	const startEdit = (id: string, currentText: string) => {
		editingId = id;
		editingText = currentText;
		editPreviewMode = false;
	};

	const cancelEdit = () => {
		editingId = null;
		editingText = '';
		editPreviewMode = false;
	};

	const can_comment = $derived(hasUserLevel(user?.level, Levels.Member));
	const is_admin = $derived(!!user && hasUserLevel(user?.level, Levels.Admin));

	const canEdit = (data: ReturnType<typeof makeCommentTree>[number]) => {
		if (!user) return false;
		if (is_admin) return true;
		if (data.user.username !== user.username) return false;
		// Lock: if edited by a different user (admin), original author can no longer edit
		if (data.edited_by && data.edited_by.username !== data.user.username) return false;
		return Date.now() - data.time.getTime() < EDIT_WINDOW_MS;
	};

	const delete_comment = async (comment_id: string) => {
		await client.DELETE('/api/comment/comment', {
			fetch,
			params: { query: { comment_id, model, pk } }
		});
		invalidateAll();
	};
</script>

{#snippet reply(reply_to: string)}
	<form
		class="reply-form gap-2"
		method="POST"
		action="/comments?/create"
		use:enhance={() => {
			return async ({ update, result }) => {
				if (result.type === 'success') {
					const comment_text = drafts[reply_to]?.trim();
					if (comment_text) {
						document
							.querySelectorAll('.reply-toggle')
							.forEach((e) => ((e as HTMLInputElement).checked = false));
						drafts[reply_to] = '';
						previews[reply_to] = '';
						previewMode[reply_to] = false;
					}
				}
				await update({ reset: false });
			};
		}}
	>
		<input type="text" name="model" hidden value={model} />
		<input type="text" name="pk" hidden value={pk} />
		<input type="text" name="reply_to" hidden value={reply_to} />
		<div class="reply-main">
			{#if previewMode[reply_to]}
				<div class="editor-panel reply-editor">
					<div class="prose prose-neutral prose-sm dark:prose-invert max-w-none">
						<!-- eslint-disable-next-line svelte/no-at-html-tags -->
						{@html previews[reply_to]}
					</div>
				</div>
			{:else}
				<textarea
					class="reply-editor block min-h-15 w-full"
					name="comment"
					bind:value={drafts[reply_to]}
				></textarea>
			{/if}
			<div class="reply-actions">
				<button type="button" class="h-15 p-3" onclick={() => togglePreview(reply_to)}>
					{previewMode[reply_to] ? m.minor_crisp_cobra_list() : m.many_each_wolf_arrive()}
				</button>
				<input type="submit" class="h-15 p-3" value={m.inner_solid_toad_zap()} />
			</div>
		</div>
	</form>
{/snippet}

{#snippet comment(data: ReturnType<typeof makeCommentTree>[number], depth: number)}
	<div class="comment grid grid-cols-[8rem_1fr] max-sm:grid-cols-1" id="c{data.id}">
		<div
			class="text-otodb-content-fainter flex flex-col gap-1 text-xs max-sm:flex-row max-sm:items-center max-sm:gap-2"
		>
			<a href="/profile/{data.user.username}">{data.user.username}</a>
			<a href="#c{data.id}"><Time format="relative" date={data.time} /></a>
			{#if data.edited_at}
				<EditedBy
					date={data.edited_at}
					user={data.edited_by && data.edited_by.username !== data.user.username
						? data.edited_by
						: null}
				/>
			{/if}
		</div>
		<div>
			<span class="text-otodb-content-fainter float-right text-xs leading-none"
				>#{data.index}</span
			>
			{#if editingId === data.id}
				<form
					class="edit-form"
					method="POST"
					action="/comments?/edit"
					use:enhance={() => {
						return async ({ update, result }) => {
							if (result.type === 'success') {
								cancelEdit();
							}
							await update({ reset: false });
						};
					}}
				>
					<input type="hidden" name="comment_id" value={data.id} />
					<div class="reply-main">
						{#if editPreviewMode}
							<div class="editor-panel reply-editor">
								<div
									class="prose prose-neutral prose-sm dark:prose-invert max-w-none"
								>
									<!-- eslint-disable-next-line svelte/no-at-html-tags -->
									{@html editPreview}
								</div>
							</div>
						{:else}
							<textarea
								class="reply-editor block min-h-15 w-full"
								name="comment"
								bind:value={editingText}
							></textarea>
						{/if}
						<div class="reply-actions">
							<button type="button" class="h-15 p-3" onclick={toggleEditPreview}>
								{editPreviewMode
									? m.minor_crisp_cobra_list()
									: m.many_each_wolf_arrive()}
							</button>
							<input
								type="submit"
								class="h-15 p-3"
								value={m.last_late_penguin_bubble()}
							/>
							<button type="button" class="h-15 p-3" onclick={cancelEdit}>
								{m.lower_whole_gopher_fulfill()}
							</button>
						</div>
					</div>
				</form>
			{:else}
				<div class="prose prose-neutral prose-sm dark:prose-invert max-w-none">
					<!-- eslint-disable-next-line svelte/no-at-html-tags -->
					{@html renderMarkdown(data.comment)}
				</div>
			{/if}
			{#if editingId === null}
				<div class="comment-actions flex justify-end gap-2 pt-2">
					{#if can_comment}
						<label class="cursor-pointer px-2 py-1">
							{m.kind_brief_earthworm_dash()}
							<input type="checkbox" class="reply-toggle hidden" value={false} />
						</label>
					{/if}
					{#if canEdit(data)}
						<button class="px-2 py-1" onclick={() => startEdit(data.id, data.comment)}>
							{m.minor_crisp_cobra_list()}
						</button>
					{/if}
					{#if user && (hasUserLevel(user?.level, Levels.Admin) || data.user.username === user.username)}
						<button class="px-2 py-1" onclick={() => delete_comment(data.id)}
							>{m.even_alert_grebe_taste()}</button
						>
					{/if}
				</div>
			{/if}
		</div>
	</div>
	<div class="border-otodb-content-fainter ml-2 border-l-2 pl-3">
		{@render reply(data.id)}
		{#each data.children as child, i (i)}
			{@render comment(child, depth + 1)}
		{/each}
	</div>
{/snippet}

<div>
	{#if tree.length}
		{#each tree as c, i (i)}
			{@render comment(c, 0)}
		{/each}
	{:else}
		{m.new_basic_dove_love()}
	{/if}
	{#if can_comment}
		<h4 class="mb-2">{m.mild_loud_shad_enchant({ type: m.weak_safe_cat_mix(), name: '' })}</h4>
		{@render reply('0')}
	{/if}
</div>

<style>
	form.reply-form {
		display: none;
		flex-direction: column;
		width: 100%;
	}
	h4 + form.reply-form {
		display: flex;
	}
	form.edit-form {
		display: flex;
		flex-direction: column;
		width: 100%;
	}
	div.reply-main {
		display: flex;
		width: 100%;
		align-items: flex-start;
		gap: 0.25rem;
	}
	.reply-editor {
		flex: 1 1 auto;
	}
	div.editor-panel {
		width: 100%;
		min-height: 3.75rem;
		padding: 0.5rem;
		border: 1px solid var(--otodb-color-content-faint, #666);
		background-color: var(--otodb-color-bg-primary);
	}
	div.reply-actions {
		display: flex;
		flex-direction: row;
		gap: 0.25rem;
		align-items: flex-start;
		margin-left: auto;
	}
	div.comment {
		background-color: var(--otodb-color-bg-primary);
		padding: 0.5rem 1rem 0.8rem 1rem;
		margin: 1.5rem 0;
		& .comment-actions {
			opacity: 0;
		}
		&:hover .comment-actions {
			opacity: 1;
		}
		&:target {
			box-shadow: -4px 0 0 var(--otodb-color-content-faint);
		}
		&:has(input.reply-toggle:checked) .comment-actions {
			opacity: 1;
		}
		&:has(input.reply-toggle:checked) + div > form.reply-form {
			display: flex;
		}
	}
	textarea {
		field-sizing: content;
	}
</style>
