<script lang="ts">
	import Section from '$lib/Section.svelte';

	import { m } from '$lib/paraglide/messages.js';
	import { WorkTagCategory } from '$lib/enums';
	import WorkTag from '$lib/WorkTag.svelte';
	import Pager from '$lib/Pager.svelte';
	import { page } from '$app/state';
	import { locales } from '$lib/paraglide/runtime';
	import { languages } from '$lib/enums/Languages';
	import { allMediaTypes, mediaTypes } from '$lib/enums/MediaType';

	let { data } = $props();

	let category = $state(data.category);
</script>

<Section
	title={m.empty_legal_chicken_taste()}
	type={m.mean_top_antelope_love()}
	menuLinks={[
		{ title: m.grand_merry_fly_succeed(), pathname: `work?query=${data.query}` },
		{ title: m.empty_legal_chicken_taste(), pathname: 'tag' },
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
		<select name="category" bind:value={category}>
			<option value={-1}>{m.keen_soft_crow_relish()}</option>
			{#each WorkTagCategory as cat, i (i)}
				<option value={i}>{cat()}</option>
			{/each}
		</select>
		{#if category === 6}
			<select name="media_type" multiple value={data.media_type ?? []}>
				{#each allMediaTypes as t (t)}
					<option value={mediaTypes[t].id}>{mediaTypes[t].nameFn()}</option>
				{/each}
			</select>
		{/if}
		<h4>{m.good_heavy_mayfly_spin()}</h4>
		<select name="order" value={data.order ?? 'newest'}>
			<option value="newest">{m.shy_quiet_anaconda_enrich()}</option>
			<option value="count">{m.low_icy_lizard_commend()}</option>
			<option value="name">{m.livid_dull_parakeet_devour()}</option>
		</select>
		<div class="mt-2 flex flex-wrap items-start gap-4">
			<label class="flex flex-col">
				{m.loose_trite_bat_roam()}
				<select name="wiki_lang" multiple value={data.wiki_lang}>
					{#each locales as lang (lang)}
						<option value={languages[lang].id}>{languages[lang].name}</option>
					{/each}
				</select>
			</label>
			<label class="flex flex-col">
				{m.actual_flat_mayfly_expand()}
				<select name="wiki_lang_missing" multiple value={data.wiki_lang_missing}>
					{#each locales as lang (lang)}
						<option value={languages[lang].id}>{languages[lang].name}</option>
					{/each}
				</select>
			</label>
			<label class="flex flex-col">
				{m.lofty_house_nils_greet()}
				<select name="lang_pref" multiple value={data.lang_pref}>
					<option value={-1}>{m.mellow_alert_jan_leap()}</option>
					{#each locales as lang (lang)}
						<option value={languages[lang].id}>{languages[lang].name}</option>
					{/each}
				</select>
			</label>
			<label class="flex flex-col">
				{m.strong_lower_firefox_exhale()}
				<select name="lang_pref_missing" multiple value={data.lang_pref_missing}>
					{#each locales as lang (lang)}
						<option value={languages[lang].id}>{languages[lang].name}</option>
					{/each}
				</select>
			</label>
			<label class="flex flex-col">
				{m.stout_same_insect_conquer()}
				<select name="has_connections" value={data.has_connections ?? ''}>
					<option value="">---</option>
					<option value="true">{m.broad_large_squid_zoom()}</option>
					<option value="false">{m.great_lucky_goldfish_sail()}</option>
				</select>
			</label>
			<label>
				<input type="checkbox" name="deprecated_only" checked={data.deprecated_only} />
				{m.pink_funny_platypus_aim()}
			</label>
			<label>
				<input type="hidden" name="hide_orphans" value="off" />
				<input type="checkbox" name="hide_orphans" checked={data.hide_orphans} />
				{m.spry_great_monkey_fry()}
			</label>
		</div>
		<input type="submit" value={m.mean_top_antelope_love()} class="mt-2" />
	</form>

	<hr class="my-5" />

	<table class="w-full">
		<tbody>
			{#each data.results?.items ?? [] as tag, i (i)}
				<tr class="border-otodb-bg-fainter border-b">
					<td class="py-1.5">
						<WorkTag {tag} />
						<span class="text-otodb-content-faint ml-1 tabular-nums"
							>{tag.n_instance ?? 0}</span
						>
					</td>
				</tr>
			{/each}
		</tbody>
	</table>
	{#if data.results?.count}
		<Pager
			n_count={data.results.count}
			page={data.page}
			page_size={data.batch_size}
			base_url={page.url.toString()}
		/>
	{/if}
</Section>
