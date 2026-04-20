<script lang="ts">
	import client, { getDisplayText } from '$lib/api';
	import CommentTree from '$lib/CommentTree.svelte';
	import DisplayText from '$lib/DisplayText.svelte';
	import {
		PlatformNames,
		RatingNames,
		WorkOriginNames,
		WorkRelationDisplayBackward,
		WorkRelationDisplayForward,
		WorkStatusNames
	} from '$lib/enums';
	import { WorkTagCategoryMap } from '$lib/enums/workTagCategory.js';
	import { m } from '$lib/paraglide/messages.js';
	import RefreshButton from '$lib/RefreshButton.svelte';
	import {
		PathsApiCommentCommentDeleteParametersQueryModel,
		WorkOrigin,
		WorkRelationTypes,
		WorkTagCategory,
		type components
	} from '$lib/schema.js';
	import Section from '$lib/Section.svelte';
	import SourcesViewer from '$lib/SourcesViewer.svelte';
	import { callSavingToast } from '$lib/toast';
	import WorkCard from '$lib/WorkCard.svelte';
	import WorkTagTree from '$lib/WorkTagTree.svelte';
	import type { ComponentProps } from 'svelte';
	import { SvelteMap } from 'svelte/reactivity';
	import type { PageProps } from './$types.js';

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

	const groupedTags: [WorkTagCategory, PageProps['data']['tags']][] = $derived(
		[
			...Map.groupBy(data.tags, (t) => {
				const c = t.category;
				if (WorkTagCategoryMap[c].canSetAsSource && t.sample) return WorkTagCategory.Source;
				else return c;
			}).entries()
		].toSorted(([a], [b]) => WorkTagCategoryMap[a].order - WorkTagCategoryMap[b].order)
	);

	const merge_paths = (
		paths: (typeof groupedTags)[number][1]
	): ComponentProps<typeof WorkTagTree>['tree'][] => {
		const graph: SvelteMap<string, Set<string>> = new SvelteMap();
		paths
			.filter((p) => p.primary_path.length)
			.forEach((path) =>
				path.primary_path.forEach((p, i, a) => {
					const next_node = (i + 1 === a.length ? path : a[i + 1]).slug;
					if (graph.has(p.slug)) graph.get(p.slug)?.add(next_node);
					else graph.set(p.slug, new Set([next_node]));
				})
			);
		const traverse = (node: string): ComponentProps<typeof WorkTagTree>['tree'] => ({
			node: [...paths, ...paths.flatMap((p) => p.primary_path)].find((n) => n.slug === node)!,
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

	const relTree = $derived(
		data.relations[0].length > 0
			? ([...Map.groupBy(data.relations[0], (r) => +(r.A_id === data.id)).entries()].map(
					(d) => [+d[0], [...Map.groupBy(d[1]!, (r) => r.relation).entries()]]
				) as [0 | 1, [WorkRelationTypes, { A_id: number; B_id: number }[]][]][])
			: null
	);
</script>

<Section type={m.grand_merry_fly_succeed()} title={data.title} menuLinks={data.links}>
	<div class="@container">
		<div class="flex w-full flex-col @[720px]:flex-row">
			<div class="shrink-0">
				<SourcesViewer
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
								<td
									><div class="description-cell external-link-icon">
										<!-- eslint-disable-next-line svelte/no-at-html-tags -->
										{@html data.description}
									</div></td
								>
							</tr>
							{#if relTree}
								<tr>
									<th>{m.alive_these_jay_pick()}</th>
									<td
										><ul>
											{#each relTree as [dir, rels], i (i)}
												{#each rels as [tp, relations], j (j)}
													<li>
														{m.mild_loud_shad_enchant({
															type: [
																WorkRelationDisplayBackward,
																WorkRelationDisplayForward
															][dir][tp](),
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
																)!}
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
								<td>{RatingNames[data.rating]()}</td>
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
															<td
																><a href="/list/{list[0].id}"
																	>{list[0].name}</a
																></td
															>
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
			{#each groupedTags as [cat, tags] (cat)}
				<span
					class="mt-4 border-l-2 px-3 pb-2"
					style="border-color: {WorkTagCategoryMap[cat]
						.color};background-color: color-mix(in hsl, {WorkTagCategoryMap[cat]
						.color}, transparent 85%);"
				>
					<h5 class="my-2 font-bold">
						{WorkTagCategoryMap[cat].nameFn()}
					</h5>
					<ul class="flex list-none flex-wrap gap-2">
						{#each merge_paths(tags) as tree, j (j)}
							<li class="m-0">
								<WorkTagTree {tree} />
							</li>
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
		? [{ pathname: `upload/add?for_work=${data.id}`, title: m.helpful_away_jay_succeed() }]
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
							{PlatformNames[src.platform]}
							{src.work_origin === WorkOrigin.Author
								? ''
								: ' ' + WorkOriginNames[src.work_origin]()}
							-
							{src.title || src.url}
						</a>
					</strong>
					<a href="/upload/{src.id}" class="ml-2 text-sm">»</a>
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
							{WorkOriginNames[src.work_origin]()}
						</strong>
					</div>
					<div>
						{m.civil_trick_oryx_clap()}:
						<strong>{WorkStatusNames[src.work_status]()}</strong>
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
						<div class="external-link-icon whitespace-pre-wrap">
							<!-- eslint-disable-next-line svelte/no-at-html-tags -->
							{@html src.description}
						</div>
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
	<CommentTree
		comments={data.comments}
		user={data.user ?? null}
		model={PathsApiCommentCommentDeleteParametersQueryModel.mediawork}
		pk={data.id}
	/>
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
