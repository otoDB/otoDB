<script lang="ts">
	import { goto, invalidateAll } from '$app/navigation';
	import { page } from '$app/state';
	import client from '$lib/api';
	import { dirtyEnhance } from '$lib/dirty';
	import { hasUserLevel } from '$lib/enums/userLevel';
	import { hydrate, renderMarkdown } from '$lib/markdown';
	import { m } from '$lib/paraglide/messages';
	import { Levels, type components } from '$lib/schema';
	import Time from '$lib/Time.svelte';
	import EditedBy from './EditedBy.svelte';

	type Post = components['schemas']['ThreadPostSchema'];
	type Thread = components['schemas']['ThreadSchema'];

	interface Props {
		thread: Thread;
		posts: Post[];
		user: App.Locals['user'] | null;
		entitiesText: string;
		isGardening: boolean;
	}
	let { thread, posts, user, entitiesText, isGardening }: Props = $props();

	// Derive the targeted post num from URL
	const permalinkNum = (url: URL) => url.pathname.match(/^\/thread\/[^/.]+\.(\d+)$/)?.[1] ?? null;
	const targetNum = $derived(permalinkNum(page.url));

	const hydrateMd = (node: HTMLElement) => hydrate(node, thread.id);

	$effect(() => {
		if (targetNum !== null)
			document.getElementById(`p${targetNum}`)?.scrollIntoView({ block: 'start' });
	});

	let draft = $state('');
	let preview = $state('');
	let previewMode = $state(false);

	let editingNum = $state<number | null>(null);
	let editBody = $state('');
	let editTitle = $state('');
	let editEntities = $state('');
	let editPreview = $state('');
	let editPreviewMode = $state(false);

	const EDIT_WINDOW_MS = 180 * 24 * 60 * 60 * 1000;
	const is_mod = $derived(!!user && hasUserLevel(user?.level, Levels.Mod));
	const can_comment = $derived(
		hasUserLevel(user?.level, Levels.Member) && (!thread.closed_at || is_mod)
	);

	const canEditPost = (p: Post) => {
		if (!user) return false;
		if (is_mod) return true;
		if (p.user.username !== user.username) return false;
		if (p.edited_by && p.edited_by.username !== p.user.username) return false;
		return Date.now() - new Date(p.created_at ?? 0).getTime() < EDIT_WINDOW_MS;
	};

	const quote = (num: number) => {
		const token = `t${thread.id}.${num}: `;
		draft = draft ? `${draft}\n${token}` : token;
		previewMode = false;
		document.getElementById('reply-box')?.focus();
	};

	const togglePreview = () => {
		if (previewMode) {
			previewMode = false;
			return;
		}
		if (!draft.trim()) return;
		preview = renderMarkdown(draft);
		previewMode = true;
	};

	const startEdit = (p: Post) => {
		editingNum = p.num;
		editBody = p.body;
		editPreviewMode = false;
		if (p.num === 1) {
			editTitle = thread.title;
			editEntities = entitiesText;
		}
	};
	const cancelEdit = () => {
		editingNum = null;
	};
	const toggleEditPreview = () => {
		if (editPreviewMode) {
			editPreviewMode = false;
			return;
		}
		if (!editBody.trim()) return;
		editPreview = renderMarkdown(editBody);
		editPreviewMode = true;
	};

	const delete_post = async (num: number) => {
		await client.DELETE('/api/thread/post', {
			fetch,
			params: { query: { thread_id: thread.id, num } }
		});
		await invalidateAll();
	};

	/**
	 * Delegated click handler for post references
	 */
	function postRefNav() {
		return (node: HTMLElement) => {
			const onClick = (event: MouseEvent) => {
				if (
					event.defaultPrevented ||
					event.button !== 0 ||
					event.metaKey ||
					event.ctrlKey ||
					event.shiftKey ||
					event.altKey
				)
					return;
				const anchor = (event.target as HTMLElement).closest('a');
				const href = anchor?.getAttribute('href');
				const match = href?.match(/^\/thread\/(\d+)\.(\d+)$/);
				if (!match) return;
				const [, tid, num] = match;
				// Post in different thread -> let it navigate
				if (tid !== thread.id) return;
				// Post not on this page -> let it navigate
				if (!document.getElementById(`p${num}`)) return;
				event.preventDefault();
				goto(`/thread/${tid}.${num}`);
			};
			node.addEventListener('click', onClick);
			return () => node.removeEventListener('click', onClick);
		};
	}
</script>

{#snippet editor(
	value: () => string,
	set: (v: string) => void,
	previewing: boolean,
	html: string,
	toggle: () => void,
	submitLabel: string,
	onCancel?: () => void
)}
	<div class="reply-main">
		{#if previewing}
			<div class="editor-panel reply-editor">
				<div class="prose prose-neutral prose-sm dark:prose-invert max-w-none" {@attach hydrateMd}>
					<!-- eslint-disable-next-line svelte/no-at-html-tags -->
					{@html html}
				</div>
			</div>
		{:else}
			<textarea
				class="reply-editor block min-h-15 w-full"
				name="body"
				value={value()}
				oninput={(e) => set(e.currentTarget.value)}
			></textarea>
		{/if}
		<div class="reply-actions">
			<button type="button" class="h-15 p-3" onclick={toggle}>
				{previewing ? m.minor_crisp_cobra_list() : m.many_each_wolf_arrive()}
			</button>
			<input type="submit" class="h-15 p-3" value={submitLabel} />
			{#if onCancel}
				<button type="button" class="h-15 p-3" onclick={onCancel}>
					{m.lower_whole_gopher_fulfill()}
				</button>
			{/if}
		</div>
	</div>
{/snippet}

<div {@attach postRefNav()}>
	{#each posts as p (p.num)}
		<div
			class="post grid grid-cols-[8rem_1fr] max-sm:grid-cols-1"
			class:highlighted={`${p.num}` === targetNum}
			id="p{p.num}"
		>
			<div
				class="text-otodb-content-fainter flex flex-col gap-1 text-xs max-sm:flex-row max-sm:items-center max-sm:gap-2"
			>
				<a href="/user/{p.user.username}">{p.user.username}</a>
				<a href="/thread/{thread.id}.{p.num}"
					><Time format="relative" date={p.created_at ?? ''} /></a
				>
				{#if p.edited_at}
					<EditedBy
						date={p.edited_at}
						user={p.edited_by && p.edited_by.username !== p.user.username ? p.edited_by : null}
					/>
				{/if}
			</div>
			<div>
				<span class="text-otodb-content-fainter float-right text-xs leading-none">#{p.num}</span>
				{#if editingNum === p.num}
					{#if p.num === 1}
						<form
							class="edit-form"
							method="POST"
							action="?/editThread"
							use:dirtyEnhance={{
								custom_submit:
									() =>
									async ({ update, result }) => {
										if (result.type === 'success') cancelEdit();
										await update({ reset: false });
									}
							}}
						>
							<table>
								<tbody>
									<tr>
										<th>{m.large_factual_octopus_exhale()}</th>
										<td><input type="text" name="title" required bind:value={editTitle} /></td>
									</tr>
								</tbody>
							</table>
							{#if isGardening}
								<h4>{m.fine_zany_octopus_trim()}</h4>
								<textarea name="entities" bind:value={editEntities}></textarea>
							{/if}
							<input type="hidden" name="post" value={editBody} />
							{@render editor(
								() => editBody,
								(v) => (editBody = v),
								editPreviewMode,
								editPreview,
								toggleEditPreview,
								m.last_late_penguin_bubble(),
								cancelEdit
							)}
						</form>
					{:else}
						<form
							class="edit-form"
							method="POST"
							action="?/editPost"
							use:dirtyEnhance={{
								custom_submit:
									() =>
									async ({ update, result }) => {
										if (result.type === 'success') cancelEdit();
										await update({ reset: false });
									}
							}}
						>
							<input type="hidden" name="num" value={p.num} />
							{@render editor(
								() => editBody,
								(v) => (editBody = v),
								editPreviewMode,
								editPreview,
								toggleEditPreview,
								m.last_late_penguin_bubble(),
								cancelEdit
							)}
						</form>
					{/if}
				{:else}
					<div
						class="prose prose-neutral prose-sm dark:prose-invert max-w-none"
						{@attach (node) => {
							void p.body; // re-hydrate when the body changes (e.g. after an edit)
							return hydrateMd(node);
						}}
					>
						<!-- eslint-disable-next-line svelte/no-at-html-tags -->
						{@html renderMarkdown(p.body)}
					</div>
					<div class="post-actions flex justify-end gap-2 pt-2">
						{#if can_comment}
							<button class="px-2 py-1" onclick={() => quote(p.num)}>
								{m.kind_brief_earthworm_dash()}
							</button>
						{/if}
						{#if canEditPost(p)}
							<button class="px-2 py-1" onclick={() => startEdit(p)}>
								{m.minor_crisp_cobra_list()}
							</button>
						{/if}
						{#if p.num !== 1 && user && (is_mod || p.user.username === user.username)}
							<button class="px-2 py-1" onclick={() => delete_post(p.num)}>
								{m.even_alert_grebe_taste()}
							</button>
						{/if}
					</div>
				{/if}
			</div>
		</div>
	{/each}
</div>

{#if can_comment}
	<h4 class="mt-4 mb-2">{m.mild_loud_shad_enchant({ type: m.weak_safe_cat_mix(), name: '' })}</h4>
	<form
		class="reply-form"
		method="POST"
		action="?/reply"
		use:dirtyEnhance={{
			custom_submit:
				() =>
				async ({ update, result }) => {
					await update();
					if (result.type === 'success') await goto(`/thread/${thread.id}.${result.data}`);
				}
		}}
	>
		<div class="reply-main">
			{#if previewMode}
				<div class="editor-panel reply-editor">
					<div
						class="prose prose-neutral prose-sm dark:prose-invert max-w-none"
						{@attach hydrateMd}
					>
						<!-- eslint-disable-next-line svelte/no-at-html-tags -->
						{@html preview}
					</div>
				</div>
			{:else}
				<textarea
					id="reply-box"
					class="reply-editor block min-h-15 w-full"
					name="body"
					bind:value={draft}
				></textarea>
			{/if}
			<div class="reply-actions">
				<button type="button" class="h-15 p-3" onclick={togglePreview}>
					{previewMode ? m.minor_crisp_cobra_list() : m.many_each_wolf_arrive()}
				</button>
				<input type="submit" class="h-15 p-3" value={m.inner_solid_toad_zap()} />
			</div>
		</div>
	</form>
{/if}

<style>
	div.post {
		background-color: var(--otodb-color-bg-primary);
		padding: 0.5rem 1rem 0.8rem 1rem;
		margin: 1.5rem 0;
		& .post-actions {
			opacity: 0;
		}
		&:hover .post-actions {
			opacity: 1;
		}
		&:target,
		&.highlighted {
			box-shadow: -4px 0 0 var(--otodb-color-content-faint);
		}
	}
	form.reply-form,
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
	textarea {
		field-sizing: content;
	}
</style>
