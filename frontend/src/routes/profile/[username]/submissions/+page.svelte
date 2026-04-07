<script lang="ts">
	import Section from '$lib/Section.svelte';
	import type { PageProps } from './$types';
	import { m } from '$lib/paraglide/messages.js';
	import { Platform, Status, UserLevel, WorkOrigin, WorkStatus } from '$lib/enums';
	import RefreshButton from '$lib/RefreshButton.svelte';
	import Pager from '$lib/Pager.svelte';
	import { page } from '$app/state';

	let { data }: PageProps = $props();
</script>

<Section title={data.profile.username} type={m.fuzzy_crazy_cobra_lead()} menuLinks={data.links}>
	{#if data.user?.username === data.profile.username}
		<a href="/upload/add">{m.fluffy_crisp_horse_imagine()}</a>
	{/if}
	<form method="get">
		<table>
			<caption>{m.livid_same_wren_create()}</caption>
			<tbody>
				<tr>
					<td>{m.just_noisy_moth_beam()}</td>
					<td
						><select name="standing" value={data.standing ?? 1}
							>{#each Status as p, i (i)}<option value={i}>{p()}</option
								>{/each}</select
						></td
					>
				</tr>
				<tr>
					<td>{m.sour_swift_sparrow_spin()}</td>
					<td
						><select name="platform" value={data.platform ?? null}
							><option value={null}>---</option
							>{#each Platform.slice(1) as p, i (i)}<option value={i + 1}>{p}</option
								>{/each}</select
						></td
					>
				</tr>
				<tr>
					<td>{m.large_polite_otter_thrive()}</td>
					<td
						><select name="origin" value={data.origin ?? null}
							><option value={null}>---</option><option value={0}
								>{WorkOrigin[0]()}</option
							><option value={1}>{WorkOrigin[1]()}</option></select
						></td
					>
				</tr>
				<tr>
					<td>{m.civil_trick_oryx_clap()}</td>
					<td
						><select name="status" value={data.status ?? null}
							><option value={null}>---</option><option value={0}
								>{WorkStatus[0]()}</option
							><option value={1}>{WorkStatus[1]()}</option></select
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
							><option value="-">{m.kind_quick_bullock_push()}</option><option
								value="+">{m.novel_orange_mantis_feast()}</option
							></select
						>
					</td>
				</tr>
			</tbody>
		</table>
		<input type="submit" />
	</form>
	<hr class="my-2" />
	{#if data.standing === 0}
		<h2>{m.such_actual_okapi_dare()}</h2>
		{#if data.submissions?.items.length}
			<table class="w-full">
				<thead
					><tr>
						<th>{m.large_factual_octopus_exhale()}</th>
						<th>{m.sour_swift_sparrow_spin()}</th>
						<th>{m.super_agent_pigeon_aim()}</th>
						<th>{m.large_polite_otter_thrive()}</th>
						<th>{m.noisy_moving_newt_belong()}</th>
						{#if data.user && data.user.level >= UserLevel.EDITOR}
							<th>{m.mushy_proof_hornet_dig()}</th>
						{/if}
					</tr></thead
				>
				<tbody>
					{#each data.submissions.items as src, i (i)}
						<tr>
							<td class="whitespace-nowrap"
								><a href="/upload/{src.id}">{src.title || src.url}</a></td
							>
							<td>{Platform[src.platform]}</td><td>{src.published_date}</td>
							<td class="whitespace-nowrap">{WorkOrigin[src.work_origin]()}</td>
							<td class="whitespace-nowrap"
								><a href={src.url} target="_blank" rel="noopener noreferrer"
									>{m.noisy_moving_newt_belong()}</a
								></td
							>
							{#if data.user && data.user.level >= UserLevel.EDITOR}
								<td><RefreshButton source={src} /></td>
							{/if}
						</tr>
					{/each}
				</tbody>
			</table>
		{:else}
			<p>{m.moving_such_seal_hug()}</p>
		{/if}
	{:else if data.standing === 1}
		<h2>{m.spare_few_kudu_learn()}</h2>
		{#if data.submissions?.items.length}
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
					{#each data.submissions.items as src, i (i)}
						<tr>
							<td class="whitespace-nowrap"
								><a href="/work/{src.media}"
									>#{src.media} - {src.title || src.url}</a
								></td
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
	{:else if data.standing === 2}
		<h2>{m.stale_vexed_hare_pray()}</h2>
		{#if data.submissions?.items.length}
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
					{#each data.submissions.items as src, i (i)}
						<tr>
							<td class="whitespace-nowrap">{src.title || src.url}</td>
							<!-- <td class="whitespace-nowrap">{src.rejection.reason}</td> `src.rejection` might be no longer exists. -->
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
	{/if}
	{#if data.submissions?.count}
		<Pager
			n_count={data.submissions.count}
			page={data.page}
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
