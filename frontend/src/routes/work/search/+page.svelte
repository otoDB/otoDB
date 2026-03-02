<script lang="ts">
	import Section from '$lib/Section.svelte';
	import type { PageProps } from './$types';
	import { m } from '$lib/paraglide/messages.js';
	import WorkCard from '$lib/WorkCard.svelte';
	import TagsField from '$lib/TagsField.svelte';
	import Pager from '$lib/Pager.svelte';
	import { page } from '$app/state';
	import { UserLevel } from '$lib/enums';

	let { data }: PageProps = $props();
</script>

<Section
	title={m.grand_merry_fly_succeed()}
	type={m.mean_top_antelope_love()}
	menuLinks={[
		{ title: m.grand_merry_fly_succeed(), pathname: `work/search` },
		{ title: m.empty_legal_chicken_taste(), pathname: `tag/search?query=${data.query}` },
		{ title: m.grand_nice_pony_belong(), pathname: `song/search?query=${data.query}` },
		{
			title: m.dull_plain_angelfish_cuddle(),
			pathname: `song_attribute/search?query=${data.query}`
		},
		{ title: m.stale_loose_squid_cut(), pathname: `list/search?query=${data.query}` }
	]}
>
	<form target="_self" method="get">
		<input
			type="text"
			name="query"
			placeholder="{m.mean_top_antelope_love()}..."
			value={data.query}
		/>
		<input type="submit" value={m.mean_top_antelope_love()} />
		<h4>{m.mild_loud_shad_enchant({ type: m.empty_legal_chicken_taste(), name: '' })}</h4>
		<TagsField type="work" name="tags" value={data.query_tags.split(' ')} class="w-full" />
		<h4>{m.good_heavy_mayfly_spin()}</h4>
		<select name="order" value={data.order ?? 'id'}
			><option value="id">{m.kind_vivid_niklas_savor()}</option><option value="pub"
				>{m.swift_each_zebra_assure()}</option
			></select
		>
		<select name="dir" value={data.dir ?? '-'}
			><option value="-">{m.kind_quick_bullock_push()}</option><option value="+"
				>{m.novel_orange_mantis_feast()}</option
			></select
		>
		{#if data.user?.level >= UserLevel.EDITOR}
			<hr />
			<select name="queue" value={data.queue ?? ''}>
				<option value="">--</option>
				<option value="unseen">Unseen</option>
				<option value="all">All</option>
			</select>
		{/if}
	</form>
	<hr />
	<div class="grid grid-cols-[repeat(auto-fill,minmax(192px,1fr))] gap-x-4 gap-y-4">
		{#each data.results?.items as work, i (i)}
			<WorkCard {work} />
		{/each}
	</div>
	{#if data.results?.count}
		<Pager
			n_count={data.results.count}
			page={data.page}
			page_size={data.batch_size}
			base_url={page.url}
		/>
	{/if}
</Section>

<style>
	hr {
		margin: 1rem 0;
	}
</style>
