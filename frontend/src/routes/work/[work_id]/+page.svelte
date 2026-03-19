<script lang="ts">
	import Section from '$lib/Section.svelte';
	import { m } from '$lib/paraglide/messages.js';
	import {
		Platform,
		Rating,
		WorkOrigin,
		WorkRelationDisplayBackward,
		WorkRelationDisplayForward,
		WorkStatus,
		WorkTagCategoriesSettableAsSource,
		WorkTagCategory,
		WorkTagPresentationColours,
		WorkTagPresentationOrder
	} from '$lib/enums';
	import WorkTag from '$lib/WorkTag.svelte';
	import client, { getDisplayText } from '$lib/api';
	import type { components } from '$lib/schema';
	import DisplayText from '$lib/DisplayText.svelte';
	import RefreshButton from '../RefreshButton.svelte';
	import CommentTree from '$lib/CommentTree.svelte';
	import { callSavingToast } from '$lib/toast';
	import { SvelteMap } from 'svelte/reactivity';
	import WorkCard from '$lib/WorkCard.svelte';
	import SourceViewer from '$lib/SourceViewer.svelte';

	let { data } = $props();

	let [userLists, userListsFetched]: [[components['schemas']['ListSchema'], boolean][], boolean] =
			$derived(data && [[], false]),
		userListsShown = $state(false);
	const showLists = async () => {
		if (!userListsFetched) {
			const { data: lists } = await client.GET('/api/profile/work_in_my_lists', {
				fetch,
				params: { query: { work_id: data.id } }
			});
			userLists = lists!;
			userListsFetched = true;
			userListsShown = true;
		} else {
			userListsShown = !userListsShown;
		}
	};
	const toggleWork = async (list_id: number) => {
		const p = client.PUT('/api/list/toggle_work', {
			fetch,
			params: { query: { list_id, work_id: data.id } }
		});
		callSavingToast(p);
		const { error } = await p;
		if (!error) {
			const list = userLists.find((el) => el[0].id === list_id)!;
			list[1] = !list[1];
		}
	};

	const merge_paths = (paths) => {
		const graph = new SvelteMap();
		paths
			.filter((p) => p.primary_path.length)
			.forEach((path) =>
				path.primary_path.forEach((p, i, a) => {
					const next_node = (i + 1 === a.length ? path : a[i + 1]).slug;
					if (graph.has(p.slug)) graph.get(p.slug).add(next_node);
					else graph.set(p.slug, new Set([next_node]));
				})
			);
		const traverse = (node) => ({
			node: [...paths, ...paths.flatMap((p) => p.primary_path)].find((n) => n.slug === node),
			real: paths.some((n) => n.slug === node),
			children: Array.from(graph.get(node) ?? []).map((n) => traverse(n))
		});
		return [
			...graph
				.keys()
				.filter((n) => !graph.values().some((s) => s.has(n)))
				.map(traverse),
			...paths
				.filter((p) => p.primary_path.length === 0 && !graph.has(p.slug))
				.map((n) => ({ node: n, real: true }))
		];
	};
</script>

<Section type={m.grand_merry_fly_succeed()} title={data.title} menuLinks={data.links}>
	<div class="@container">
		<div class="flex w-full flex-col @[720px]:flex-row">
			<div class="shrink-0">
				<SourceViewer
					sources={data.sources ?? []}
					thumbnail={data.thumbnail}
					thumbnailAlt={getDisplayText(data.title)}
				/>
			</div>
			<div class="ml-2 grow">
				<div>
					<table class="w-full">
						<tbody>
							<tr>
								<th class="w-24">{m.large_factual_octopus_exhale()}</th>
								<td><DisplayText value={data.title} /></td>
							</tr>
							<tr>
								<th class="w-24">{m.clear_lucky_peacock_pick()}</th>
								<!-- eslint-disable-next-line svelte/no-at-html-tags -->
								<td><div class="description-cell">{@html data.description}</div></td
								>
							</tr>
							{#if data.relations[0].length}
								<tr>
									<th>{m.alive_these_jay_pick()}</th>
									<td
										><ul>
											{#each Object.entries(Object.groupBy(data.relations[0], (r) => +(r.A_id === data.id))).map( (d) => [d[0], Object.entries(Object.groupBy(d[1], (r) => r.relation))] ) as [dir, rels], i (i)}
												{#each rels as [tp, relations], j (j)}
													<li>
														{m.mild_loud_shad_enchant({
															type: [
																WorkRelationDisplayBackward,
																WorkRelationDisplayForward
															][+dir][tp](),
															name: ''
														})}
														<ul class="ml-2">
															{#each relations as r, j (j)}
																{@const w = data.relations[1].find(
																	(w) =>
																		w.id ===
																		(r.A_id === data.id
																			? r.B_id
																			: r.A_id)
																)}
																<li>
																	<a href="/work/{w.id}"
																		>#{w.id} - {w.title}</a
																	>
																</li>
															{/each}
														</ul>
													</li>
												{/each}
											{/each}
										</ul></td
									>
								</tr>
							{/if}
							<tr>
								<th class="w-24">{m.good_dark_bumblebee_spur()}</th>
								<td>{Rating[data.rating]()}</td>
							</tr>
						</tbody>
					</table>
				</div>
				{#if data.user}
					<div class="mt-2 w-full">
						<h2>{m.watery_sunny_seal_heal()}</h2>
						<table class="w-full">
							<tbody>
								<tr>
									<th class="w-24">{m.stale_loose_squid_cut()}</th>
									<td>
										<button onclick={showLists}>
											{m.proud_every_goat_affirm()}
										</button>
										{#if userListsShown}
											<table class="absolute">
												<tbody>
													{#each userLists as list, i (i)}
														<tr>
															<td>{list[0].name}</td>
															<td>
																<input
																	type="checkbox"
																	checked={list[1]}
																	oninput={() => {
																		toggleWork(list[0].id);
																	}}
																/>
															</td>
														</tr>
													{/each}
												</tbody>
											</table>
										{/if}
									</td>
								</tr>
							</tbody>
						</table>
					</div>
				{/if}
			</div>
		</div>
		<div
			class={['mt-2 flex flex-row flex-wrap gap-x-3 border-t', { hidden: !data.tags.length }]}
		>
			{#each Object.entries(Object.groupBy( data.tags, (t) => (WorkTagCategoriesSettableAsSource.includes(t.category) && t.sample ? 3 : t.category) )).toSorted((a, b) => WorkTagPresentationOrder.indexOf(+a[0]) - WorkTagPresentationOrder.indexOf(+b[0])) as cat, i (i)}
				<span
					class="mt-4 border-l-2 px-3 pb-2"
					style="border-color: {WorkTagPresentationColours[
						cat[0]
					]};background-color: color-mix(in hsl, {WorkTagPresentationColours[
						cat[0]
					]}, transparent 85%);"
				>
					<h5 class="my-2 font-bold">
						{WorkTagCategory[cat[0]]()}
					</h5>
					<ul class="flex list-none flex-wrap gap-2">
						{#each merge_paths(cat[1]) as tag, j (j)}
							<li class="m-0"><WorkTag {tag} tree={true} /></li>
						{/each}
					</ul>
				</span>
			{/each}
		</div>
	</div>
</Section>

<Section
	title={m.extra_brave_tapir_skip()}
	menuLinks={data.user
		? [{ pathname: `source/add?for_work=${data.id}`, title: m.helpful_away_jay_succeed() }]
		: []}
>
	<div class="mt-2 flex w-full flex-col gap-y-4">
		{#each data.sources as src, i (i)}
			<div
				class={[
					'w-full border px-4 py-2',
					src.work_status !== 0 ? 'bg-otodb-bg-fainter text-otodb-content-fainter' : ''
				]}
			>
				{#if data.user}
					<span class="float-right mt-2">
						<RefreshButton source={src} />
					</span>
				{/if}
				<div class="text-lg">
					<strong>
						<a
							href={src.url}
							target="_blank"
							rel="noopener noreferrer"
							class={[src.work_status !== 0 ? 'text-otodb-content-fainter' : '']}
						>
							{Platform[src.platform]}
							{src.work_origin === 0 ? '' : ' ' + WorkOrigin[src.work_origin]()}
							-
							{src.title || src.url}
						</a>
					</strong>
					<a href="/source/{src.id}" class="ml-2 text-sm">»</a>
				</div>

				<div class="mt-2 flex flex-wrap gap-x-2">
					<div>
						{m.super_agent_pigeon_aim()}:
						<strong>
							<date>
								{#if src.published_date}
									{src.published_date}
								{:else}
									{m.simple_less_marlin_enchant()}
								{/if}
							</date>
						</strong>
					</div>
					<div>
						{m.large_polite_otter_thrive()}:
						<strong>
							{WorkOrigin[src.work_origin]()}
						</strong>
					</div>
					<div>
						{m.civil_trick_oryx_clap()}:
						<strong>{WorkStatus[src.work_status]()}</strong>
					</div>
					<div>
						{m.big_dry_seahorse_succeed()}:
						<strong>
							{#if src.work_width}
								{src.work_width}x{src.work_height}
							{:else}
								{m.simple_less_marlin_enchant()}
							{/if}
						</strong>
					</div>
					<div>
						{m.nice_tense_mule_grasp()}:
						<strong>
							{#if src.work_duration}
								{Math.floor(src.work_duration / 60)}:{(
									'0' +
									(src.work_duration % 60)
								).slice(-2)}
							{:else}
								{m.simple_less_marlin_enchant()}
							{/if}
						</strong>
					</div>
				</div>
				<div class="my-2">
					<details>
						<summary>{m.clear_lucky_peacock_pick()}</summary>
						<!-- eslint-disable-next-line svelte/no-at-html-tags -->
						{@html src.description}
					</details>
				</div>
			</div>
		{/each}
	</div>
</Section>

{#await data.similar}
	<!-- Blank -->
{:then similar}
	{#if similar?.length}
		<Section title={m.topical_main_beaver_walk()}>
			<div class="grid grid-cols-[repeat(auto-fill,minmax(192px,1fr))] gap-x-4 gap-y-4">
				{#each similar as s, i (i)}
					<WorkCard work={s} />
				{/each}
			</div>
		</Section>
	{/if}
{/await}

<Section title={m.same_broad_haddock_pinch()}>
	<CommentTree comments={data.comments} user={data.user ?? null} model="mediawork" pk={data.id} />
</Section>

<style>
	.description-cell {
		white-space: pre-wrap;
		max-height: 15em;
		overflow-y: auto;
		overflow-wrap: anywhere;
	}
	th {
		white-space: nowrap;
	}
</style>
