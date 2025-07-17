<script lang="ts">
	import Section from '$lib/Section.svelte';
	import CollapsibleText from './CollapsibleText.svelte';
	import { m } from '$lib/paraglide/messages.js';
	import { Platform, Rating, WorkOrigin, WorkStatus } from '$lib/enums';
	import WorkTag from '$lib/WorkTag.svelte';
	import client from '$lib/api';
	import type { components } from '$lib/schema';
	import RefreshButton from '../RefreshButton.svelte';
	import CommentTree from '$lib/CommentTree.svelte';
	import ExternalEmbed from '$lib/ExternalEmbed.svelte';

	let { data } = $props();

	let userLists: [components['schemas']['ListSchema'], boolean][] = $state([]),
		userListsFetched = false,
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
		const { error, data: state } = await client.PUT('/api/list/toggle_work', {
			fetch,
			params: { query: { list_id, work_id: data.id } }
		});
		if (!error) {
			const list = userLists.find((el) => el[0].id === list_id)!;
			list[1] = !list[1];
		}
	};

	let cover_select = $state(-1);
</script>

<Section
	title={m.mild_loud_shad_enchant({ type: m.grand_merry_fly_succeed(), name: data.title })}
	menuLinks={data.links}
>
	<div class="@container">
		<div class="flex w-full flex-col @[720px]:flex-row">
			<div class="flex-shrink-0">
				{#if cover_select === -1}
					<img
						src={data.thumbnail}
						alt={data.title}
						class="h-[270px] w-[480px] object-cover"
					/>
				{:else}
					<ExternalEmbed width={480} height={270} src={data.sources[cover_select]} />
				{/if}
				<div class="my-2">
					<a
						href={data.thumbnail}
						target="_blank"
						rel="noopener noreferrer"
						class="cover_select"
						class:selected={cover_select === -1}
						onclick={(e) => {
							e.preventDefault();
							cover_select = -1;
						}}
					>
						{m.heroic_ideal_orangutan_aid()}
					</a>
					{#each data.sources as s, i (i)}
						<a
							href={s.url}
							target="_blank"
							rel="noopener noreferrer"
							class="cover_select"
							class:selected={cover_select === i}
							onclick={(e) => {
								e.preventDefault();
								cover_select = i;
							}}
						>
							{Platform[s.platform]}{s.work_origin === 0
								? ''
								: ' ' + WorkOrigin[s.work_origin]()}
						</a>
					{/each}
				</div>
			</div>
			<div class="ml-2 flex-grow">
				<div>
					<table class="w-full">
						<tbody>
							<tr>
								<th class="w-24">{m.large_factual_octopus_exhale()}</th>
								<td>{data.title}</td>
							</tr>
							<tr>
								<th class="w-24">{m.clear_lucky_peacock_pick()}</th>
								<!-- eslint-disable-next-line svelte/no-at-html-tags -->
								<td><div class="description-cell">{@html data.description}</div></td
								>
							</tr>
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
		<ul id="work-tags">
			{#each data.tags as tag, i (i)}
				<li><WorkTag {tag} /></li>
			{/each}
		</ul>
	</div>
</Section>

<Section
	title={m.extra_brave_tapir_skip()}
	menuLinks={data.user
		? [{ pathname: `work/add?for_work=${data.id}`, title: m.helpful_away_jay_succeed() }]
		: []}
>
	<div class="mt-2 flex w-full flex-col gap-y-4">
		{#each data.sources as src, i (i)}
			<div
				class={[
					'w-full border px-4 py-2',
					src.work_status !== 0 ? 'bg-otodb-fainter-bg text-otodb-fainter-content' : ''
				]}
			>
				<div class="text-lg">
					<strong>
						<a
							href={src.url}
							target="_blank"
							rel="noopener noreferrer"
							class={[
								'hover:underline',
								src.work_status !== 0 ? 'text-otodb-fainter-content' : ''
							]}
						>
							{Platform[src.platform]}
							{src.work_origin === 0 ? '' : ' ' + WorkOrigin[src.work_origin]()}
							-
							{src.title}
						</a>
					</strong>
				</div>

				<div class="mt-2 flex flex-wrap gap-x-2">
					<div>
						{m.super_agent_pigeon_aim()}:
						<strong>
							<date>
								{src.published_date}
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
					<div></div>
				</div>
				<div class="mt-2">
					<CollapsibleText text={src.description}></CollapsibleText>
				</div>
				{#if data.user}
					<div class="mt-2 flex justify-end">
						<RefreshButton source={src} />
					</div>
				{/if}
			</div>
		{/each}
	</div>
</Section>

<Section title={m.same_broad_haddock_pinch()}>
	<CommentTree comments={data.comments} user={data.user ?? null} model="mediawork" pk={data.id} />
</Section>

<style>
	#work-tags {
		grid-column: 1 / span 2;
		border-top: var(--otodb-faint-content) 1px solid;
		margin-top: 2rem;
		padding-top: 1rem;
		display: flex;
		gap: 0.3rem 1rem;
		flex-wrap: wrap;
		list-style: none;
		& > li {
			margin: 0;
		}
	}
	.description-cell {
		white-space: pre-wrap;
		max-height: 15em;
		overflow-y: auto;
		word-wrap: break-word;
	}
	th {
		white-space: nowrap;
	}
	.cover_select {
		padding: 0.2rem 0.5rem;
		display: inline-block;
		background-color: var(--otodb-bg-color);
		border: 1px solid var(--otodb-content-color);
		text-decoration: none;
		&:hover {
			background-color: var(--otodb-fainter-bg);
		}
		&:active {
			background-color: var(--otodb-faint-bg);
		}
		&.selected {
			background-color: var(--otodb-content-color);
			border: 1px solid var(--otodb-bg-color);
			color: var(--otodb-bg-color);
		}
	}
</style>
