<script lang="ts">
	import Section from '$lib/Section.svelte';
	import { m } from '$lib/paraglide/messages.js';
	import { LanguageNames, Languages, SongTagCategory } from '$lib/enums';
	import { enhance } from '$app/forms';
	import type { PageProps } from './$types';
	import TagField from '$lib/TagField.svelte';
	import { callErrorToast, callSavingToast } from '$lib/toast';
	import client from '$lib/api';
	import { goto, invalidateAll } from '$app/navigation';
	import GuidelineWarning from '$lib/GuidelineWarning.svelte';
	import { locales } from '$lib/paraglide/runtime';
	import type { components } from '$lib/schema';

	let { data, form }: PageProps = $props();

	let category = $state(form?.category ?? data.tag?.category);
	$effect(() => {
		if (form?.failed) {
			callErrorToast(m.green_due_javelina_pop());
		}
	});

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
			...data.aliases.map((a) => [a.slug, a.name])
		])
	);

	const removeAlias = async (alias: components['schemas']['TagSongSchema']) => {
		await client.DELETE('/api/tag/alias', {
			fetch,
			params: { query: { tag_slug: data.tag.slug, alias: alias.slug, type: 'song' } }
		});
		invalidateAll();
	};

	const setBase = async (tag: components['schemas']['TagSongSchema']) => {
		await client.POST('/api/tag/set_base', {
			fetch,
			params: { query: { tag_slug: tag.slug, type: 'song' } }
		});
		goto(`/song_attribute/${tag.slug}/`, { invalidateAll: true });
	};

	const submitLangPref = async (lang: number, tag_slug: string) => {
		const p = client.PUT('/api/tag/lang_pref', {
			fetch,
			params: { query: { lang, tag_slug, type: 'song' } }
		});
		callSavingToast(p);
		await p;
		invalidateAll();
	};

	const del = async () => {
		const { response } = await client.DELETE('/api/tag/tag', {
			fetch,
			params: { query: { tag_slug: data.tag.slug, type: 'song' } }
		});
		if (response.ok) {
			goto('/', { invalidateAll: true });
		} else if (response.status === 400) {
			callErrorToast(m.flat_fuzzy_pug_sway());
		}
	};
</script>

<Section title={data.tag.name} type={m.dull_plain_angelfish_cuddle()} menuLinks={data.links}>
	<GuidelineWarning />
	<form method="POST" use:enhance action="?/edit">
		<table>
			<tbody>
				<tr>
					<th><label for="category">{m.plane_awful_bobcat_spark()}</label></th>
					<td
						><select name="category" bind:value={category}>
							{#each SongTagCategory as cat, i (i)}
								<option value={i}>{cat()}</option>
							{/each}
						</select></td
					>
				</tr>
				<tr>
					<th><label for="parent">{m.away_crisp_blackbird_twist()}</label></th>
					<td
						><TagField
							type="song"
							name="parent"
							value={form?.parent_slug ?? data.tree?.at(-1)?.slug ?? ''}
						/></td
					>
				</tr>
			</tbody>
		</table>
		<input type="submit" />
	</form>
	<button onclick={del}>{m.proof_merry_chicken_bump()}</button>
</Section>

<Section title={m.alive_lofty_opossum_laugh()}>
	{#if data.aliases.length}
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
					><td><input type="text" bind:value={tagNames[data.tag.slug]} /></td>
					{#each locales as locale, i (i)}
						<td
							><input
								type="radio"
								bind:group={tagLangPrefs[locale]}
								value={data.tag.slug}
								onclick={() => submitLangPref(Languages[locale], data.tag.slug)}
							/>{#if tagLangPrefs[locale] === null}{m.factual_house_antelope_arise()}{/if}</td
						>
					{/each}<td>{m.simple_less_marlin_enchant()}</td></tr
				>
				{#each data.aliases as a, i (i)}
					<tr
						><td><input type="text" bind:value={tagNames[a.slug]} /></td>
						{#each locales as locale, i (i)}
							<td
								><input
									type="radio"
									bind:group={tagLangPrefs[locale]}
									value={a.slug}
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
	<a href="/song_attribute/alias?from={data.tag.slug}">{m.weary_moving_swallow_chop()}</a>
</Section>
