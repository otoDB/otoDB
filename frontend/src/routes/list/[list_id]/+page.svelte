<script lang="ts">
	import Section from '$lib/Section.svelte';
	import type { PageProps } from './$types';
	import { m } from '$lib/paraglide/messages.js';
	import CommentTree from '$lib/CommentTree.svelte';
	import { Platform, UserLevel, WorkOrigin } from '$lib/enums';
	import RefreshButton from '../../work/RefreshButton.svelte';
	import UnboundSourceActions from '../../work/unbound/UnboundSourceActions.svelte';

	let { data }: PageProps = $props();
</script>

<svelte:head>
	<title
		>{m.mild_loud_shad_enchant({
			type: m.stale_loose_squid_cut(),
			name: data.list.name
		})}</title
	>
</svelte:head>

<Section
	title={m.mild_loud_shad_enchant({ type: m.stale_loose_squid_cut(), name: data.list.name })}
>
	<h3>By: <a href="/profile/{data.list?.author.username}">{data.list?.author.username}</a></h3>
	<p class="whitespace-pre-wrap">{data.list.description}</p>
	{#if data.list?.author.username == data.user?.username}
		<a href="/list/{data.list.id}/edit">Edit this list...</a>
		<a href="/list/{data.list.id}/delete" data-sveltekit-preload-data="tap"
			>Delete this list...</a
		>
	{/if}
</Section>
<Section title="Entries">
	<ol class="list-outside list-decimal">
		{#each data.entries.items as entry, i (i)}
			<li class="ml-5 p-2">
				<div style="display: flex; gap: 1rem;align-items:flex-start;">
					<a href="/work/{entry.work.id}"
						><img
							style="max-width:10rem"
							src={entry.work.thumbnail}
							alt={entry.work.title}
						/></a
					>
					<div>
						<a href="/work/{entry.work.id}">{entry.work.title}</a>
						<p>{entry.description}</p>
					</div>
				</div>
			</li>
		{:else}
			<li>This list has no entries!</li>
		{/each}
	</ol>
	{JSON.stringify()}
</Section>

{#if data.list.pending_items.length}
	<Section title="Pending entries">
		<ul class="pending">
			{#each data.list.pending_items as src, i (i)}
				<li>
					<span>
						<h3>
							<a href={src.url} target="_blank" rel="noopener noreferrer"
								>{src.title}</a
							>
						</h3>
						<h4>{Platform[src.platform]} {src.published_date}</h4>
						{#if src.rejection_reason}
							<p class="text-red-400">Rejected: {src.rejection_reason}</p>
						{:else}
							<RefreshButton source={src} />
							{#if data.user && data.user?.level >= UserLevel.MODERATOR}
								<UnboundSourceActions source={src} />
							{/if}
						{/if}
					</span>
					<span>
						<a href={src.url} target="_blank" rel="noopener noreferrer"
							><img
								src={src.thumbnail}
								alt={src.title}
								class="float-right clear-both w-50"
							/></a
						>
					</span>
				</li>
			{/each}
		</ul>
	</Section>
{/if}

<Section title={m.same_broad_haddock_pinch()}>
	<CommentTree comments={data.comments} user={data.user ?? null} model="pool" pk={data.list.id} />
</Section>

<style>
	ul.pending > li {
		display: flex;
		background-color: var(--otodb-fainter-bg);
		justify-content: space-between;
		margin: 1rem 0;
		padding: 1rem;
	}
</style>
