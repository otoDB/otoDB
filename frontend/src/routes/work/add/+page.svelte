<script lang="ts">
	import Section from '$lib/Section.svelte';
	import { m } from '$lib/paraglide/messages.js';
	import type { PageProps } from './$types';
	import { enhance } from '$app/forms';
	import { Rating } from '$lib/enums';
	import { callErrorToast } from '$lib/toast';

	let { data, form }: PageProps = $props();
	let isReupload = $derived(Boolean(form?.origin === false || data.title));

	$effect(() => {
		if (form?.failed) {
			callErrorToast(form.message);
		}
	});
</script>

<svelte:head>
	<title>
		{data.title
			? m.mild_loud_shad_enchant({ type: m.helpful_away_jay_succeed(), name: data.title })
			: m.helpful_away_jay_succeed()}
	</title>
</svelte:head>

<Section
	title={data.title
		? m.mild_loud_shad_enchant({ type: m.helpful_away_jay_succeed(), name: data.title })
		: m.helpful_away_jay_succeed()}
>
	<p>{m.mild_loud_shad_enchant({ type: m.fit_noble_niklas_build(), name: '' })}</p>
	<ul>
		<li>YouTube</li>
		<li>Niconico</li>
		<li>Bilibili</li>
		<li>SoundCloud</li>
	</ul>
	<form method="POST" use:enhance class="mt-4">
		<table>
			<tbody>
				<tr>
					<th class="w-min whitespace-nowrap">
						<label for="url">URL</label>
					</th>
					<td class="w-full">
						<input
							required
							type="text"
							name="url"
							value={form?.url ?? data.link ?? ''}
							class="w-full"
						/>
					</td>
				</tr>
				<tr>
					<th class="w-min whitespace-nowrap">
						<label for="origin">{m.watery_fuzzy_fireant_thrive()}</label>
					</th>
					<td class="w-full">
						<select bind:value={isReupload}>
							<option value={true}>{m.broad_large_squid_zoom()}</option>
							<option value={false}>{m.great_lucky_goldfish_sail()}</option>
						</select>
					</td>
				</tr>
				{#if isReupload}
					<tr>
						<th><label for="original_url">{m.crisp_steep_angelfish_bump()}</label></th>
						<td><input type="text" name="original_url" /></td>
					</tr>
				{/if}
				{#if data.isNewWork}
					<tr
						><th><label for="rating">{m.good_dark_bumblebee_spur()}</label></th><td
							><select name="rating">
								{#each Rating as r, i (i)}<option value={i}>{r()}</option
									>{/each}</select
							></td
						></tr
					>
				{/if}
			</tbody>
		</table>
		<input class="mt-4" type="submit" />
	</form>
</Section>
