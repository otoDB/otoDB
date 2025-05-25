<script lang="ts">
	import Section from '$lib/Section.svelte';
	import type { PageProps } from './$types';
	import { m } from '$lib/paraglide/messages.js';
	import { Platform, WorkOrigin, WorkStatus } from '$lib/enums';
	import RefreshButton from '../../../work/RefreshButton.svelte';
	import client from '$lib/api';

	let { data }: PageProps = $props();
	let results = $state(data.submissions!.items);
	let page = $state(0);

	let approved = $derived(results.filter((s) => s.media));
	let pending = $derived(results.filter((s) => !s.media && !s.rejection_reason));
	let rejected = $derived(results.filter((s) => s.rejection_reason));

	$effect(() => {
		client
			.GET('/api/profile/submissions', {
				fetch,
				params: {
					query: {
						username: data.profile.username,
						limit: data.batch_size,
						offset: page * data.batch_size
					}
				}
			})
			.then(({ data }) => (results = data.items));
	});
</script>

<Section
	title={m.mild_loud_shad_enchant({
		type: m.fuzzy_crazy_cobra_lead(),
		name: data.profile.username
	})}
	menuLinks={data.links}
>
	{#if data.user?.username === data.profile.username}
		<a href="/work/add">{m.fluffy_crisp_horse_imagine()}</a>
	{/if}
	<h2>{m.such_actual_okapi_dare()}</h2>
	{#if pending?.length}
		<table class="w-full">
			<thead
				><tr>
					<th>{m.large_factual_octopus_exhale()}</th>
					<th>{m.sour_swift_sparrow_spin()}</th>
					<th>{m.super_agent_pigeon_aim()}</th>
					<th>{m.large_polite_otter_thrive()}</th>
					<th>{m.noisy_moving_newt_belong()}</th>
					{#if data.user}
						<th>{m.mushy_proof_hornet_dig()}</th>
					{/if}
				</tr></thead
			>
			<tbody>
				{#each pending as src, i (i)}
					<tr>
						<td class="whitespace-nowrap">{src.title}</td>
						<td>{Platform[src.platform]}</td><td>{src.published_date}</td>
						<td class="whitespace-nowrap">{WorkOrigin[src.work_origin]()}</td>
						<td class="whitespace-nowrap"
							><a href={src.url} target="_blank" rel="noopener noreferrer"
								>{m.noisy_moving_newt_belong()}</a
							></td
						>
						{#if data.user}
							<td><RefreshButton source={src} /></td>
						{/if}
					</tr>
				{/each}
			</tbody>
		</table>
	{:else}
		<p>{m.moving_such_seal_hug()}</p>
	{/if}

	<h2>{m.stale_vexed_hare_pray()}</h2>
	{#if rejected?.length}
		<table class="w-full">
			<thead
				><tr>
					<th>{m.large_factual_octopus_exhale()}</th>
					<th>{m.weary_spicy_fly_attend()}</th>
					<th>{m.sour_swift_sparrow_spin()}</th>
					<th>{m.super_agent_pigeon_aim()}</th>
					<th>{m.large_polite_otter_thrive()}</th>
					<th>{m.noisy_moving_newt_belong()}</th>
					{#if data.user}
						<th>{m.mushy_proof_hornet_dig()}</th>
					{/if}
				</tr></thead
			>
			<tbody>
				{#each rejected as src, i (i)}
					<tr>
						<td class="whitespace-nowrap">{src.title}</td>
						<td class="whitespace-nowrap">{src.rejection_reason}</td>
						<td>{Platform[src.platform]}</td><td>{src.published_date}</td>
						<td class="whitespace-nowrap">{WorkOrigin[src.work_origin]()}</td>
						<td class="whitespace-nowrap"
							><a href={src.url} target="_blank" rel="noopener noreferrer"
								>{m.noisy_moving_newt_belong()}</a
							></td
						>
						{#if data.user}
							<td><RefreshButton source={src} /></td>
						{/if}
					</tr>
				{/each}
			</tbody>
		</table>
	{:else}
		<p>{m.moving_such_seal_hug()}</p>
	{/if}

	<h2>{m.spare_few_kudu_learn()}</h2>
	{#if approved?.length}
		<table class="w-full">
			<thead
				><tr>
					<th>{m.large_factual_octopus_exhale()}</th>
					<th>{m.sour_swift_sparrow_spin()}</th>
					<th>{m.super_agent_pigeon_aim()}</th>
					<th>{m.large_polite_otter_thrive()}</th>
					<th>{m.civil_trick_oryx_clap()}</th>
					<th>{m.noisy_moving_newt_belong()}</th>
					{#if data.user}
						<th>{m.mushy_proof_hornet_dig()}</th>
					{/if}
				</tr></thead
			>
			<tbody>
				{#each approved as src, i (i)}
					<tr>
						<td class="whitespace-nowrap"
							><a href="/work/{src.media}">{src.title}</a></td
						>
						<td>{Platform[src.platform]}</td><td>{src.published_date}</td>
						<td class="whitespace-nowrap">{WorkOrigin[src.work_origin]()}</td><td
							class="whitespace-nowrap">{WorkStatus[src.work_status]()}</td
						>
						<td class="whitespace-nowrap"
							><a href={src.url} target="_blank" rel="noopener noreferrer"
								>{m.noisy_moving_newt_belong()}</a
							></td
						>
						{#if data.user}
							<td><RefreshButton source={src} /></td>
						{/if}
					</tr>
				{/each}
			</tbody>
		</table>
	{:else}
		<p>{m.moving_such_seal_hug()}</p>
	{/if}
	{#if data.submissions?.count}
		<div class="mt-3 flex justify-center gap-2">
			{#each Array(Math.ceil(data.submissions?.count / data.batch_size)).fill(undefined) as _, i (i)}
				<label class="inline-block border p-2">
					<input type="radio" value={i} bind:group={page} hidden />
					{i + 1}
				</label>
			{/each}
		</div>
	{/if}
</Section>

<style>
	h2 {
		font-size: larger;
		margin: 1rem 0 0.5rem 0;
		font-weight: 600;
	}
	label:has(input:checked) {
		background-color: var(--otodb-content-color);
		color: var(--otodb-bg-color);
	}
</style>
