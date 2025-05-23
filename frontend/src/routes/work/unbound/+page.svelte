<script lang="ts">
	import Section from '$lib/Section.svelte';
	import type { PageProps } from './$types';
	import { m } from '$lib/paraglide/messages.js';
	import { Platform, WorkOrigin } from '$lib/enums';
	import { getLocale } from '$lib/paraglide/runtime';
	import RefreshButton from '../RefreshButton.svelte';
	import { invalidateAll } from '$app/navigation';
	import client from '$lib/api';
	import { isSOV, isSVO } from '$lib/ui';
	import WorkCard from '$lib/WorkCard.svelte';
	import WorkField from '$lib/WorkField.svelte';

	let { data }: PageProps = $props();

	let actions = $state(
		Array(data.sources.length).fill({
			reason: '',
			menu: 'none',
			suggestion_candidate: -1,
			specify_target: null
		})
	);
	let suggestions = $state(Array(data.sources.length).fill([]));
	let loaded = Array(data.sources.length).fill(false);
	const submit = async () => {
		await Promise.all(
			actions.map(async (v, i) => {
				if (v.menu === 'new')
					await client.POST('/api/work/assign_source', {
						fetch,
						params: {
							query: {
								source_id: data.sources[i].id,
								work_id:
									v.suggestion_candidate === -1
										? undefined
										: v.suggestion_candidate === 0
											? v.specify_target?.id
											: v.suggestion_candidate
							}
						}
					});
				else if (v.menu === 'reject')
					await client.POST('/api/work/reject_source', {
						fetch,
						params: { query: { source_id: data.sources[i].id, reason: v.reason } }
					});
			})
		);
		invalidateAll();
	};
	const unfold = async (i: number) => {
		if (!loaded[i] && actions[i].menu === 'new') {
			const { data: similar } = await client.GET('/api/work/search', {
				fetch,
				params: { query: { query: data.sources[i].title } }
			});
			if (similar) suggestions = similar.items;
			loaded[i] = true;
		}
	};
</script>

<svelte:head>
	<title>{m.suave_gray_stork_type()}</title>
</svelte:head>

<Section title={m.suave_gray_stork_type()} menuLinks={data.links}>
	{#if data.sources.length}
		<input type="submit" onclick={submit} />
		<table class="w-full">
			<thead
				><tr>
					<th>{m.knotty_due_hamster_wave()}</th>
					<th>{m.heroic_ideal_orangutan_aid()}</th>
					<th>No Action</th>
					<th>{m.lucky_bold_hornet_push()}</th>
					<th>{m.alive_blue_marlin_push()}</th>
				</tr></thead
			>
			<tbody>
				{#each data.sources as src, i (i)}
					<tr>
						<td>
							<h3>
								<a href={src.url} target="_blank" rel="noopener noreferrer"
									>{src.title}</a
								>
							</h3>
							<h4>
								{m.swift_sweet_anaconda_hurl()}
								<a href="/profile/{src.added_by.username}"
									>{src.added_by.username}</a
								>
							</h4>
							<h4>{Platform[src.platform]} {src.published_date}</h4>
							<h4>
								{m.mild_loud_shad_enchant({
									type: m.large_polite_otter_thrive(),
									name: WorkOrigin[src.work_origin]()
								})}
							</h4>
							<RefreshButton source={src} />
						</td>
						<td>
							<a href={src.url} target="_blank" rel="noopener noreferrer"
								><img
									src={src.thumbnail}
									alt={src.title}
									class="float-right clear-both w-50"
								/></a
							>
							{JSON.stringify(actions[i].menu)}
						</td>
						<td>
							<label>
								<input
									autocomplete="off"
									type="radio"
									value="none"
									bind:group={actions[i].menu}
								/>
								No action
							</label>
						</td>
						<td>
							<label>
								<input
									autocomplete="off"
									type="radio"
									value="new"
									bind:group={actions[i].menu}
									onchange={() => unfold(i)}
								/>
								{m.lucky_bold_hornet_push()}
							</label>
							{#if actions[i].menu === 'new'}
								{#if isSVO(getLocale())}
									{m.cute_neat_gull_greet()}
								{/if}
								<table>
									<thead>
										<tr><th></th><th>{m.grand_merry_fly_succeed()}</th></tr>
									</thead><tbody>
										{#each suggestions[i] as work, j (j)}
											<tr>
												<td
													><input
														type="radio"
														value={work.id}
														bind:group={actions[i].suggestion_candidate}
													/></td
												>
												<td><WorkCard {work} /></td>
											</tr>
										{/each}
										<tr>
											<td
												><input
													type="radio"
													value={-1}
													bind:group={actions[i].suggestion_candidate}
												/></td
											>
											<td>{m.careful_red_cow_evoke()}</td>
										</tr>
										<tr>
											<td
												><input
													type="radio"
													value={0}
													bind:group={actions[i].suggestion_candidate}
												/></td
											>
											<td>
												<WorkField value={actions[i].specify_target} />
											</td>
										</tr>
									</tbody>
								</table>
								{#if isSOV(getLocale())}
									{m.cute_neat_gull_greet()}
								{/if}
							{/if}
						</td>
						<td>
							<label>
								<input
									autocomplete="off"
									type="radio"
									value="reject"
									bind:group={actions[i].menu}
								/>
								{m.alive_blue_marlin_push()}
							</label>
							{#if actions[i].menu === 'reject'}
								<label
									>{m.weary_spicy_fly_attend()}
									<input
										type="text"
										bind:value={actions[i].reason}
										required
									/></label
								>
							{/if}
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	{:else}
		<h3>{m.moving_such_seal_hug()}</h3>
	{/if}
</Section>
