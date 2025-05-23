<script lang="ts">
	import Section from '$lib/Section.svelte';
	import type { PageProps } from './$types';
	import { m } from '$lib/paraglide/messages.js';
	import CommentTree from '$lib/CommentTree.svelte';
	import { Platform } from '$lib/enums';
	import { isSOV, isSVO } from '$lib/ui';
	import { getLocale } from '$lib/paraglide/runtime';

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
	<h3>
		{#if isSVO(getLocale())}
			{m.curly_safe_lynx_fond()}
		{/if}
		<a href="/profile/{data.list?.author.username}">{data.list?.author.username}</a>
		{#if isSOV(getLocale())}
			{m.curly_safe_lynx_fond()}
		{/if}
	</h3>
	<p class="whitespace-pre-wrap">{data.list.description}</p>
	{#if data.list?.author.username == data.user?.username}
		<a href="/list/{data.list.id}/edit">{m.sunny_steep_termite_trust()}</a>
		<a href="/list/{data.list.id}/delete" data-sveltekit-preload-data="tap"
			>{m.key_sea_chicken_boost()}</a
		>
	{/if}
</Section>
<Section title={m.bald_clear_marlin_grasp()}>
	<ol class="list-outside list-decimal">
		{#each data.entries.items as entry, i (i)}
			<li class="mx-5 my-3 p-2">
				<span class="inline-flex items-start gap-1">
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
				</span>
			</li>
		{:else}
			<li>{m.hour_flat_finch_zoom()}</li>
		{/each}
	</ol>
</Section>

{#if data.list.pending_items.length}
	<Section title={m.front_smart_hound_fold()}>
		<ul>
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
							<p class="text-red-400">
								{m.mild_loud_shad_enchant({
									type: m.weary_spicy_fly_attend(),
									name: src.rejection_reason
								})}
							</p>
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
	ul > li {
		display: flex;
		justify-content: space-between;
		margin: 1rem 0;
	}
	ul > li,
	ol > li {
		background-color: var(--otodb-fainter-bg);
		padding: 1rem;
	}
</style>
