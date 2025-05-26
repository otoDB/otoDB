<script lang="ts">
	import Section from '$lib/Section.svelte';
	import { m } from '$lib/paraglide/messages.js';
	import {
		LanguageNames,
		Languages,
		SongConnectionTypes,
		TagWorkConnectionTypes,
		WorkTagCategory
	} from '$lib/enums';
	import { enhance } from '$app/forms';
	import type { PageProps } from './$types';
	import TagField from '$lib/TagField.svelte';
	import Markdown from 'svelte-exmarkdown';
	import RelationEditor from '$lib/RelationEditor.svelte';
	import client from '$lib/api';
	import { invalidateAll } from '$app/navigation';
	import { getLocale, locales } from '$lib/paraglide/runtime';
	import { debounce } from '$lib/ui';
	import type { components } from '$lib/schema';

	let { data, form }: PageProps = $props();

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

	const submitLangPref = async (lang: number, tag_slug: string) => {
		await client.PUT('/api/tag/lang_pref', {
			fetch,
			params: { query: { lang, tag_slug } }
		});
		invalidateAll();
	};

	const update_connection = async (e) => {
		const el = e.target;
		if (el.value.trim() === '')
			await client.DELETE('/api/tag/connection', {
				fetch,
				params: { query: { site: +el.name, tag_slug: data.tag.slug } }
			});
		else
			await client.PUT('/api/tag/connection', {
				body: { content_id: el.value.trim(), site: +el.name },
				params: { query: { tag_slug: data.tag.slug } }
			});
	};
	const update_song_connection = async (e) => {
		const el = e.target;
		if (el.value.trim() === '')
			await client.DELETE('/api/tag/song_connection', {
				fetch,
				params: { query: { site: +el.name, song_id: data.tag.song?.id } }
			});
		else
			await client.PUT('/api/tag/song_connection', {
				body: { content_id: el.value.trim(), site: +el.name },
				params: { query: { song_id: data.tag.song?.id } }
			});
	};
</script>

<Section
	title={m.mild_loud_shad_enchant({ type: m.empty_legal_chicken_taste(), name: data.tag.name })}
	menuLinks={data.links}
>
	<form method="POST" use:enhance action="?/edit">
		{#if form?.failed}<p class="error">Failed!</p>{/if}
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
					<td
						><TagField
							type="work"
							name="parent"
							value={form?.parent_slug ?? data.parent_slug ?? ''}
						/></td
					>
				</tr>
			</tbody>
		</table>
		{#if category === 2}
			<table>
				<tbody>
					<tr
						><th><label for="song_title">{m.large_factual_octopus_exhale()}</label></th
						><td
							><input
								type="text"
								name="song_title"
								value={data.tag?.song?.title ?? ''}
							/></td
						></tr
					>
					<tr
						><th><label for="song_author">{m.crisp_red_canary_tickle()}</label></th><td
							><input
								type="text"
								name="song_author"
								value={data.tag?.song?.author ?? ''}
							/></td
						></tr
					>
					<tr
						><th><label for="song_bpm">BPM</label></th><td
							><input
								type="number"
								name="song_bpm"
								value={data.tag?.song?.bpm ?? 100}
							/></td
						></tr
					>
				</tbody>
			</table>
		{/if}
		<input type="submit" />
	</form>
</Section>

{#if data.details.aliases.length}
	<Section title={m.alive_lofty_opossum_laugh()}>
		<table>
			<thead>
				<tr
					><th>Name</th>
					{#each locales as locale, i (i)}
						<th>{LanguageNames[locale]} Display</th>
					{/each}
					<th>{m.that_true_owl_embrace()}</th></tr
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
							/>{#if tagLangPrefs[locale] === null}[Auto]{/if}</td
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
							></td
						></tr
					>
				{/each}
			</tbody>
		</table>
	</Section>
{/if}

<Section title={m.curly_zesty_pelican_aim()}>
	<div class="my-2">
		{#each locales as locale, i (i)}
			<label class="wiki-lang-tab">
				<input type="radio" bind:group={wikiView} value={locale} />
				{LanguageNames[locale]}
			</label>
		{/each}
	</div>

	<form action="?/wiki_page" method="POST" use:enhance>
		<input type="text" hidden value={wikiView} name="lang" />
		<div class="grid grid-cols-2 gap-3">
			<textarea required name="md" bind:value={mds[wikiView]}></textarea>
			<div id="md-preview">
				<Markdown md={mds[wikiView]} />
			</div>
		</div>
		<input type="submit" />
	</form>
</Section>

<Section title="Connections">
	<table>
		<thead>
			<tr>
				<td>Site</td>
				<td>ID</td>
			</tr>
		</thead><tbody>
			{#each Object.keys(TagWorkConnectionTypes)
				.filter((e) => !isNaN(e))
				.toSorted() as s, i (i)}
				<tr>
					<td>{TagWorkConnectionTypes[s]}</td>
					<td
						><input
							type="text"
							name={s}
							value={data.connections?.find(({ site }) => site === +s)?.content_id ??
								''}
							oninput={debounce(update_connection)}
						/></td
					></tr
				>
			{/each}
		</tbody>
	</table>
</Section>
{#if category === 2 && data.tag.category === 2}
	<Section
		title={m.mild_loud_shad_enchant({
			type: m.grand_nice_pony_belong(),
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

	<Section title="Song Connections">
		<table>
			<thead>
				<tr>
					<td>Site</td>
					<td>ID</td>
				</tr>
			</thead><tbody>
				{#each Object.keys(SongConnectionTypes)
					.filter((e) => !isNaN(e))
					.toSorted() as s, i (i)}
					<tr>
						<td>{SongConnectionTypes[s]}</td>
						<td
							><input
								type="text"
								name={s}
								value={data.song_connections?.find(({ site }) => site === +s)
									?.content_id ?? ''}
								oninput={debounce(update_song_connection)}
							/></td
						></tr
					>
				{/each}
			</tbody>
		</table>
	</Section>
{/if}

<style>
	label.wiki-lang-tab {
		padding: 0.2rem 0.5rem;
		display: inline-block;
		background-color: var(--otodb-bg-color);
		border: 1px solid var(--otodb-content-color);
		&:hover {
			background-color: var(--otodb-fainter-bg);
		}
		&:active {
			background-color: var(--otodb-faint-bg);
		}
		& > input {
			display: none;
		}
		&:has(> input:checked) {
			background-color: var(--otodb-content-color);
			border: 1px solid var(--otodb-bg-color);
			color: var(--otodb-bg-color);
		}
	}
</style>
