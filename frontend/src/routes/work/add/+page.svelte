<script lang="ts">
	import Section from '$lib/Section.svelte';
	import { m } from '$lib/paraglide/messages.js';
	import type { PageProps } from './$types';
	import { enhance } from '$app/forms';

	let { data, form }: PageProps = $props();
</script>

<svelte:head>
	<title
		>{data.title
			? m.mild_loud_shad_enchant({ type: m.helpful_away_jay_succeed(), name: data.title })
			: m.helpful_away_jay_succeed()}</title
	>
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
	<form method="POST" use:enhance>
		{#if form?.failed}<p class="error">{form.message}</p>{/if}
		<table>
			<tbody>
				<tr>
					<th><label for="url">URL</label></th>
					<td><input required type="text" name="url" value={form?.url ?? data.link ?? ''} /></td>
				</tr>
				<tr>
					<th><label for="origin">{m.watery_fuzzy_fireant_thrive()}</label></th>
					<td
						><input
							type="checkbox"
							name="origin"
							checked={form?.origin ?? !data.title}
						/></td
					>
				</tr>
			</tbody>
		</table>
		<input type="submit" />
	</form>
</Section>
