<script lang="ts">
	import client from '$lib/api';
	import CommentTree from '$lib/CommentTree.svelte';
	import { PlatformNames, WorkOriginNames } from '$lib/enums';
	import { isSOV, isSVO } from '$lib/enums/language.js';
	import ExternalEmbed from '$lib/ExternalEmbed.svelte';
	import LoadMoreButton from '$lib/LoadMoreButton.svelte';
	import Pager from '$lib/Pager.svelte';
	import { m } from '$lib/paraglide/messages.js';
	import { getLocale } from '$lib/paraglide/runtime';
	import { PathsApiCommentCommentDeleteParametersQueryModel } from '$lib/schema.js';
	import Section from '$lib/Section.svelte';
	import WorkCard from '$lib/WorkCard.svelte';
	import WorkThumbnail from '$lib/WorkThumbnail.svelte';
	import type { ComponentProps } from 'svelte';

	let { data } = $props();

	let pending_items = $derived(data.pending_items!.items);

	let current = $state(0);
	let select = $state(-1);
	let sources: ComponentProps<typeof ExternalEmbed>['src'][] | undefined = $state();

	$effect(() => {
		if (data.entries.items[current]) {
			client
				.GET('/api/work/sources', {
					fetch,
					params: { query: { work_id: data.entries.items[current].work.id } }
				})
				.then(({ data }) => {
					sources = data;
					select = 0;
				});
		}
	});
</script>

<Section title={data.list.name} type={m.stale_loose_squid_cut()} menuLinks={data.links}>
	<h3>
		{#if isSVO(getLocale())}
			{m.curly_safe_lynx_fond()}
		{/if}
		<a href="/profile/{data.list?.author.username}">{data.list?.author.username}</a>
		{#if isSOV(getLocale())}
			{m.curly_safe_lynx_fond()}
		{/if}
	</h3>
	{#if data.list.upstream}
		<address><a href={data.list.upstream}>{m.male_red_platypus_borrow()}</a></address>
	{/if}
	<p class="whitespace-pre-wrap">{data.list.description}</p>
</Section>

{#if data.entries.items.length && sources && sources.length && select >= 0 && select < sources.length}
	<Section title={m.mealy_soft_myna_talk()}>
		<ExternalEmbed src={sources[select]} />
		<div class="my-2">
			{#each sources as s, i (i)}
				<label
					><input
						hidden
						type="radio"
						name="cover_select"
						value={i}
						bind:group={select}
					/>{PlatformNames[s.platform]}{s.work_origin === 0
						? ''
						: ' ' + WorkOriginNames[s.work_origin]()}</label
				>
			{/each}
		</div>
	</Section>
{/if}
<Section title={m.bald_clear_marlin_grasp()}>
	{#if data.entries?.items.length}
		<div class="flex w-full">
			<ol
				class="mr-5 w-full list-outside list-decimal"
				start={1 + data.batch_size * (data.page - 1)}
			>
				{#each data.entries.items as entry, i (i)}
					<li class="mx-5 w-full p-1">
						<label class="grid gap-5 md:grid-cols-[15rem_1fr]">
							<input class="hidden" type="radio" value={i} bind:group={current} />
							<WorkCard work={entry.work} />
							{#if entry.description}
								<p class="wrap-anywhere">{entry.description}</p>
							{:else}
								<p class="text-otodb-content-fainter">
									[{m.simple_less_marlin_enchant()}]
								</p>
							{/if}
						</label>
					</li>
				{/each}
			</ol>
		</div>
		{#if data.entries?.count}
			<Pager n_count={data.entries.count} page={data.page} page_size={data.batch_size} />
		{/if}
	{:else}
		<h3>{m.hour_flat_finch_zoom()}</h3>
	{/if}
</Section>

{#if pending_items.length}
	<Section title={m.front_smart_hound_fold()}>
		<ul>
			{#each pending_items as src, i (i)}
				<li>
					<span>
						<h3>
							<a href="/upload/{src.id}">{src.title || src.url}</a>
						</h3>
						<h4>{PlatformNames[src.platform]} {src.published_date}</h4>
					</span>
					<span>
						<a href={src.url} target="_blank" rel="noopener noreferrer"
							><WorkThumbnail
								thumbnail={src.thumbnail}
								alt={src.title || src.url}
								class="float-right clear-both aspect-video w-50"
							/></a
						>
					</span>
				</li>
			{/each}
		</ul>
		<LoadMoreButton
			fetchNextBatch={() =>
				client.GET('/api/list/pending', {
					fetch,
					params: {
						query: {
							list_id: data.list.id,
							limit: data.batch_size,
							offset: pending_items.length
						}
					}
				})}
			maxCount={data.pending_items!.count}
			bind:results={pending_items}
		/>
	</Section>
{/if}

<Section title={m.same_broad_haddock_pinch()}>
	<CommentTree
		comments={data.comments}
		user={data.user ?? null}
		model={PathsApiCommentCommentDeleteParametersQueryModel.pool}
		pk={data.list.id}
	/>
</Section>

<style>
	ul > li {
		display: flex;
		justify-content: space-between;
		margin: 1rem 0;
	}
	ul > li,
	ol > li > label {
		background-color: var(--otodb-color-bg-primary);
		padding: 1rem;
		cursor: pointer;
		&:has(> input:checked) {
			background-color: var(--otodb-color-bg-fainter);
		}
	}
	label:has(> input[name='cover_select']) {
		padding: 0.2rem 0.5rem;
		display: inline-block;
		background-color: var(--otodb-color-bg-primary);
		border: 1px solid var(--otodb-color-content-primary);
		&:hover {
			background-color: var(--otodb-color-bg-fainter);
		}
		&:active {
			background-color: var(--otodb-color-bg-faint);
		}
	}
	label:has(> input[name='cover_select']:checked) {
		background-color: var(--otodb-color-content-primary);
		border: 1px solid var(--otodb-color-bg-primary);
		color: var(--otodb-color-bg-primary);
	}
</style>
