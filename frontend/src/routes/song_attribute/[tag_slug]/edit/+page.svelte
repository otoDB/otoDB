<script lang="ts">
	import { enhance } from '$app/forms';
	import { goto } from '$app/navigation';
	import GuidelineWarning from '$lib/GuidelineWarning.svelte';
	import Section from '$lib/Section.svelte';
	import TagField from '$lib/TagField.svelte';
	import client from '$lib/api';
	import { dirtyEnhance } from '$lib/dirty';
	import { SongTagCategory } from '$lib/enums';
	import { languages } from '$lib/enums/Languages.js';
	import { m } from '$lib/paraglide/messages.js';
	import { locales } from '$lib/paraglide/runtime';
	import {
		PathsApiTagTag_aliasesPostParametersQueryType,
		PathsApiTagTagDeleteParametersQueryType
	} from '$lib/schema.js';
	import { callErrorCodeToast, callErrorToast } from '$lib/toast';

	let { data, form } = $props();

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
				data.tag.lang_prefs.find(({ lang }) => lang === languages[l].id)?.slug ?? null
			])
		) as Record<keyof typeof languages, string | null>
	);
	let tagNames: Record<string, string> = $state(
		Object.fromEntries([
			[data.tag.slug, data.tag.name],
			...data.aliases.map((a) => [a.slug, a.name])
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
					Object.entries(tagLangPrefs).map(([k, v]) => [
						languages[k as keyof typeof languages].id,
						v
					])
				),
				names: tagNames
			},
			params: {
				query: {
					type: PathsApiTagTag_aliasesPostParametersQueryType.song,
					tag_slug: data.tag.slug
				}
			}
		});
		if (error) {
			aliases_post_gate.p = Promise.withResolvers<void>();
			if (error && typeof error === 'object' && 'code' in error) {
				callErrorCodeToast(error.code, error.data ?? {});
			} else {
				callErrorToast(m.green_due_javelina_pop());
			}
		} else goto(`/song_attribute/${base}/`, { invalidateAll: true });
	};

	const del = async () => {
		const { response } = await client.DELETE('/api/tag/tag', {
			fetch,
			params: {
				query: {
					tag_slug: data.tag.slug,
					type: PathsApiTagTagDeleteParametersQueryType.song
				}
			}
		});
		if (response.ok) {
			goto('/', { invalidateAll: true });
		} else if (response.status === 400) {
			callErrorToast(m.flat_fuzzy_pug_sway());
		}
	};

	const form_barrier = {};
</script>

<Section title={data.tag.name} type={m.dull_plain_angelfish_cuddle()} menuLinks={data.links}>
	<GuidelineWarning />
	<form
		method="POST"
		use:enhance
		action="?/edit"
		use:dirtyEnhance={{ barrier: form_barrier, priority: 0 }}
	>
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
	<a href="/song_attribute/alias?from={data.tag.slug}">{m.weary_moving_swallow_chop()}</a>
	<form
		method="POST"
		use:dirtyEnhance={{
			barrier: form_barrier,
			priority: 1,
			manual_post: aliases_post_gate
		}}
		onsubmit={submit_aliases}
	>
		{#if data.aliases.length}
			<table>
				<thead>
					<tr
						><th>{m.alive_lofty_opossum_laugh()}</th>
						{#each locales as locale, i (i)}
							<th>{languages[locale].name} {m.mellow_upper_finch_drip()}</th>
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
					{#each data.aliases as a, i (i)}
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
