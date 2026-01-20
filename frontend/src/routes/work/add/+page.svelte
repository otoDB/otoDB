<script lang="ts">
	import Section from '$lib/Section.svelte';
	import { m } from '$lib/paraglide/messages.js';
	import type { PageProps } from './$types';
	import { enhance } from '$app/forms';
	import { Rating, UserLevel, Platform } from '$lib/enums';
	import { callErrorToast } from '$lib/toast';
	import { getDisplayText } from '$lib/api';

	let { data, form }: PageProps = $props();
	let isOriginal = $derived(!!(form?.origin ?? !data.title));
	let isUnavailable = $derived(!!data.unavailable_source);

	$effect(() => {
		if (form?.failed) {
			callErrorToast(form.message);
		}
	});

	const title = data.title
		? m.mild_loud_shad_enchant({
				type: data.unavailable_source
					? m.new_aloof_camel_read()
					: m.helpful_away_jay_succeed(),
				name: getDisplayText(data.title)
			})
		: m.helpful_away_jay_succeed();

	let submitting = $state(false);
</script>

<svelte:head>
	<title>{title}</title>
</svelte:head>

<Section {title}>
	{#if !data.unavailable_source}
		<p>{m.mild_loud_shad_enchant({ type: m.fit_noble_niklas_build(), name: '' })}</p>
		<ul>
			{#each Platform.slice(1) as platform, i (i)}
				<li>{platform}</li>
			{/each}
		</ul>
	{/if}
	<form
		method="POST"
		use:enhance={({ cancel }) => {
			if (submitting) return cancel();
			submitting = true;
		}}
		class="mt-4"
	>
		<table>
			<tbody>
				{#if !data.unavailable_source}
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
							<select name="origin" bind:value={isOriginal}>
								<option value={true}>{m.broad_large_squid_zoom()}</option>
								<option value={false}>{m.great_lucky_goldfish_sail()}</option>
							</select>
						</td>
					</tr>
					{#if !isOriginal}
						<tr>
							<th
								><label for="original_url">{m.crisp_steep_angelfish_bump()}</label
								></th
							>
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
					{#if data.user?.level >= UserLevel.EDITOR}
						<tr>
							<th class="w-min whitespace-nowrap">
								<label for="isUnavailable">{m.that_large_mare_ascend()}</label>
							</th>
							<td class="w-full">
								<select id="isUnavailable" bind:value={isUnavailable}>
									<option value={false}>{m.great_lucky_goldfish_sail()}</option>
									<option value={true}>{m.broad_large_squid_zoom()}</option>
								</select>
							</td>
						</tr>
					{/if}
				{/if}
				{#if isUnavailable}
					<tr>
						<th><label for="manual_title">{m.large_factual_octopus_exhale()}</label></th
						>
						<td>
							<input
								type="text"
								name="manual_title"
								class="w-full"
								value={data.unavailable_source?.title}
							/>
						</td>
					</tr>
					<tr>
						<th
							><label for="manual_description">{m.clear_lucky_peacock_pick()}</label
							></th
						>
						<td
							><textarea
								name="manual_description"
								class="w-full"
								rows="3"
								value={data.unavailable_source?.description}
							></textarea></td
						>
					</tr>
					<tr>
						<th
							><label for="manual_uploader_id"
								>{m.vivid_still_bumblebee_explore()}</label
							></th
						>
						<td
							><input
								type="text"
								name="manual_uploader_id"
								class="w-full"
								value={data.unavailable_source?.uploader_id}
							/></td
						>
					</tr>
					<tr>
						<th
							><label for="manual_thumbnail_url"
								>{m.heroic_ideal_orangutan_aid()}</label
							></th
						>
						<td
							><input
								type="url"
								name="manual_thumbnail_url"
								class="w-full"
								value={data.unavailable_source?.thumbnail}
							/></td
						>
					</tr>
					<tr>
						<th><label for="manual_width">{m.big_dry_seahorse_succeed()}</label></th>
						<td>
							<input
								type="number"
								id="manual_width"
								name="manual_width"
								min="0"
								placeholder={m.home_yummy_eel_scold()}
								value={data.unavailable_source?.work_width}
							/>
							x
							<input
								type="number"
								id="manual_height"
								name="manual_height"
								min="0"
								placeholder={m.legal_strong_ladybug_fade()}
								value={data.unavailable_source?.work_height}
							/>
						</td>
					</tr>
					<tr>
						<th><label for="manual_duration">{m.nice_tense_mule_grasp()}</label></th>
						<td
							><input
								type="number"
								name="manual_duration"
								min="0"
								value={data.unavailable_source?.work_duration}
							/></td
						>
					</tr>
					<tr>
						<th><label for="manual_date">{m.super_agent_pigeon_aim()}</label></th>
						<td
							><input
								type="date"
								name="manual_date"
								value={data.unavailable_source?.published_date}
							/></td
						>
					</tr>
				{/if}
			</tbody>
		</table>
		<input disabled={submitting} class="mt-4" type="submit" />
	</form>
</Section>
