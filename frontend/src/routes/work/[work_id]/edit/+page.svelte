<script lang="ts">
	import Section from '$lib/Section.svelte';
	import { m } from '$lib/paraglide/messages.js';
	import type { PageProps } from '../$types';
	import { Platform, Rating, WorkOrigin, UserLevel } from '$lib/enums';
	import RelationEditor from '$lib/RelationEditor.svelte';
	import client, { getDisplayText } from '$lib/api';
	import { goto, invalidateAll } from '$app/navigation';
	import { callErrorToast, callSavingToast } from '$lib/toast';
	import { dirtyEnhance } from '$lib/ui';
	import GuidelineWarning from '$lib/GuidelineWarning.svelte';
	import RefreshButton from '../../RefreshButton.svelte';
	import WorkThumbnail from '$lib/WorkThumbnail.svelte';

	let { data, form }: PageProps = $props();
	let title: string = $state(form?.title ?? getDisplayText(data.title, '')),
		description: string = $state(form?.description ?? data.description!),
		rating: number = $state(form?.rating ?? data.rating!),
		thumbnail_source_id: number | null = $state(
			form?.thumbnail_source ?? data.thumbnail_source ?? data.sources?.[0]?.id ?? null
		);
	const del = async () => {
		if (confirm(m.mad_brief_falcon_pop())) {
			await client.DELETE('/api/work/work', {
				fetch,
				params: { query: { work_id: data.id } }
			});
			goto('/source', { invalidateAll: true });
		}
	};
	const unbind = async (source_id: number) => {
		if (data.sources?.length === 1) {
			if (!confirm(m.tired_real_gazelle_evoke())) return;
		}
		await client.POST('/api/source/unbind', { fetch, params: { query: { source_id } } });
		if (data.sources?.length === 1) goto('/source');
		else invalidateAll();
	};
	const updateStatus = (source_id: number) => async (e) => {
		const p = client.PUT('/api/source/origin', {
			fetch,
			params: { query: { source_id, status: e.target.value } }
		});
		callSavingToast(p);
		await p;
	};

	$effect(() => {
		if (form?.failed) {
			callErrorToast(m.green_due_javelina_pop());
		}
	});

	const form_barrier = {};
</script>

<Section title={data.title} type={m.grand_merry_fly_succeed()} menuLinks={data.links}>
	<GuidelineWarning />
	<form method="POST" use:dirtyEnhance={{ barrier: form_barrier, priority: 0 }} action="?/edit">
		<table class="inline">
			<tbody>
				<tr
					><th><label for="title">{m.large_factual_octopus_exhale()}</label></th><td
						><input
							type="text"
							name="title"
							bind:value={title}
							autocomplete="off"
						/></td
					></tr
				>
				<tr
					><th><label for="description">{m.clear_lucky_peacock_pick()}</label></th><td
						><textarea name="description" bind:value={description}></textarea></td
					></tr
				>
				<tr
					><th><label for="rating">{m.good_dark_bumblebee_spur()}</label></th><td
						><select name="rating" bind:value={rating}>
							{#each Rating as r, i (i)}<option value={i}>{r()}</option
								>{/each}</select
						></td
					></tr
				>
				<tr
					><th><label for="thumbnail_source">{m.heroic_ideal_orangutan_aid()}</label></th
					><td
						><select name="thumbnail_source" bind:value={thumbnail_source_id}>
							{#each data.sources! as src (src.id)}
								<option value={src.id}
									>{Platform[src.platform]}
									{src.work_origin === 0
										? ''
										: ' ' + WorkOrigin[src.work_origin]()}
									-
									{src.title || src.url}</option
								>
							{/each}
						</select>
						{#if thumbnail_source_id}
							{@const selectedSource = data.sources!.find(
								(s) => s.id === thumbnail_source_id
							)}
							<WorkThumbnail
								class="mt-2 aspect-video w-20"
								thumbnail={selectedSource?.thumbnail}
								alt={selectedSource?.title ?? ''}
							/>
						{/if}</td
					></tr
				>
				<tr
					><th><label for="reason">{m.wide_just_gull_glow()}</label></th><td
						><input type="text" name="reason" value={form?.reason ?? ''} /></td
					></tr
				>
			</tbody>
		</table>
		<table class="inline">
			<thead
				><tr>
					<th></th>
					<th>{m.large_factual_octopus_exhale()}</th>
					<th>{m.clear_lucky_peacock_pick()}</th>
					<th>{m.sour_swift_sparrow_spin()}</th>
					<th>{m.large_polite_otter_thrive()}</th>
					<th>{m.super_agent_pigeon_aim()}</th>
					<th>{m.noisy_moving_newt_belong()}</th>
					<th>{m.heroic_ideal_orangutan_aid()}</th>
					<th>{m.sour_lime_shad_edit()}</th>
					<th>{m.mushy_proof_hornet_dig()} / {m.minor_crisp_cobra_list()}</th>
				</tr></thead
			>
			<tbody>
				{#each data.sources! as src, i (i)}
					<tr>
						<td
							><button
								onclick={() => {
									title = src.title;
									description = src.description;
									thumbnail_source_id = src.id;
								}}
								type="button">&lt;&lt;</button
							></td
						>
						<td class="whitespace-nowrap">{src.title || src.url}</td>
						<td
							><details>
								<summary>[{m.tough_early_sparrow_bask()}]</summary><span
									class="whitespace-pre-wrap">{src.description}</span
								>
							</details></td
						>
						<td>{Platform[src.platform]}</td>
						<td class="whitespace-nowrap"
							><select value={src.work_origin} onchange={updateStatus(src.id)}
								>{#each WorkOrigin as w, i (i)}
									<option value={i}>{w()}</option>
								{/each}</select
							></td
						>
						<td>{src.published_date}</td>
						<td class="whitespace-nowrap"
							><a href={src.url} target="_blank" rel="noopener noreferrer"
								>{m.noisy_moving_newt_belong()}</a
							></td
						>
						<td>
							{src.thumbnail
								? m.full_best_canary_view()
								: m.simple_less_marlin_enchant()}
						</td>
						<td
							><button type="button" onclick={() => unbind(src.id)}
								>{m.sour_lime_shad_edit()}</button
							></td
						><td>
							{#if src.work_status === 0}
								<RefreshButton source={src} />
							{:else if src.work_status === 1}
								{#if data.user?.level >= UserLevel.EDITOR}
									<a href="/source/add?for_source={src.id}"
										>{m.minor_crisp_cobra_list()}</a
									>
								{:else}
									{m.simple_less_marlin_enchant()}
								{/if}
							{/if}
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
		<br />
		<input type="submit" />
	</form>
	{#if data.user?.level >= UserLevel.ADMIN}
		<button onclick={del}>{m.suave_less_deer_grip()}</button>
	{/if}
</Section>

<Section title={m.alive_these_jay_pick()}>
	<RelationEditor
		init_relations={data.relations}
		obj_type="work"
		this_id={data.id}
		form_control={{ barrier: form_barrier, priority: 1 }}
	></RelationEditor>
</Section>
