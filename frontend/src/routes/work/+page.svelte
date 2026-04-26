<script lang="ts">
	import Section from '$lib/Section.svelte';

	import { m } from '$lib/paraglide/messages.js';
	import WorkCard from '$lib/WorkCard.svelte';
	import TagsField from '$lib/TagsField.svelte';
	import Pager from '$lib/Pager.svelte';
	import { page } from '$app/state';
	import { SEARCH_DOCS_POST_ID } from '$lib/ui';
	let { data } = $props();

	const examples = [
		{ tags: 'rating:general duration:>=300', desc: m.bold_quiet_robin_chase },
		{ tags: 'mediatype:anime order:published', desc: m.clever_swift_owl_seek },
		{
			tags: '(super_mario_series | kirby_series) bpm:140..160',
			desc: m.bright_calm_finch_match
		},
		{ tags: 'touhou -touhou[category:song]', desc: m.crisp_neat_wren_match }
	];
</script>

<Section
	title={m.grand_merry_fly_succeed()}
	type={m.mean_top_antelope_love()}
	menuLinks={[
		{ title: m.grand_merry_fly_succeed(), pathname: `work` },
		{ title: m.empty_legal_chicken_taste(), pathname: `tag?query=${data.query}` },
		{ title: m.grand_nice_pony_belong(), pathname: `song?query=${data.query}` },
		{
			title: m.dull_plain_angelfish_cuddle(),
			pathname: `song_attribute?query=${data.query}`
		},
		{ title: m.stale_loose_squid_cut(), pathname: `list?query=${data.query}` }
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

		<details>
			<summary>{m.keen_brisk_lark_track()}</summary>
			<ul class="grid list-none grid-cols-[max-content_auto] gap-x-4 gap-y-1">
				{#each examples as { tags, desc } (tags)}
					<li class="contents">
						<a class="otodb-search-link" href="/work?tags={encodeURIComponent(tags)}">
							<code>{tags}</code>
						</a>
						<span>{desc()}</span>
					</li>
				{/each}
			</ul>
			<div class="mt-2">
				<a href="/post/{SEARCH_DOCS_POST_ID}">
					{m.swift_keen_otter_guide()}
				</a>
			</div>
		</details>
	</form>
	<hr />
	<div class="grid grid-cols-[repeat(auto-fill,minmax(192px,1fr))] gap-x-4 gap-y-4">
		{#each data.results.items as work, i (i)}
			<WorkCard {work} />
		{/each}
	</div>
	<Pager
		n_count={data.results.count}
		page={data.page}
		page_size={data.batch_size}
		base_url={page.url.toString()}
	/>
</Section>

<style>
	hr {
		margin: 1rem 0;
	}
</style>
