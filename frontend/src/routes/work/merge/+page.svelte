<script lang="ts">
	import Section from '$lib/Section.svelte';
	import { m } from '$lib/paraglide/messages.js';
	import WorkField from '$lib/WorkField.svelte';
	import { Rating, type components } from '$lib/schema';
	import { enumValues, PlatformNames, RatingNames, WorkOriginNames } from '$lib/enums';
	import client, { getDisplayText } from '$lib/api';
	import GuidelineWarning from '$lib/GuidelineWarning.svelte';
	import WorkThumbnail from '$lib/WorkThumbnail.svelte';
	import type { ComponentProps } from 'svelte';

	let work: Record<
		'a' | 'b',
		{
			work: null | ComponentProps<typeof WorkField>['value'];
			title: string;
			description: string;
			thumbnail_source_id: number | null;
			rating: Rating;
			sources: null | components['schemas']['WorkSourceSchema'][];
		}
	> = $state({
		a: {
			work: null,
			title: '',
			description: '',
			thumbnail_source_id: null,
			rating: 0,
			sources: null
		},
		b: {
			work: null,
			title: '',
			description: '',
			thumbnail_source_id: null,
			rating: 0,
			sources: null
		}
	});

	async function updateInfo(i: keyof typeof work) {
		if (work[i].work) {
			const [workResponse, sourcesResponse] = await Promise.all([
				client.GET('/api/work/work', {
					fetch,
					params: { query: { work_id: work[i].work.id } }
				}),
				client.GET('/api/work/sources', {
					fetch,
					params: { query: { work_id: work[i].work.id } }
				})
			]);

			if (workResponse.data && sourcesResponse.data) {
				work[i].work = workResponse.data;
				work[i].title = workResponse.data.title || '';
				work[i].description = workResponse.data.description || '';
				work[i].rating = workResponse.data.rating;

				work[i].sources = sourcesResponse.data;
				work[i].thumbnail_source_id =
					workResponse.data?.thumbnail_source ?? sourcesResponse.data?.[0]?.id ?? null;
			}
		} else {
			work[i].work = null;
			work[i].title = '';
			work[i].thumbnail_source_id = null;
			work[i].description = '';
			work[i].rating = 0;
		}
	}

	let selectingTitle = $state<keyof typeof work>('a');
	let selectingDescription = $state<keyof typeof work>('a');
	let selectingThumbnailSource = $state<keyof typeof work>('a');
	let selectingRating = $state<keyof typeof work>('a');
</script>

<Section title={m.heroic_same_wasp_conquer()}>
	<GuidelineWarning />
	<form method="POST">
		<table>
			<tbody>
				<tr
					><th></th>
					<td>
						<WorkField bind:value={work['a'].work} oninput={() => updateInfo('a')} />
					</td>
					<td></td><td></td>
					<td>
						<WorkField bind:value={work['b'].work} oninput={() => updateInfo('b')} />
					</td>
					<th></th></tr
				>
				<tr
					><th>{m.large_factual_octopus_exhale()}</th>
					<td
						><input
							type="text"
							disabled={!work['a'].work || selectingTitle !== 'a'}
							bind:value={work['a'].title}
						/></td
					>
					<td
						><input
							type="radio"
							disabled={!work['a'].work}
							value="a"
							bind:group={selectingTitle}
						/></td
					>
					<td
						><input
							type="radio"
							disabled={!work['b'].work}
							value="b"
							bind:group={selectingTitle}
						/></td
					>
					<td
						><input
							type="text"
							disabled={!work['b'].work || selectingTitle !== 'b'}
							bind:value={work['b'].title}
						/></td
					>
					<th>{m.large_factual_octopus_exhale()}</th></tr
				>
				<tr
					><th>{m.clear_lucky_peacock_pick()}</th>
					<td
						><textarea
							disabled={!work['a'].work || selectingDescription !== 'a'}
							bind:value={work['a'].description}
						></textarea></td
					>
					<td
						><input
							type="radio"
							disabled={!work['a'].work}
							value="a"
							bind:group={selectingDescription}
						/></td
					>
					<td
						><input
							type="radio"
							disabled={!work['b'].work}
							value="b"
							bind:group={selectingDescription}
						/></td
					>
					<td
						><textarea
							disabled={!work['b'].work || selectingDescription !== 'b'}
							bind:value={work['b'].description}
						></textarea></td
					>
					<th>{m.clear_lucky_peacock_pick()}</th></tr
				>
				<tr
					><th>{m.heroic_ideal_orangutan_aid()}</th>
					<td>
						{#if work['a'].sources && work['a'].sources.length > 0}
							<select
								disabled={!work['a'].work || selectingThumbnailSource !== 'a'}
								bind:value={work['a'].thumbnail_source_id}
							>
								{#each work['a'].sources as source (source.id)}
									<option value={source.id}
										>{PlatformNames[source.platform]}
										{source.work_origin === 0
											? ''
											: ' ' + WorkOriginNames[source.work_origin]()}
										-
										{source.title}</option
									>
								{/each}
							</select>
							{@const selectedSource = work['a'].sources.find(
								(s) => s.id === work['a'].thumbnail_source_id
							)}
							<WorkThumbnail
								class="mt-2 aspect-video w-15"
								thumbnail={selectedSource?.thumbnail}
								alt={getDisplayText(work['a'].title)}
							/>
						{/if}
					</td>
					<td
						><input
							type="radio"
							disabled={!work['a'].work}
							value="a"
							bind:group={selectingThumbnailSource}
						/></td
					>
					<td
						><input
							type="radio"
							disabled={!work['b'].work}
							value="b"
							bind:group={selectingThumbnailSource}
						/></td
					>
					<td>
						{#if work['b'].sources && work['b'].sources.length > 0}
							<select
								disabled={!work['b'].work || selectingThumbnailSource !== 'b'}
								bind:value={work['b'].thumbnail_source_id}
							>
								{#each work['b'].sources as source (source.id)}
									<option value={source.id}>{source.title}</option>
								{/each}
							</select>
							{@const selectedSource = work['b'].sources.find(
								(s) => s.id === work['b'].thumbnail_source_id
							)}
							<WorkThumbnail
								class="mt-2 aspect-video w-15"
								thumbnail={selectedSource?.thumbnail}
								alt={getDisplayText(work['b'].title)}
							/>
						{/if}
					</td>
					<th>{m.heroic_ideal_orangutan_aid()}</th></tr
				>
				<tr
					><th>{m.good_dark_bumblebee_spur()}</th>
					<td
						><select
							disabled={!work['a'].work || selectingRating !== 'a'}
							bind:value={work['a'].rating}
						>
							{#each enumValues(Rating) as r, i (i)}<option value={r}
									>{RatingNames[r]()}</option
								>{/each}
						</select></td
					>
					<td
						><input
							type="radio"
							disabled={!work['a'].work}
							value="a"
							bind:group={selectingRating}
						/></td
					>
					<td
						><input
							type="radio"
							disabled={!work['b'].work}
							value="b"
							bind:group={selectingRating}
						/></td
					>
					<td
						><select
							disabled={!work['b'].work || selectingRating !== 'b'}
							bind:value={work['b'].rating}
						>
							{#each enumValues(Rating) as r, i (i)}<option value={r}
									>{RatingNames[r]()}</option
								>{/each}
						</select></td
					>
					<th>{m.good_dark_bumblebee_spur()}</th></tr
				>
			</tbody>
		</table>
		<input hidden type="number" name="A" value={work['a'].work?.id} />
		<input hidden type="number" name="B" value={work['b'].work?.id} />
		<input
			hidden
			type="text"
			name="title"
			value={work[selectingTitle].title}
			autocomplete="off"
		/>
		<textarea hidden value={work[selectingDescription].description} name="description"
		></textarea>
		<input
			hidden
			type="number"
			value={work[selectingThumbnailSource].thumbnail_source_id}
			name="thumbnail_source_id"
		/>
		<input hidden type="number" name="rating" value={work[selectingRating].rating} />
		<input type="submit" disabled={!work['a'].work || !work['b'].work} />
	</form>
</Section>
