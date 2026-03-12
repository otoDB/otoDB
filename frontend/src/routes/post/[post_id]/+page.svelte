<script lang="ts">
	import CommentTree from '$lib/CommentTree.svelte';
	import LangSwitch from '$lib/LangSwitch.svelte';
	import Section from '$lib/Section.svelte';
	import WorkTag from '$lib/WorkTag.svelte';
	import client from '$lib/api.js';
	import { EntityModelRoutes, Languages, PostCategories } from '$lib/enums.js';
	import { renderMarkdown } from '$lib/markdown.js';
	import { m } from '$lib/paraglide/messages.js';
	import { getLocale } from '$lib/paraglide/runtime.js';
	import { timeAgo } from '$lib/ui.js';
	import { mount, unmount } from 'svelte';

	let { data } = $props();
	let lang_view = $derived(
		data.post.pages.some((p) => p.lang === Languages[getLocale()])
			? getLocale()
			: Languages[data.post.pages[0].lang]
	);
	let page_object = $derived(data.post.pages.find((p) => p.lang === Languages[lang_view]));
	let page = $derived(
		renderMarkdown(page_object?.page ?? '').replaceAll(
			/&lt;otodb-worktag\s*slug="(.+?)"\s*\/&gt;/g,
			'<otodb-worktag data-slug="$1"></otodb-worktag>'
		)
	);
	$effect(() => {
		if (page) {
			const tags = Array.from(document.querySelectorAll('.post-content otodb-worktag')).map(
				(el) =>
					client
						.GET('/api/tag/tag', {
							fetch,
							params: { query: { tag_slug: el.dataset.slug } }
						})
						.then((r) => mount(WorkTag, { target: el, props: { tag: r.data! } }))
			);
			return () => {
				tags.forEach((p) => p.then(unmount));
			};
		}
	});
</script>

<Section title={data.post.title}>
	<div class="text-otodb-content-fainter mb-6 text-xs">
		<p>
			<a href="/post/search?category={data.post.category}"
				>{PostCategories[data.post.category]()}</a
			>
			{#if data.post.category === 0}
				&middot;
				<a href="#p{data.post_id}"
					><time title={new Date(page_object.modified).toLocaleString()}
						>{timeAgo(page_object.modified)}</time
					></a
				>
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
		availableLanguages={data.post.pages.map((v) => Languages[v.lang])}
		bind:value={lang_view}
	/>
	{#if data.post.category > 0}
		<div class="my-2 grid grid-cols-[8rem_1fr] max-sm:grid-cols-1" id="p{data.post_id}">
			<div
				class="text-otodb-content-fainter flex flex-col gap-1 text-xs max-sm:flex-row max-sm:items-center max-sm:gap-2"
			>
				<a href="/profile/{data.post?.added_by.username}">{data.post?.added_by.username}</a>
				<a href="#p{data.post_id}"
					><time title={new Date(page_object.modified).toLocaleString()}
						>{timeAgo(page_object.modified)}</time
					></a
				>
			</div>
			<div class="px-4 py-2">
				<div
					class="post-content prose prose-neutral prose-sm dark:prose-invert mt-4 max-w-none"
				>
					<!-- eslint-disable-next-line svelte/no-at-html-tags -->
					{@html page}
				</div>
			</div>
		</div>
	{:else}
		<div
			class="post-content prose prose-neutral prose-sm dark:prose-invert mx-auto mt-4 max-w-4xl"
			id="p{data.post_id}"
		>
			<!-- eslint-disable-next-line svelte/no-at-html-tags -->
			{@html page}
		</div>
	{/if}
</Section>

<Section title={m.same_broad_haddock_pinch()}>
	<CommentTree
		comments={data.comments}
		user={data.user ?? null}
		model="post"
		pk={+data.post_id}
	/>
</Section>
