<script lang="ts">
	import Section from '$lib/Section.svelte';
	import { m } from '$lib/paraglide/messages.js';
	import {
		Errors,
		LanguageNames,
		Languages,
		ProfileConnectionLink,
		ProfileConnectionTypes,
		SongConnectionLink,
		SongConnectionTypes,
		MediaConnectionLink,
		MediaConnectionTypes,
		WorkTagCategory,
		MediaType
	} from '$lib/enums';
	import type { PageProps } from './$types';
	import RelationEditor from '$lib/RelationEditor.svelte';
	import client, { getTagDisplaySlug } from '$lib/api';
	import { renderMarkdown } from '$lib/markdown';
	import { goto } from '$app/navigation';
	import { getLocale, locales } from '$lib/paraglide/runtime';
	import { callErrorToast } from '$lib/toast';
	import { dirtyEnhance } from '$lib/ui';
	import TagsField from '$lib/TagsField.svelte';
	import GuidelineWarning from '$lib/GuidelineWarning.svelte';

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
	let edited_md = $state(Object.fromEntries(locales.map((lang) => [lang, false])));

	let tagLangPrefs = $state(
		Object.fromEntries(
			locales.map((l) => [
				l,
				data.tag.lang_prefs.find(({ lang }) => lang === Languages[l])?.slug ?? null
			])
		)
	);
	let tagNames: Record<string, string> = $state(
		Object.fromEntries([
			[data.tag.slug, data.tag.name],
			...data.details.aliases.map((a) => [a.slug, a.name])
		])
	);
	let to_delete: string[] = $state([]);
	let base = $state(data.tag.slug);
	const aliases_post_gate = { p: Promise.withResolvers<void>() };

	const submit_aliases = async () => {
		await aliases_post_gate.p.promise;
		const { error } = await client.POST('/api/tag/tag_aliases', {
			fetch,
			body: {
				base_slug: base,
				unalias_slugs: to_delete,
				lang_prefs: Object.fromEntries(
					Object.entries(tagLangPrefs).map(([k, v]) => [Languages[k], v])
				),
				names: tagNames
			},
			params: { query: { type: 'work', tag_slug: data.tag.slug } }
		});
		if (error) {
			aliases_post_gate.p = Promise.withResolvers<void>();
			// TODO: Update toast API to handle cases like this accordingly
			callErrorToast(
				(error && typeof error === 'object' && 'code' in error
					? (Errors[error.code as number]?.(error.data as Record<string, string>) ??
						(error.data as Record<string, string>)?.message)
					: undefined) ?? m.green_due_javelina_pop()
			);
		} else goto(`/tag/${base}/`, { invalidateAll: true });
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

	let previewHtml = $derived(renderMarkdown(mds[wikiView] ?? ''));

	const form_barrier = {};
</script>

<Section title={data.tag.name} type={m.empty_legal_chicken_taste()} menuLinks={data.links}>
	<GuidelineWarning />
	<form method="POST" use:dirtyEnhance={{ barrier: form_barrier, priority: 0 }} action="?/edit">
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
	<hr class="my-2" />
	<button onclick={del}>{m.chunky_giant_quail_breathe()}</button>
</Section>

{#if category === 2 && data.tag.category === 2}
	<Section
		title={data.tag!.song!.title}
		type={m.grand_nice_pony_belong() + ' ' + m.alive_these_jay_pick()}
		menuLinks={data.song_links}
	>
		<RelationEditor
			init_relations={data.song_relations}
			obj_type="song"
			this_id={data.tag.song?.id}
			form_control={{ barrier: form_barrier, priority: 4 }}
		></RelationEditor>
	</Section>
{/if}

<Section title={m.alive_lofty_opossum_laugh()}>
	<a href="/tag/alias?from={data.tag.slug}">{m.weary_moving_swallow_chop()}</a>
	<form
		method="POST"
		use:dirtyEnhance={{
			barrier: form_barrier,
			priority: 2,
			manual_post: aliases_post_gate
		}}
		onsubmit={submit_aliases}
	>
		{#if data.details.aliases.length}
			<table>
				<thead>
					<tr
						><th>{m.alive_lofty_opossum_laugh()}</th>
						{#each locales as locale, i (i)}
							<th>{LanguageNames[locale]} {m.mellow_upper_finch_drip()}</th>
						{/each}
						<th>{m.that_true_owl_embrace()}</th><th>{m.even_such_wallaby_fond()}</th
						></tr
					>
				</thead>
				<tbody>
					<tr
						><td><input type="text" bind:value={tagNames[data.tag.slug]} /></td>
						{#each locales as locale, i (i)}
							<td
								><input
									type="radio"
									bind:group={tagLangPrefs[locale]}
									value={data.tag.slug}
								/>{#if tagLangPrefs[locale] === null}{m.factual_house_antelope_arise()}{/if}</td
							>
						{/each}<td
							><input
								type="checkbox"
								bind:group={to_delete}
								value={data.tag.slug}
								disabled={base === data.tag.slug}
							/></td
						><td
							><input
								type="radio"
								bind:group={base}
								value={data.tag.slug}
								disabled={to_delete.includes(data.tag.slug)}
							/></td
						></tr
					>
					{#each data.details.aliases as a, i (i)}
						<tr
							><td><input type="text" bind:value={tagNames[a.slug]} /></td>
							{#each locales as locale, i (i)}
								<td
									><input
										type="radio"
										bind:group={tagLangPrefs[locale]}
										value={a.slug}
									/></td
								>
							{/each}
							<td
								><input
									type="checkbox"
									bind:group={to_delete}
									value={a.slug}
									disabled={base === a.slug}
								/></td
							><td
								><input
									type="radio"
									bind:group={base}
									value={a.slug}
									disabled={to_delete.includes(a.slug)}
								/></td
							></tr
						>
					{/each}
				</tbody>
			</table>
		{:else}
			<table>
				<thead>
					<tr><th>{m.alive_lofty_opossum_laugh()}</th></tr>
				</thead>
				<tbody>
					<tr><td><input type="text" bind:value={tagNames[data.tag.slug]} /></td></tr>
				</tbody>
			</table>
		{/if}
		<input type="submit" />
	</form>
</Section>

<Section title={m.curly_zesty_pelican_aim()}>
	<div class="my-2">
		{#each locales as locale, i (i)}
			<label class="wiki-lang-tab">
				<input type="radio" bind:group={wikiView} value={locale} />
				{LanguageNames[
					locale
				]}{#if edited_md[locale]}{m.great_clean_beaver_amuse()}{m.awful_house_liger_expand({
						content: '*'
					})}{/if}
			</label>
		{/each}
	</div>

	<form
		action="?/wiki_page"
		method="POST"
		use:dirtyEnhance={{ barrier: form_barrier, priority: 1 }}
	>
		<input
			type="text"
			hidden
			name="wiki_pages"
			value={JSON.stringify(
				locales
					.filter((lang) => edited_md[lang])
					.map((lang) => ({ lang: Languages[lang], md: mds[lang] }))
			)}
		/>
		<div class="grid grid-cols-2 gap-3">
			<textarea
				onchange={() => {
					edited_md[wikiView] = true;
				}}
				bind:value={mds[wikiView]}
			></textarea>
			<div class="prose prose-neutral prose-sm dark:prose-invert">
				<!-- eslint-disable-next-line svelte/no-at-html-tags -->
				{@html previewHtml}
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
				{#if category === 2}
					{#each Object.keys(SongConnectionTypes).filter((e) => !isNaN(e)) as k, i (i)}
						<tr
							><td>{SongConnectionTypes[k]}</td><td
								><code>{SongConnectionLink[k]('<code>')}</code></td
							></tr
						>
					{/each}
				{:else if category === 6}
					{#each Object.keys(MediaConnectionTypes).filter((e) => !isNaN(e)) as k, i (i)}
						<tr
							><td>{MediaConnectionTypes[k]}</td><td
								><code>{MediaConnectionLink[k]('<code>')}</code></td
							></tr
						>
					{/each}
				{:else if category === 4}
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
	<form
		action="?/connections"
		method="POST"
		use:dirtyEnhance={{ barrier: form_barrier, priority: 3 }}
	>
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
