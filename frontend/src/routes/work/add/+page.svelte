<script lang="ts">
	import Section from '$lib/Section.svelte';
	import { m } from '$lib/paraglide/messages.js';
	import type { PageProps } from './$types';
	import { enhance } from '$app/forms';
	import { callErrorToast } from '$lib/toast';

	let { data, form }: PageProps = $props();

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
						<select name="origin" value={form?.origin ?? !data.title}>
							<option value={true}>{m.broad_large_squid_zoom()}</option>
							<option value={false}>{m.great_lucky_goldfish_sail()}</option>
						</select>
					</td>
				</tr>
			</tbody>
		</table>
		<input class="mt-4" type="submit" />
	</form>
</Section>
