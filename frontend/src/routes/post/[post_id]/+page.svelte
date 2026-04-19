<script lang="ts">
	import { enhance } from '$app/forms';
	import CommentTree from '$lib/CommentTree.svelte';
	import EditedBy from '$lib/EditedBy.svelte';
	import LangSwitch from '$lib/LangSwitch.svelte';
	import Section from '$lib/Section.svelte';
	import TimeAgo from '$lib/TimeAgo.svelte';
	import WorkTag from '$lib/WorkTag.svelte';
	import client from '$lib/api.js';
	import { EntityModelRoutes } from '$lib/enums.js';
	import { languages, resolveLanguageKeyById } from '$lib/enums/language.js';
	import { postCategoryNames } from '$lib/enums/postCategory.js';
	import { hasUserLevel } from '$lib/enums/userLevel.js';
	import { entity_to_shorthand, get_entity, renderMarkdown } from '$lib/markdown.js';
	import { m } from '$lib/paraglide/messages.js';
	import { getLocale } from '$lib/paraglide/runtime.js';
	import { Levels, PathsApiCommentCommentDeleteParametersQueryModel } from '$lib/schema.js';
	import { mount, unmount } from 'svelte';

	let { data } = $props();

	let lang_view = $derived(
		data.post.pages.some((p) => p.lang === languages[getLocale()].id)
			? getLocale()
			: resolveLanguageKeyById(data.post.pages[0].lang)
	);
	let page_object = $derived(data.post.pages.find((p) => p.lang === languages[lang_view].id)!);
	let page = $derived(renderMarkdown(page_object?.page ?? ''));

	const postLd = $derived.by(() => {
		const pageObj = data.post.pages.find((p) => p.lang === languages[lang_view].id);
		if (!pageObj) return null;
		return (
			'<script type="application/ld+json">' +
			JSON.stringify({
				'@context': 'https://schema.org',
				'@type': 'DiscussionForumPosting',
				'headline': data.post.title,
				'text': pageObj.page.slice(0, 500),
				'url': `https://otodb.net/post/${data.post_id}`,
				'author': {
					'@type': 'Person',
					'name': data.post.added_by.username,
					'url': `https://otodb.net/profile/${data.post.added_by.username}`
				},
				'datePublished': pageObj.modified,
				...(data.post.edited_at ? { dateModified: data.post.edited_at } : {})
			}) +
			'</' +
			'script>'
		);
	});
	$effect(() => {
		if (page) {
			const tags = Array.from(document.querySelectorAll('.post-content otodb-worktag'))
				.filter((e) => e.hasAttribute('slug'))
				.map((el) =>
					client
						.GET('/api/tag/tag', {
							fetch,
							params: {
								query: {
									tag_slug: el.getAttribute('slug')!
								}
							}
						})
						.then((r) => mount(WorkTag, { target: el, props: { tag: r.data! } }))
				);
			return () => {
				tags.forEach((p) => p.then(unmount));
			};
		}
	});

	let isEditing = $state(false);
	let editTitle = $state('');
	let editContent = $state('');
	let editEntities = $state('');
	let editPreviewHtml = $derived(renderMarkdown(editContent));
	let editEntitiesParsed = $derived(
		editEntities
			.split('\n')
			.map(get_entity)
			.filter((x) => !!x)
	);

	const is_admin = $derived(hasUserLevel(data.user?.level, Levels.Admin));
	const editedByOther =
		data.post.edited_by && data.post.edited_by.username !== data.post.added_by.username;
	const canEdit =
		data.user &&
		(is_admin || (data.post.added_by.username === data.user.username && !editedByOther));

	const startEdit = () => {
		editTitle = data.post.title;
		editContent = page_object?.page ?? '';
		editEntities = (data.post.entities ?? [])
			.map(({ entity, id }) => entity_to_shorthand(entity, id))
			.join('\n');
		isEditing = true;
	};

	const cancelEdit = () => {
		isEditing = false;
	};
</script>

<svelte:head>
	{#if postLd}
		<!-- eslint-disable-next-line svelte/no-at-html-tags -->
		{@html postLd}
	{/if}
</svelte:head>

<Section title={isEditing ? '' : data.post.title}>
	{#if isEditing}
		<form
			method="POST"
			action="?/edit"
			use:enhance={() => {
				return async ({ update, result }) => {
					if (result.type === 'success') {
						isEditing = false;
					}
					await update({ reset: false });
				};
			}}
		>
			<input type="hidden" name="lang" value={lang_view} />
			<table>
				<tbody>
					<tr>
						<th>{m.large_factual_octopus_exhale()}</th>
						<td><input type="text" name="title" required bind:value={editTitle} /></td>
					</tr>
				</tbody>
			</table>
			{#if data.post.category === 3}
				<h4>{m.fine_zany_octopus_trim()}</h4>
				<textarea name="entities" bind:value={editEntities}></textarea>
				<ul class="inline-block">
					{#each editEntitiesParsed as { entity, id }, i (i)}
						{@const link = `/${EntityModelRoutes[entity]}/${id}`}
						<li><a href={link}>{link}</a></li>
					{/each}
				</ul>
			{/if}
			<div class="grid grid-cols-2 gap-3">
				<textarea rows="10" bind:value={editContent} class="w-full" name="post" required
				></textarea>
				<div class="prose prose-neutral prose-sm dark:prose-invert">
					<!-- eslint-disable-next-line svelte/no-at-html-tags -->
					{@html editPreviewHtml}
				</div>
			</div>
			<div class="mt-2 flex gap-2">
				<input type="submit" value={m.last_late_penguin_bubble()} />
				<button type="button" onclick={cancelEdit}>{m.lower_whole_gopher_fulfill()}</button>
			</div>
		</form>
	{:else}
		<div class="text-otodb-content-fainter mb-6 text-xs">
			<p>
				<a href="/post?category={data.post.category}"
					>{postCategoryNames[data.post.category]()}</a
				>
				{#if data.post.category === 0}
					&middot;
					<a href="#p{data.post_id}"><TimeAgo date={page_object.modified} /></a>
				{/if}
			</p>
			{#if data.post.entities?.length}
				<p class="mt-1">
					{m.fine_zany_octopus_trim()}:
					{#each data.post.entities as { id, entity }, i (i)}
						{#if i > 0},
						{/if}
						{@const link = `/${EntityModelRoutes[entity]}/${id}`}
						<a href={link}>{link}</a>
					{/each}
				</p>
			{/if}
		</div>
		<LangSwitch
			availableLanguages={data.post.pages.map((v) => resolveLanguageKeyById(v.lang))}
			bind:value={lang_view}
		/>
		{#if data.post.category > 0}
			<div class="op-post grid grid-cols-[8rem_1fr] max-sm:grid-cols-1" id="p{data.post_id}">
				<div
					class="text-otodb-content-fainter flex flex-col gap-1 text-xs max-sm:flex-row max-sm:items-center max-sm:gap-2"
				>
					<a href="/profile/{data.post?.added_by.username}"
						>{data.post?.added_by.username}</a
					>
					<a href="#p{data.post_id}"><TimeAgo date={page_object.modified} /></a>
					{#if data.post.edited_at && data.post.edited_by}
						<EditedBy
							date={data.post.edited_at}
							user={editedByOther ? data.post.edited_by : null}
						/>
					{/if}
				</div>
				<div class="px-4 py-2">
					<div
						class="post-content prose prose-neutral prose-sm dark:prose-invert mt-4 max-w-none"
					>
						<!-- eslint-disable-next-line svelte/no-at-html-tags -->
						{@html page}
					</div>
					{#if canEdit}
						<div class="post-actions flex justify-end gap-2 pt-2">
							<button class="px-2 py-1" onclick={startEdit}>Edit</button>
						</div>
					{/if}
				</div>
			</div>
		{:else}
			<div
				class="post-content prose prose-neutral prose-sm dark:prose-invert mx-auto mt-4 max-w-4xl"
				id="p{data.post_id}"
			>
				<!-- eslint-disable-next-line svelte/no-at-html-tags -->
				{@html page}
				{#if canEdit}
					<div class="post-actions flex justify-end gap-2 pt-2">
						<button class="px-2 py-1" onclick={startEdit}>Edit</button>
					</div>
				{/if}
			</div>
		{/if}
	{/if}
</Section>

<Section title={m.same_broad_haddock_pinch()}>
	<CommentTree
		comments={data.comments}
		user={data.user ?? null}
		model={PathsApiCommentCommentDeleteParametersQueryModel.post}
		pk={+data.post_id}
	/>
</Section>

<style>
	div.op-post {
		background-color: var(--otodb-color-bg-primary);
		padding: 0.5rem 1rem 0.8rem 1rem;
		margin: 0.5rem 0;
		&:target {
			box-shadow: -4px 0 0 var(--otodb-color-content-faint);
		}
		& .post-actions {
			opacity: 0;
		}
		&:hover .post-actions {
			opacity: 1;
		}
	}
</style>
