<script lang="ts">
	import Section from '$lib/Section.svelte';
	import type { PageProps } from './$types';
	import { m } from '$lib/paraglide/messages.js';
	import WorkCard from '$lib/WorkCard.svelte';
	import TagsField from '$lib/TagsField.svelte';
	import client from '$lib/api';
	import LoadMoreButton from '$lib/LoadMoreButton.svelte';

	let { data }: PageProps = $props();
	let results = $derived(data.results!.items);

	const fetchNextBatch = () =>
		client.GET('/api/work/search', {
			fetch,
			params: {
				query: {
					query: data.query,
					tags: data.query_tags,
					limit: data.batch_size,
					offset: results.length,
					order: data.order ? (data.dir === '-' ? '-' : '') + data.order : null
				}
			}
		});
</script>

<svelte:head>
	<title
		>{m.mild_loud_shad_enchant({
			type: m.mean_top_antelope_love(),
			name: m.grand_merry_fly_succeed()
		})}</title
	>
</svelte:head>

<Section
	title={m.mild_loud_shad_enchant({
		type: m.mean_top_antelope_love(),
		name: m.grand_merry_fly_succeed()
	})}
	menuLinks={[
		{ title: m.grand_merry_fly_succeed(), pathname: `work/search` },
		{ title: m.empty_legal_chicken_taste(), pathname: `tag/search?query=${data.query}` },
		{ title: m.grand_nice_pony_belong(), pathname: `tag/song/search?query=${data.query}` },
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
	</form>
	<hr />
	<div class="grid grid-cols-[repeat(auto-fill,minmax(192px,1fr))] gap-x-4 gap-y-4">
		{#each results as work, i (i)}
			<WorkCard {work} />
		{/each}
	</div>
	<LoadMoreButton maxCount={data.results!.count} bind:results {fetchNextBatch} />
</Section>

<style>
	hr {
		margin: 1rem 0;
	}
</style>
