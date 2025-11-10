<script lang="ts">
	import Section from '$lib/Section.svelte';
	import { m } from '$lib/paraglide/messages.js';
	import {
		LanguageNames,
		Languages,
		ProfileConnectionLink,
		ProfileConnectionTypes,
		SongConnectionLink,
		SongConnectionTypes,
		MediaConnectionLink,
		MediaConnectionTypes,
		TagWorkConnectionLink,
		TagWorkConnectionTypes,
		WorkTagCategory,
		MediaType
	} from '$lib/enums';
	import type { PageProps } from './$types';
	import Markdown from 'svelte-exmarkdown';
	import RelationEditor from '$lib/RelationEditor.svelte';
	import client, { getTagDisplaySlug } from '$lib/api';
	import { goto, invalidateAll } from '$app/navigation';
	import { getLocale, locales } from '$lib/paraglide/runtime';
	import type { components } from '$lib/schema';
	import { callErrorToast, callSavingToast } from '$lib/toast';
	import { dirtyEnhance } from '$lib/ui';
	import TagsField from '$lib/TagsField.svelte';

	let { data, form }: PageProps = $props();

	let parents = $state(
		form?.parent_slugs ?? data.parents?.map((t) => getTagDisplaySlug(t)) ?? []
	);
	let prev_n_parents = parents.length;
	let primary = $state(
		form?.primary ??
			(data.details?.primary_parent
				? (() => {
						const parentTag = data.parents?.find(
							(t) => t.slug === data.details?.primary_parent
						);
						return parentTag ? parents.indexOf(getTagDisplaySlug(parentTag)) : -1;
					})()
				: -1)
	);
	$effect(() => {
		if (prev_n_parents === 0 && parents.length > 0) primary = 0;
		if (parents.length === 0) primary = -1;
		prev_n_parents = parents.length;
	});

	let category = $state(form?.category ?? data.tag?.category);
	let wikiView = $state(getLocale());
	let mds = $state(
		Object.fromEntries(
			locales.map((lang) => [
				lang,
				data.wiki_page?.find((p) => p.lang === Languages[lang])?.page ?? ''
			])
		)
	);

	let tagLangPrefs = $state(
		Object.fromEntries(
			locales.map((l) => [
				l,
				data.tag.lang_prefs.find(({ lang }) => lang === Languages[l])?.tag ?? null
			])
		)
	);

	const removeAlias = async (alias: components['schemas']['TagWorkSchema']) => {
		await client.DELETE('/api/tag/alias', {
			fetch,
			params: { query: { tag_slug: data.tag.slug, alias: alias.slug } }
		});
		invalidateAll();
	};

	const setBase = async (tag: components['schemas']['TagWorkSchema']) => {
		await client.POST('/api/tag/set_base', {
			fetch,
			params: { query: { tag_slug: tag.slug } }
		});
		goto(`/tag/${tag.slug}/`, { invalidateAll: true });
	};

	const submitLangPref = async (lang: number, tag_slug: string) => {
		const p = client.PUT('/api/tag/lang_pref', {
			fetch,
			params: { query: { lang, tag_slug } }
		});
		callSavingToast(p);
		await p;
		invalidateAll();
	};

	let urls = $state(
		[
			...data.connections[0]!.map(({ site, content_id }) =>
				TagWorkConnectionLink[site](content_id)
			),
			...(data.connections[1]?.map(
				({ site, content_id, dead }) =>
					(dead ? '-' : '') +
					(data.tag.category === 6 ? MediaConnectionLink : ProfileConnectionLink)[site](
						content_id
					)
			) ?? []),
			...(data.song_connections?.map(({ site, content_id }) =>
				SongConnectionLink[site](content_id)
			) ?? [])
		].join('\n') ?? ''
	);

	$effect(() => {
		if (form?.failed) {
			callErrorToast(m.green_due_javelina_pop());
		}
	});

	const del = async () => {
		const { response } = await client.DELETE('/api/tag/tag', {
			fetch,
			params: { query: { tag_slug: data.tag.slug } }
		});
		if (response.ok) {
			goto('/', { invalidateAll: true });
		} else if (response.status === 400) {
			callErrorToast(m.that_new_mayfly_spur());
		}
	};
</script>

<Section
	title={m.mild_loud_shad_enchant({ type: m.empty_legal_chicken_taste(), name: data.tag.name })}
	menuLinks={data.links}
>
	<form method="POST" use:dirtyEnhance action="?/edit">
		{#if data.tag.category === 2 && category !== 2}
			<p class="text-red-500">
				{m.front_game_porpoise_pout()}
			</p>
		{/if}
		<table>
			<tbody>
				<tr>
					<th><label for="category">{m.plane_awful_bobcat_spark()}</label></th>
					<td
						><select name="category" bind:value={category}>
							{#each WorkTagCategory as cat, i (i)}
								<option value={i}>{cat()}</option>
							{/each}
						</select></td
					>
				</tr>
				<tr>
					<th><label for="parent">{m.away_crisp_blackbird_twist()}</label></th>
					<td>
						<TagsField type="work" bind:value={parents} name="parents" />
					</td>
				</tr>
				<tr>
					<th><label for="primary">{m.alive_light_eagle_stop()}</label></th>
					<td
						><select name="primary" bind:value={primary}
							><option value={-1}>None</option>{#each parents as p, i (i)}<option
									value={i}>{p}</option
								>{/each}</select
						></td
					>
				</tr>
				<tr>
					<th><label for="deprecated">{m.heavy_orange_okapi_intend()}</label></th>
					<td
						><input
							type="checkbox"
							name="deprecated"
							checked={form?.deprecated ?? data.tag.deprecated}
						/></td
					>
				</tr>
				{#if category === 2}
					<tr
						><th><label for="song_title">{m.large_factual_octopus_exhale()}</label></th
						><td
							><input
								type="text"
								name="song_title"
								value={data.tag?.song?.title ?? ''}
								required
							/></td
						></tr
					>
					<tr
						><th><label for="song_author">{m.crisp_red_canary_tickle()}</label></th><td
							><input
								type="text"
								name="song_author"
								value={data.tag?.song?.author ?? ''}
								required
							/></td
						></tr
					>
					<tr
						><th><label for="song_bpm">BPM</label></th><td
							><input
								type="number"
								step="any"
								min="0"
								name="song_bpm"
								value={data.tag?.song?.bpm}
							/></td
						></tr
					>
					<tr
						><th
							><label for="song_variable_bpm">{m.tasty_male_tadpole_glow()}</label
							></th
						><td
							><input
								type="checkbox"
								name="song_variable_bpm"
								checked={data.tag?.song?.variable_bpm ?? false}
							/></td
						></tr
					>
				{:else if category === 6}
					<tr>
						<th>Media type</th>
						<td>
							<select name="media_type" multiple value={data.tag.media_type ?? []}>
								{#each Object.keys(MediaType).filter((e) => !isNaN(e)) as t, i (i)}
									<option value={+t}>{MediaType[t]()}</option>
								{/each}
							</select>
						</td>
					</tr>
				{/if}
			</tbody>
		</table>
		<input type="submit" />
	</form>
	<button onclick={del}>{m.chunky_giant_quail_breathe()}</button>
</Section>

{#if category === 2 && data.tag.category === 2}
	<Section
		title={m.mild_loud_shad_enchant({
			type: m.grand_nice_pony_belong() + ' ' + m.alive_these_jay_pick(),
			name: data.tag!.song!.title
		})}
		menuLinks={data.song_links}
	>
		<RelationEditor
			init_relations={data.song_relations}
			obj_type="song"
			this_id={data.tag.song?.id}
		></RelationEditor>
	</Section>
{/if}

<Section title={m.alive_lofty_opossum_laugh()}>
	{#if data.details.aliases.length}
		<table>
			<thead>
				<tr
					><th>{m.alive_lofty_opossum_laugh()}</th>
					{#each locales as locale, i (i)}
						<th>{LanguageNames[locale]} {m.mellow_upper_finch_drip()}</th>
					{/each}
					<th>{m.mild_full_sloth_work()}</th></tr
				>
			</thead>
			<tbody>
				<tr
					><td>{data.tag.name}</td>
					{#each locales as locale, i (i)}
						<td
							><input
								type="radio"
								bind:group={tagLangPrefs[locale]}
								value={data.tag.name}
								onclick={() => submitLangPref(Languages[locale], data.tag.slug)}
							/>{#if tagLangPrefs[locale] === null}{m.factual_house_antelope_arise()}{/if}</td
						>
					{/each}<td>{m.simple_less_marlin_enchant()}</td></tr
				>
				{#each data.details.aliases as a, i (i)}
					<tr
						><td>{a.name}</td>
						{#each locales as locale, i (i)}
							<td
								><input
									type="radio"
									bind:group={tagLangPrefs[locale]}
									value={a.name}
									onclick={() => submitLangPref(Languages[locale], a.slug)}
								/></td
							>
						{/each}
						<td
							><button onclick={() => removeAlias(a)}
								>{m.that_true_owl_embrace()}</button
							><button onclick={() => setBase(a)}>{m.even_such_wallaby_fond()}</button
							></td
						></tr
					>
				{/each}
			</tbody>
		</table>
	{/if}
	<a href="/tag/alias?from={data.tag.slug}">{m.weary_moving_swallow_chop()}</a>
</Section>

<Section title={m.curly_zesty_pelican_aim()}>
	<div class="my-2">
		{#each locales as locale, i (i)}
			<label class="wiki-lang-tab">
				<input type="radio" bind:group={wikiView} value={locale} />
				{LanguageNames[locale]}
			</label>
		{/each}
	</div>

	<form action="?/wiki_page" method="POST" use:dirtyEnhance>
		<input type="text" hidden value={wikiView} name="lang" />
		<div class="grid grid-cols-2 gap-3">
			<textarea name="md" bind:value={mds[wikiView]}></textarea>
			<div class="prose prose-neutral prose-sm dark:prose-invert">
				<Markdown md={mds[wikiView]} />
			</div>
		</div>
		<input type="submit" />
	</form>
</Section>

<Section title={m.jumpy_spry_canary_scoop()}>
	<details>
		<summary>{m.fit_noble_niklas_build()}</summary>
		<table>
			<tbody>
				{#if category === 2 && data.tag.category === 2}
					{#each Object.keys(SongConnectionTypes).filter((e) => !isNaN(e)) as k, i (i)}
						<tr
							><td>{SongConnectionTypes[k]}</td><td
								><code>{SongConnectionLink[k]('<code>')}</code></td
							></tr
						>
					{/each}
				{:else if category === 6 && data.tag.category === 6}
					{#each Object.keys(MediaConnectionTypes).filter((e) => !isNaN(e)) as k, i (i)}
						<tr
							><td>{MediaConnectionTypes[k]}</td><td
								><code>{MediaConnectionLink[k]('<code>')}</code></td
							></tr
						>
					{/each}
				{:else if category === 4 && data.tag.category === 4}
					{#each Object.keys(ProfileConnectionTypes).filter((e) => !isNaN(e)) as k, i (i)}
						<tr
							><td>{ProfileConnectionTypes[k]}</td><td
								><code>{ProfileConnectionLink[k]('<code>')}</code></td
							></tr
						>
					{/each}
				{/if}
				{#each Object.keys(TagWorkConnectionTypes).filter((e) => !isNaN(e)) as k, i (i)}
					<tr
						><td>{TagWorkConnectionTypes[k]}</td><td
							><code>{TagWorkConnectionLink[k]('<code>')}</code></td
						></tr
					>
				{/each}
			</tbody>
		</table>
	</details>
	<form action="?/connections" method="POST" use:dirtyEnhance>
		<textarea
			bind:value={urls}
			name="urls"
			class="w-full"
			placeholder={m.close_any_racoon_cut()}
		></textarea>
		<input type="submit" />
	</form>
</Section>

<style>
	label.wiki-lang-tab {
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
		& > input {
			display: none;
		}
		&:has(> input:checked) {
			background-color: var(--otodb-color-content-primary);
			border: 1px solid var(--otodb-color-bg-primary);
			color: var(--otodb-color-bg-primary);
		}
	}
</style>
