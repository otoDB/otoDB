<script lang="ts">
	import Section from '$lib/Section.svelte';
	import type { PageProps } from './$types';
	import { m } from '$lib/paraglide/messages.js';
	import client from '$lib/api';
	import LoadMoreButton from '$lib/LoadMoreButton.svelte';
	import TagsField from '$lib/TagsField.svelte';

	let { data }: PageProps = $props();
	let results = $derived(data.results!.items);

	const fetchNextBatch = () =>
		client.GET('/api/tag/song_search', {
			fetch,
			params: {
				query: {
					query: data.query,
					tags: data.query_tags,
					author: data.author,
					limit: data.batch_size,
					offset: results.length,
					bpm_range: data.bpm_range
				}
			}
		});
</script>

<svelte:head>
	<title
		>{m.mild_loud_shad_enchant({
			type: m.mean_top_antelope_love(),
			name: m.grand_nice_pony_belong()
		})}</title
	>
</svelte:head>

<Section
	title={m.mild_loud_shad_enchant({
		type: m.mean_top_antelope_love(),
		name: m.grand_nice_pony_belong()
	})}
	menuLinks={[
		{ title: m.grand_merry_fly_succeed(), pathname: `work/search?query=${data.query}` },
		{ title: m.empty_legal_chicken_taste(), pathname: `tag/search?query=${data.query}` },
		{ title: m.grand_nice_pony_belong(), pathname: `song/search` },
		{ title: m.stale_loose_squid_cut(), pathname: `list/search?query=${data.query}` }
	]}
>
	<form target="_self" method="get">
		<input
			type="text"
			name="query"
			placeholder="{m.mean_top_antelope_love()}..."
			value={data.query}
		/>
		<input
			type="text"
			name="author"
			placeholder={m.crisp_red_canary_tickle()}
			value={data.author}
		/>
		<input type="submit" value={m.mean_top_antelope_love()} />
		<h4>{m.mild_loud_shad_enchant({ type: m.empty_legal_chicken_taste(), name: '' })}</h4>
		<TagsField type="song" name="tags" value={data.query_tags.split(' ')} class="w-full" />
		<h4>BPM</h4>
		<input type="number" step="any" min="0" name="bpm_min" value={data.bpm_range?.[0]} />
		-
		<input type="number" step="any" min="0" name="bpm_max" value={data.bpm_range?.[1]} />
	</form>

	<hr class="my-5" />

	<table class="w-full">
		<thead>
			<tr>
				<th>{m.large_factual_octopus_exhale()}</th>
				<th>{m.crisp_red_canary_tickle()}</th>
				<th>BPM</th>
			</tr>
		</thead><tbody>
			{#each results as song, i (i)}
				<tr>
					<td><a href="/tag/{song.work_tag}">#{song.id} - {song.title}</a></td>
					<td>{song.author}</td>
					<td
						>{#if song.variable_bpm && song.bpm}{m.big_helpful_tortoise_swim()}({song.bpm}){:else if song.bpm}{song.bpm}{:else}{m.big_helpful_tortoise_swim()}{/if}</td
					>
				</tr>
			{/each}
		</tbody>
	</table>
	<LoadMoreButton {fetchNextBatch} maxCount={data.results!.count} bind:results />
</Section>
