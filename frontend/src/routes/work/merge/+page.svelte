<script lang="ts">
	import Section from '$lib/Section.svelte';
	import { m } from '$lib/paraglide/messages.js';
	import WorkField from '$lib/WorkField.svelte';
	import type { components } from '$lib/schema';
	import { Platform, Rating, WorkOrigin } from '$lib/enums';
	import client from '$lib/api';

	let work: {
		work: components['schemas']['WorkSchema'] | null;
		title: string;
		description: string;
		thumbnail_source_id: number | null;
		rating: number;
	}[] = $state([
		{
			work: null,
			title: '',
			description: '',
			thumbnail_source_id: null,
			rating: 0
		},
		{
			work: null,
			title: '',
			description: '',
			thumbnail_source_id: null,
			rating: 0
		}
	]);

	async function updateInfo(i: number) {
		if (work[i].work) {
			const { data } = await client.GET('/api/work/work', {
				fetch,
				params: { query: { work_id: work[i].work.id } }
			});
			if (data) {
				work[i].work = data;
				work[i].title = data.title;
				work[i].thumbnail_source_id =
					data.thumbnail_source ?? data.sources?.[0]?.id ?? null;
				work[i].description = data.description!;
				work[i].rating = data.rating;
			}
		} else {
			work[i].work = null;
			work[i].title = '';
			work[i].thumbnail_source_id = null;
			work[i].description = '';
			work[i].rating = 0;
		}
	}

	let selecting = $state({
		title: 0,
		description: 0,
		thumbnail_source: 0,
		rating: 0
	});
</script>

<svelte:head>
	<title>{m.heroic_same_wasp_conquer()}</title>
</svelte:head>

<Section title={m.heroic_same_wasp_conquer()}>
	<form method="POST">
		<table>
			<tbody>
				<tr
					><th></th>
					<td>
						<WorkField bind:value={work[0].work} oninput={() => updateInfo(0)} />
					</td>
					<td></td><td></td>
					<td>
						<WorkField bind:value={work[1].work} oninput={() => updateInfo(1)} />
					</td>
					<th></th></tr
				>
				<tr
					><th>{m.large_factual_octopus_exhale()}</th>
					<td
						><input
							type="text"
							disabled={!work[0].work || selecting.title !== 0}
							bind:value={work[0].title}
						/></td
					>
					<td
						><input
							type="radio"
							disabled={!work[0].work}
							value={0}
							bind:group={selecting.title}
						/></td
					>
					<td
						><input
							type="radio"
							disabled={!work[1].work}
							value={1}
							bind:group={selecting.title}
						/></td
					>
					<td
						><input
							type="text"
							disabled={!work[1].work || selecting.title !== 1}
							bind:value={work[1].title}
						/></td
					>
					<th>{m.large_factual_octopus_exhale()}</th></tr
				>
				<tr
					><th>{m.clear_lucky_peacock_pick()}</th>
					<td
						><textarea
							disabled={!work[0].work || selecting.description !== 0}
							bind:value={work[0].description}
						></textarea></td
					>
					<td
						><input
							type="radio"
							disabled={!work[0].work}
							value={0}
							bind:group={selecting.description}
						/></td
					>
					<td
						><input
							type="radio"
							disabled={!work[1].work}
							value={1}
							bind:group={selecting.description}
						/></td
					>
					<td
						><textarea
							disabled={!work[1].work || selecting.description !== 1}
							bind:value={work[1].description}
						></textarea></td
					>
					<th>{m.clear_lucky_peacock_pick()}</th></tr
				>
				<tr
					><th>{m.heroic_ideal_orangutan_aid()}</th>
					<td>
						{#if work[0].work?.sources && work[0].work.sources.length > 0}
							<select
								disabled={!work[0].work || selecting.thumbnail_source !== 0}
								bind:value={work[0].thumbnail_source_id}
							>
								{#each work[0].work.sources as source}
									<option value={source.id}
										>{Platform[source.platform]}
										{source.work_origin === 0
											? ''
											: ' ' + WorkOrigin[source.work_origin]()}
										-
										{source.title}</option
									>
								{/each}
							</select>
							{@const selectedSource = work[0].work.sources.find(
								(s) => s.id === work[0].thumbnail_source_id
							)}
							{#if selectedSource?.thumbnail}
								<img
									class="w-15 mt-2"
									src={selectedSource.thumbnail}
									alt={work[0].title}
								/>
							{/if}
						{:else}
							No sources available
						{/if}
					</td>
					<td
						><input
							type="radio"
							disabled={!work[0].work}
							value={0}
							bind:group={selecting.thumbnail_source}
						/></td
					>
					<td
						><input
							type="radio"
							disabled={!work[1].work}
							value={1}
							bind:group={selecting.thumbnail_source}
						/></td
					>
					<td>
						{#if work[1].work?.sources && work[1].work.sources.length > 0}
							<select
								disabled={!work[1].work || selecting.thumbnail_source !== 1}
								bind:value={work[1].thumbnail_source_id}
							>
								{#each work[1].work.sources as source}
									<option value={source.id}>{source.title}</option>
								{/each}
							</select>
							{@const selectedSource = work[1].work.sources.find(
								(s) => s.id === work[1].thumbnail_source_id
							)}
							{#if selectedSource?.thumbnail}
								<img
									class="w-15 mt-2"
									src={selectedSource.thumbnail}
									alt={work[1].title}
								/>
							{/if}
						{:else}
							No sources available
						{/if}
					</td>
					<th>{m.heroic_ideal_orangutan_aid()}</th></tr
				>
				<tr
					><th>{m.good_dark_bumblebee_spur()}</th>
					<td
						><select
							disabled={!work[0].work || selecting.rating != 0}
							bind:value={work[0].rating}
						>
							{#each Rating as r, i (i)}<option value={i}>{r()}</option>{/each}
						</select></td
					>
					<td
						><input
							type="radio"
							disabled={!work[0].work}
							value={0}
							bind:group={selecting.rating}
						/></td
					>
					<td
						><input
							type="radio"
							disabled={!work[1].work}
							value={1}
							bind:group={selecting.rating}
						/></td
					>
					<td
						><select
							disabled={!work[1].work || selecting.rating != 1}
							bind:value={work[1].rating}
						>
							{#each Rating as r, i (i)}<option value={i}>{r()}</option>{/each}
						</select></td
					>
					<th>{m.good_dark_bumblebee_spur()}</th></tr
				>
			</tbody>
		</table>
		<input hidden type="number" name="A" value={work[0].work?.id} />
		<input hidden type="number" name="B" value={work[1].work?.id} />
		<input hidden type="text" name="title" value={work[selecting.title].title} />
		<textarea hidden value={work[selecting.description].description} name="description"
		></textarea>
		<input
			hidden
			type="number"
			value={work[selecting.thumbnail_source].thumbnail_source_id}
			name="thumbnail_source_id"
		/>
		<input hidden type="number" name="rating" value={work[selecting.rating].rating} />
		<input type="submit" disabled={!work[0].work || !work[1].work} />
	</form>
</Section>
