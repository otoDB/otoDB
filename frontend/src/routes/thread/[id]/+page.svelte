<script lang="ts">
	import Pager from '$lib/Pager.svelte';
	import Section from '$lib/Section.svelte';
	import ThreadView from '$lib/ThreadView.svelte';
	import WorkTag from '$lib/WorkTag.svelte';
	import client from '$lib/api.js';
	import { EntityModelRoutes } from '$lib/enums.js';
	import { postCategoryNames } from '$lib/enums/postCategory.js';
	import { entity_to_shorthand, string_link_entities } from '$lib/markdown.js';
	import { m } from '$lib/paraglide/messages.js';
	import { PostCategory } from '$lib/schema.js';
	import { mount, unmount } from 'svelte';

	let { data } = $props();

	const entitiesText = $derived(
		(data.thread?.entities ?? [])
			.map(({ entity, id }) => entity_to_shorthand(entity, id))
			.join('\n')
	);
	const isGardening = $derived(data.thread?.category === PostCategory.Gardening);
	const opPost = $derived(data.posts.find((p) => p.num === 1));

	const postLd = $derived.by(() => {
		if (!data.thread || !opPost) return null;
		return (
			'<script type="application/ld+json">' +
			JSON.stringify({
				'@context': 'https://schema.org',
				'@type': 'DiscussionForumPosting',
				'headline': data.thread.title,
				'text': opPost.body.slice(0, 500),
				'url': `https://otodb.net/thread/${data.thread_id}`,
				'author': {
					'@type': 'Person',
					'name': data.thread.added_by.username,
					'url': `https://otodb.net/profile/${data.thread.added_by.username}`
				},
				'datePublished': opPost.created_at
			}) +
			'</' +
			'script>'
		);
	});

	// Hydrate [[tag]] references (rendered as <otodb-worktag>) in post bodies.
	$effect(() => {
		void data.posts;
		void data.page;
		const tags = Array.from(document.querySelectorAll('.thread-posts otodb-worktag'))
			.filter((e) => e.hasAttribute('slug'))
			.map((el) =>
				client
					.GET('/api/tag/tag', { fetch, params: { query: { tag_slug: el.getAttribute('slug')! } } })
					.then((r) => (r.data ? mount(WorkTag, { target: el, props: { tag: r.data } }) : null))
			);
		return () => {
			tags.forEach((p) => p.then((c) => c && unmount(c)));
		};
	});
</script>

<svelte:head>
	{#if postLd}
		<!-- eslint-disable-next-line svelte/no-at-html-tags -->
		{@html postLd}
	{/if}
</svelte:head>

{#if data.thread}
	<Section>
		{#snippet title()}
			{#each string_link_entities(data.thread.title) as node, i (i)}
				{#if typeof node === 'string'}
					{node}
				{:else}
					<a href={node.url}>{node.text}</a>
				{/if}
			{/each}
		{/snippet}

		<div class="text-otodb-content-fainter mb-6 text-xs">
			<p>
				<a href="/thread?category={data.thread.category}"
					>{postCategoryNames[data.thread.category]()}</a
				>
			</p>
			{#if data.thread.entities?.length}
				<p class="mt-1">
					{m.fine_zany_octopus_trim()}:
					{#each data.thread.entities as { id, entity }, i (i)}
						{#if i > 0},
						{/if}
						{@const link = `/${EntityModelRoutes[entity]}/${id}`}
						<a href={link}>{link}</a>
					{/each}
				</p>
			{/if}
		</div>

		<div class="thread-posts">
			<ThreadView
				thread={data.thread}
				threadId={data.thread_id}
				posts={data.posts}
				user={data.user ?? null}
				refAuthors={data.ref_authors}
				{entitiesText}
				{isGardening}
			/>
		</div>
		<Pager n_count={data.post_count} page={data.page} page_size={data.batch_size} />
	</Section>
{/if}
