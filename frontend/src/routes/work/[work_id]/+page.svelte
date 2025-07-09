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
	<div>
		<div class="flex w-full">
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
					<label
						><input
							hidden
							type="radio"
							name="cover_select"
							value={-1}
							bind:group={cover_select}
						/>{m.heroic_ideal_orangutan_aid()}</label
					>
					{#each data.sources as s, i (i)}
						<label>
							<input
								hidden
								type="radio"
								name="cover_select"
								value={i}
								bind:group={cover_select}
							/>
							{Platform[s.platform]}{s.work_origin === 0
								? ''
								: ' ' + WorkOrigin[s.work_origin]()}
						</label>
					{/each}
				</div>
			</div>
			<div class="ml-2 flex-grow">
				<div>
					<table class="w-full">
						<tbody>
							<tr><th>{m.large_factual_octopus_exhale()}</th><td>{data.title}</td></tr
							>
							<tr>
								<th>{m.clear_lucky_peacock_pick()}</th>
								<!-- eslint-disable-next-line svelte/no-at-html-tags -->
								<td class="whitespace-pre-wrap">{@html data.description}</td>
							</tr>
							<tr>
								<th>{m.good_dark_bumblebee_spur()}</th>
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
									<th>{m.stale_loose_squid_cut()}</th>
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
	<table class="w-full">
		<thead
			><tr>
				<th>{m.large_factual_octopus_exhale()}</th>
				<th>{m.clear_lucky_peacock_pick()}</th>
				<th>{m.sour_swift_sparrow_spin()}</th>
				<th>{m.super_agent_pigeon_aim()}</th>
				<th>{m.large_polite_otter_thrive()}</th>
				<th>{m.civil_trick_oryx_clap()}</th>
				<th>{m.big_dry_seahorse_succeed()}</th>
				<th>{m.noisy_moving_newt_belong()}</th>
				{#if data.user}
					<th>{m.mushy_proof_hornet_dig()}</th>
				{/if}
			</tr></thead
		>
		<tbody>
			{#each data.sources as src, i (i)}
				<tr>
					<td class="whitespace-nowrap">{src.title}</td>
					<td><CollapsibleText text={src.description}></CollapsibleText></td>
					<td>{Platform[src.platform]}</td><td>{src.published_date}</td>
					<td class="whitespace-nowrap">{WorkOrigin[src.work_origin]()}</td><td
						class="whitespace-nowrap">{WorkStatus[src.work_status]()}</td
					>
					<td
						>{#if src.work_width}{src.work_width}x{src.work_height}{:else}{m.simple_less_marlin_enchant()}{/if}</td
					><td class="whitespace-nowrap"
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
	th {
		white-space: nowrap;
	}
	label:has(> input[name='cover_select']) {
		padding: 0.2rem 0.5rem;
		display: inline-block;
		background-color: var(--otodb-bg-color);
		border: 1px solid var(--otodb-content-color);
		&:hover {
			background-color: var(--otodb-fainter-bg);
		}
		&:active {
			background-color: var(--otodb-faint-bg);
		}
	}
	label:has(> input[name='cover_select']:checked) {
		background-color: var(--otodb-content-color);
		border: 1px solid var(--otodb-bg-color);
		color: var(--otodb-bg-color);
	}
</style>
