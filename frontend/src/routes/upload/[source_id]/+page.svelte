<script lang="ts">
	import Section from '$lib/Section.svelte';
	import TagsField from '$lib/TagsField.svelte';
	import TagEditTable from '$lib/TagEditTable.svelte';
	import WorkField from '$lib/WorkField.svelte';
	import SourcesViewer from '$lib/SourcesViewer.svelte';
	import DisplayText from '$lib/DisplayText.svelte';
	import { Rating, WorkOrigin, WorkStatus } from '$lib/enums';
	import client, { getTagDisplaySlug } from '$lib/api';
	import WorkTag from '$lib/WorkTag.svelte';
	import { enhance } from '$app/forms';
	import type { components } from '$lib/schema';
	import { m } from '$lib/paraglide/messages.js';

	let { data } = $props();

	let mode: 'create' | 'bind' = $state('create');
	let sourceArray = $derived([data.source]);

	let tags = $state<string[]>([]);

	let title = $state(data.suggestions?.title ?? data.source.title ?? '');
	let description = $state(data.suggestions?.description ?? data.source.description ?? '');
	let rating = $state(null as number | null);
	let bindWork = $state<components['schemas']['WorkSchema'] | null>(null);

	// Tag cache for rich tag editing (sample toggles, creator roles)
	let cache: Record<string, components['schemas']['TagWorkInstanceThinSchema']> = $state({});

	// Pre-populate cache from suggestion tags
	$effect(() => {
		if (data.suggestions) {
			const allSuggestions = [
				...(data.suggestions.source_tags ?? []),
				...(data.suggestions.creator_tags ?? []),
				...(data.suggestions.new_tags ?? [])
			];
			for (const t of allSuggestions) {
				const slug = getTagDisplaySlug(t);
				if (!cache[slug]) {
					cache[slug] = { ...t, sample: false, creator_roles: null };
				}
			}
		}
	});

	// Fetch tag details for manually added tags not in cache
	$effect(() => {
		void tags;
		const timeout = setTimeout(() => {
			tags.filter((t) => !Object.hasOwn(cache, t)).forEach(async (t) => {
				const { data } = await client.GET('/api/tag/tag', {
					fetch,
					params: { query: { tag_slug: t } }
				});
				cache[t] = data ?? {
					aliased_to: null,
					category: 0,
					creator_roles: null,
					deprecated: false,
					id: -1,
					lang_prefs: [],
					name: t,
					sample: false,
					slug: t
				};
			});
		}, 750);

		return () => clearTimeout(timeout);
	});

	const toggleTag = (tag: components['schemas']['TagWorkSchema']) => {
		const slug = getTagDisplaySlug(tag);
		if (tags.includes(slug)) {
			tags = tags.filter((t) => t !== slug);
		} else {
			tags = [...tags, slug];
		}
	};

	const toggle_sample = (tag_slug: string) => {
		cache[tag_slug].sample = !cache[tag_slug].sample;
	};

	const toggle_creator_role = (tag_slug: string, role_value: number) => {
		const tag = cache[tag_slug];
		const current_roles = tag.creator_roles || [];
		const new_roles = current_roles.includes(role_value)
			? current_roles.filter((r: number) => r !== role_value)
			: [...current_roles, role_value];
		tag.creator_roles = new_roles;
	};

	// Serialize rich tag data for form submission
	let tagsJson = $derived(
		JSON.stringify(
			tags
				.filter((t) => cache[t])
				.map((t) => ({
					nameslug: cache[t].slug,
					sample: cache[t].sample,
					roles: cache[t].creator_roles
				}))
		)
	);
</script>

<Section
	title={data.source.title}
	type={m.extra_brave_tapir_skip()}
	menuLinks={data.links}
>
	<div class="@container">
		<div class="flex w-full flex-col @[720px]:flex-row">
			<div class="shrink-0">
				<SourcesViewer
					sources={sourceArray}
					thumbnail={data.source.thumbnail}
					thumbnailAlt={data.source.title ?? ''}
				/>
			</div>
			<div class="ml-2 grow">
				<table class="w-full">
					<tbody>
						<tr>
							<th class="w-24">{m.large_factual_octopus_exhale()}</th>
							<td><DisplayText value={data.source.title} /></td>
						</tr>
						<tr>
							<th class="w-24">{m.clear_lucky_peacock_pick()}</th>
							<td>
								<div class="description-cell">
									<!-- eslint-disable-next-line svelte/no-at-html-tags -->
									{@html data.source.description}
								</div>
							</td>
						</tr>
						<tr>
							<th class="w-24">{m.super_agent_pigeon_aim()}</th>
							<td>
								{#if data.source.published_date}
									{data.source.published_date}
								{:else}
									{m.simple_less_marlin_enchant()}
								{/if}
							</td>
						</tr>
						<tr>
							<th class="w-24">{m.large_polite_otter_thrive()}</th>
							<td>{WorkOrigin[data.source.work_origin]()}</td>
						</tr>
						<tr>
							<th class="w-24">{m.civil_trick_oryx_clap()}</th>
							<td>{WorkStatus[data.source.work_status]()}</td>
						</tr>
						<tr>
							<th class="w-24">{m.big_dry_seahorse_succeed()}</th>
							<td>
								{#if data.source.work_width}
									{data.source.work_width}x{data.source.work_height}
								{:else}
									{m.simple_less_marlin_enchant()}
								{/if}
							</td>
						</tr>
						<tr>
							<th class="w-24">{m.nice_tense_mule_grasp()}</th>
							<td>
								{#if data.source.work_duration}
									{Math.floor(data.source.work_duration / 60)}:{(
										'0' +
										(data.source.work_duration % 60)
									).slice(-2)}
								{:else}
									{m.simple_less_marlin_enchant()}
								{/if}
							</td>
						</tr>
						<tr>
							<th class="w-24">URL</th>
							<td
								><a href={data.source.url} target="_blank" rel="noopener"
									>{data.source.url}</a
								></td
							>
						</tr>
						{#if data.isBound}
							<tr>
								<th class="w-24">{m.grand_merry_fly_succeed()}</th>
								<td
									><a href="/work/{data.source.media}"
										>{data.source.media_title ||
											`Work #${data.source.media}`}</a
									></td
								>
							</tr>
						{/if}
					</tbody>
				</table>
			</div>
		</div>
	</div>

	{#if !data.isBound}
		<!-- Mode toggle -->
		<div class="mt-4 mb-4 flex gap-2">
			<label
				class={[
					'cursor-pointer border px-4 py-1',
					mode === 'create' ? 'bg-otodb-content-primary text-otodb-bg-primary' : ''
				]}
			>
				<input type="radio" value="create" bind:group={mode} class="hidden" />
				{m.careful_red_cow_evoke()}
			</label>
			<label
				class={[
					'cursor-pointer border px-4 py-1',
					mode === 'bind' ? 'bg-otodb-content-primary text-otodb-bg-primary' : ''
				]}
			>
				<input type="radio" value="bind" bind:group={mode} class="hidden" />
				{m.formal_ok_fly_buzz()}
			</label>
		</div>

		{#if mode === 'create'}
			<form method="POST" action="?/create" use:enhance>
				<table>
					<tbody>
						<tr>
							<th><label for="title">{m.large_factual_octopus_exhale()}</label></th>
							<td>
								<input
									id="title"
									name="title"
									type="text"
									class="w-full"
									bind:value={title}
								/>
							</td>
						</tr>
						<tr>
							<th><label for="description">{m.clear_lucky_peacock_pick()}</label></th>
							<td>
								<textarea
									id="description"
									name="description"
									class="h-32 w-full"
									bind:value={description}
								></textarea>
							</td>
						</tr>
						<tr>
							<th><label for="rating">{m.good_dark_bumblebee_spur()}</label></th>
							<td>
								<select
									id="rating"
									name="rating"
									class="border"
									bind:value={rating}
									required
								>
									<option value={null} selected disabled>---</option>
									{#each Rating as r, i (i)}
										<option value={i}>{r()}</option>
									{/each}
								</select>
							</td>
						</tr>
						<tr>
							<th><label>{m.empty_legal_chicken_taste()}</label></th>
							<td>
								{#if data.suggestions?.source_tags?.length || data.suggestions?.creator_tags?.length || data.suggestions?.new_tags?.length}
									<div class="my-2 flex flex-wrap gap-1.5">
										{#each [...(data.suggestions.source_tags ?? []), ...(data.suggestions.creator_tags ?? []), ...(data.suggestions.new_tags ?? [])] as t (t.slug)}
											<WorkTag
												tag={t}
												selected={tags.includes(getTagDisplaySlug(t))}
												onclick={toggleTag}
											/>
										{/each}
									</div>
								{/if}
								<TagsField type="work" class="w-full" bind:value={tags} />
								<TagEditTable
									{tags}
									{cache}
									ontoggle_sample={toggle_sample}
									ontoggle_creator_role={toggle_creator_role}
								/>
								<input type="hidden" name="tags_json" value={tagsJson} />
							</td>
						</tr>
					</tbody>
				</table>
				<input type="submit" />
			</form>
		{:else}
			<form method="POST" action="?/bind" use:enhance>
				<input type="hidden" name="source_url" value={data.source.url} />
				<table>
					<tbody>
						<tr>
							<th><label>{m.grand_merry_fly_succeed()}</label></th>
							<td><WorkField bind:value={bindWork} name="work_id" /></td>
						</tr>
					</tbody>
				</table>
				<input type="submit" />
			</form>
		{/if}
	{/if}
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
