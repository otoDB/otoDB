<script lang="ts">
	import { page } from '$app/state';
	import {
		enumValues,
		PlatformNames,
		SubmissionStandingNames,
		WorkOriginNames,
		WorkStatusNames
	} from '$lib/enums';
	import { hasUserLevel } from '$lib/enums/userLevel.js';
	import Pager from '$lib/Pager.svelte';
	import { m } from '$lib/paraglide/messages.js';
	import RefreshButton from '$lib/RefreshButton.svelte';
	import { Levels, Platform, SubmissionStanding, WorkOrigin, WorkStatus } from '$lib/schema.js';
	import Section from '$lib/Section.svelte';

	let { data } = $props();

	const standing = $derived(data.standing ?? SubmissionStanding.Approved);
	const isBound = $derived(
		standing === SubmissionStanding.Approved ||
			standing === SubmissionStanding.Delisted ||
			standing === SubmissionStanding.Flagged ||
			standing === SubmissionStanding.Appealed
	);
	const canRefresh = $derived(
		isBound ? !!data.user : hasUserLevel(data.user?.level, Levels.Editor)
	);
</script>

<Section title={data.profile.username} type={m.fuzzy_crazy_cobra_lead()} menuLinks={data.links}>
	{#if data.user?.username === data.profile.username}
		<a href="/upload/add">{m.fluffy_crisp_horse_imagine()}</a>
	{/if}
	<form target="_self" method="get">
		<table>
			<caption>{m.livid_same_wren_create()}</caption>
			<tbody>
				<tr>
					<td>{m.just_noisy_moth_beam()}</td>
					<td
						><select name="standing" value={standing}
							>{#each enumValues(SubmissionStanding) as p, i (i)}<option value={p}
									>{SubmissionStandingNames[p]()}</option
								>{/each}</select
						></td
					>
				</tr>
				<tr>
					<td>{m.sour_swift_sparrow_spin()}</td>
					<td
						><select name="platform" value={data.platform ?? null}
							><option value={null}>---</option>{#each enumValues(Platform) as p, i (i)}<option
									value={p}>{PlatformNames[p]}</option
								>{/each}</select
						></td
					>
				</tr>
				<tr>
					<td>{m.large_polite_otter_thrive()}</td>
					<td
						><select name="origin" value={data.origin ?? null}
							><option value={null}>---</option><option value={WorkOrigin.Author}
								>{WorkOriginNames[0]()}</option
							><option value={WorkOrigin.Reupload}>{WorkOriginNames[1]()}</option></select
						></td
					>
				</tr>
				<tr>
					<td>{m.civil_trick_oryx_clap()}</td>
					<td
						><select name="status" value={data.status ?? null}
							><option value={null}>---</option><option value={WorkStatus.Available}
								>{WorkStatusNames[WorkStatus.Available]()}</option
							><option value={WorkStatus.Down}>{WorkStatusNames[WorkStatus.Down]()}</option></select
						></td
					>
				</tr>
				<tr>
					<td>{m.good_heavy_mayfly_spin()}</td>
					<td>
						<select name="order" value={data.order ?? 'id'}
							><option value="id">{m.kind_vivid_niklas_savor()}</option><option
								value="published_date">{m.swift_each_zebra_assure()}</option
							></select
						>
						<select name="dir" value={data.dir ?? '-'}
							><option value="-">{m.kind_quick_bullock_push()}</option><option value=""
								>{m.novel_orange_mantis_feast()}</option
							></select
						>
					</td>
				</tr>
			</tbody>
		</table>
		<input type="submit" />
	</form>
	<hr class="my-2" />
	<h2>{SubmissionStandingNames[standing]()}</h2>
	{#if data.submissions?.items.length}
		<table class="w-full">
			<thead
				><tr>
					<th>{m.large_factual_octopus_exhale()}</th>
					<th>{m.sour_swift_sparrow_spin()}</th>
					<th>{m.super_agent_pigeon_aim()}</th>
					<th>{m.large_polite_otter_thrive()}</th>
					{#if isBound}
						<th>{m.civil_trick_oryx_clap()}</th>
					{/if}
					<th>{m.noisy_moving_newt_belong()}</th>
					{#if canRefresh}
						<th>{m.mushy_proof_hornet_dig()}</th>
					{/if}
				</tr></thead
			>
			<tbody>
				{#each data.submissions.items as src, i (i)}
					<tr>
						<td class="whitespace-nowrap">
							{#if isBound}
								<a href="/work/{src.media}">#{src.media} - {src.title || src.url}</a>
							{:else}
								<a href="/upload/{src.id}">{src.title || src.url}</a>
							{/if}
						</td>
						<td>{PlatformNames[src.platform]}</td><td>{src.published_date}</td>
						<td class="whitespace-nowrap">{WorkOriginNames[src.work_origin]()}</td>
						{#if isBound}
							<td class="whitespace-nowrap">{WorkStatusNames[src.work_status]()}</td>
						{/if}
						<td class="whitespace-nowrap"
							><a href={src.url} target="_blank" rel="noopener noreferrer"
								>{m.noisy_moving_newt_belong()}</a
							></td
						>
						{#if canRefresh}
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
		<Pager
			n_count={data.submissions.count}
			page_size={data.batch_size}
			base_url={page.url.toString()}
		/>
	{/if}
</Section>

<style>
	h2 {
		font-size: larger;
		margin: 1rem 0 0.5rem 0;
		font-weight: 600;
	}
</style>
