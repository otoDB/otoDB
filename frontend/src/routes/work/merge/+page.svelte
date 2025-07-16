<script lang="ts">
	import Section from '$lib/Section.svelte';
	import { m } from '$lib/paraglide/messages.js';
	import WorkField from '$lib/WorkField.svelte';
	import type { components } from '$lib/schema';
	import { Rating } from '$lib/enums';

	let work: {
		work: components['schemas']['WorkSchema'] | null;
		title: string;
		description: string;
		thumbnail: string;
		rating: number;
	}[] = $state([
		{
			work: null,
			title: '',
			description: '',
			thumbnail: '',
			rating: 0
		},
		{
			work: null,
			title: '',
			description: '',
			thumbnail: '',
			rating: 0
		}
	]);

	function updateInfo(i: number) {
		if (work[i].work) {
			work[i].title = work[i].work.title;
			work[i].thumbnail = work[i].work.thumbnail!;
			work[i].description = work[i].work.description!;
			work[i].rating = work[i].work.rating;
		} else {
			work[i].title = '';
			work[i].thumbnail = '';
			work[i].description = '';
			work[i].rating = 0;
		}
	}

	let selecting = $state({
		title: 0,
		description: 0,
		thumbnail: 0,
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
					<td
						><input
							type="text"
							disabled={!work[0].work || selecting.thumbnail !== 0}
							bind:value={work[0].thumbnail}
						/><img class="w-15" src={work[0].thumbnail} alt={work[0].title} /></td
					>
					<td
						><input
							type="radio"
							disabled={!work[0].work}
							value={0}
							bind:group={selecting.thumbnail}
						/></td
					>
					<td
						><input
							type="radio"
							disabled={!work[1].work}
							value={1}
							bind:group={selecting.thumbnail}
						/></td
					>
					<td
						><input
							type="text"
							disabled={!work[1].work || selecting.thumbnail !== 1}
							bind:value={work[1].thumbnail}
						/><img class="w-15" src={work[1].thumbnail} alt={work[1].title} /></td
					>
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
		<input hidden type="text" value={work[selecting.thumbnail].thumbnail} name="thumbnail" />
		<input hidden type="number" name="rating" value={work[selecting.rating].rating} />
		<input type="submit" disabled={!work[0] || !work[1]} />
	</form>
</Section>
