<script lang="ts">
	import Section from '$lib/Section.svelte';
	import type { PageProps } from './$types';
	import { m } from '$lib/paraglide/messages.js';
	import { Platform, WorkOrigin, WorkStatus } from '$lib/enums';
	import RefreshButton from '../../../work/RefreshButton.svelte';

	let { data }: PageProps = $props();
</script>

<svelte:head>
	<title
		>{m.mild_loud_shad_enchant({
			type: m.fuzzy_crazy_cobra_lead(),
			name: data.profile.username
		})}</title
	>
</svelte:head>

<Section
	title={m.mild_loud_shad_enchant({
		type: m.fuzzy_crazy_cobra_lead(),
		name: data.profile.username
	})}
	menuLinks={data.links}
>
	{#if data.user?.username === data.profile.username}
		<a href="/work/add">Add a work...</a>
	{/if}

	<h2>Pending</h2>
	{#if data.pending?.length}
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
				<!-- eslint-disable-next-line svelte/require-each-key -->
				{#each data.pending as src}
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
		<p>No pending submissions.</p>
	{/if}

	<h2>Rejected</h2>
	{#if data.rejected?.length}
		<table class="w-full">
			<thead
				><tr>
					<th>{m.large_factual_octopus_exhale()}</th>
					<th>Rejection reason</th>
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
				<!-- eslint-disable-next-line svelte/require-each-key -->
				{#each data.rejected as src}
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
		<p>No rejected submissions.</p>
	{/if}

	<h2>Approved</h2>
	{#if data.approved?.length}
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
				<!-- eslint-disable-next-line svelte/require-each-key -->
				{#each data.approved as src}
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
		<p>No approved submissions.</p>
	{/if}
</Section>
