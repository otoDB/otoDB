<script lang="ts">
	import { invalidateAll } from '$app/navigation';
	import client from '$lib/api';
	import { dirtyClick } from '$lib/dirty';
	import { hasUserLevel } from '$lib/enums/userLevel.js';
	import Banner from '$lib/Banner.svelte';
	import Pager from '$lib/Pager.svelte';
	import Section from '$lib/Section.svelte';
	import ThreadView from '$lib/ThreadView.svelte';
	import { EntityModelRoutes } from '$lib/enums.js';
	import { postCategoryNames } from '$lib/enums/postCategory.js';
	import { entity_to_shorthand, string_link_entities } from '$lib/markdown.js';
	import { m } from '$lib/paraglide/messages.js';
	import { Levels, PostCategory } from '$lib/schema.js';

	let { data } = $props();

	const is_mod = $derived(!!data.user && hasUserLevel(data.user.level, Levels.Mod));

	const can_close = $derived(is_mod && !data.thread?.closed_at);
	const close_thread = async () => {
		await client.PUT('/api/thread/close', {
			fetch,
			params: { query: { thread_id: data.thread.id } }
		});
		await invalidateAll();
	};

	const op_edited_by_another = $derived(
		!!data.thread?.edited_by && data.thread.edited_by.username !== data.thread.added_by.username
	);
	const can_reopen = $derived(
		!!data.thread?.closed_at &&
			(is_mod ||
				(!!data.user &&
					data.user.username === data.thread?.added_by.username &&
					!op_edited_by_another))
	);
	const reopen_thread = async () => {
		await client.PUT('/api/thread/reopen', {
			fetch,
			params: { query: { thread_id: data.thread.id } }
		});
		await invalidateAll();
	};

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
				'url': `https://otodb.net/thread/${data.thread.id}`,
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
</script>

<svelte:head>
	<meta name="robots" content="noindex" />
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

		{#if data.thread.closed_at}
			<Banner variant="info" title={m.any_fair_gull_treat()} />
		{/if}

		<div class="text-otodb-content-fainter mb-6 flex items-center gap-4 text-xs">
			<div class="flex grow items-center space-x-2">
				<p>
					<a href="/thread?category={data.thread.category}"
						>{postCategoryNames[data.thread.category]()}</a
					>
				</p>
				{#if data.thread.entities?.length}
					<p>
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
			<div class="shrink-0">
				{#if can_close}
					<button type="button" class="px-3 py-1" {@attach dirtyClick(close_thread)}>
						{m.mean_watery_pig_walk()}
					</button>
				{/if}
				{#if can_reopen}
					<button type="button" class="px-3 py-1" {@attach dirtyClick(reopen_thread)}>
						{m.elegant_each_ant_approve()}
					</button>
				{/if}
			</div>
		</div>

		<div class="thread-posts">
			<ThreadView
				thread={data.thread}
				posts={data.posts}
				user={data.user ?? null}
				{entitiesText}
				{isGardening}
			/>
		</div>
		<Pager
			n_count={data.post_count}
			page_size={data.batch_size}
			base_url="/thread/{data.thread.id}"
		/>
	</Section>
{/if}
