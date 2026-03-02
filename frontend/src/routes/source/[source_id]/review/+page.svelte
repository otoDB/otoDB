<script lang="ts">
	import Section from '$lib/Section.svelte';
	import TagsField from '$lib/TagsField.svelte';
	import WorkField from '$lib/WorkField.svelte';
	import SourceViewer from '$lib/SourceViewer.svelte';
	import { Rating, WorkOrigin, WorkStatus } from '$lib/enums';
	import { getTagDisplaySlug } from '$lib/api';
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
	let rating = $state(0);
	let bindWork = $state<components['schemas']['WorkSchema'] | null>(null);

	const toggleTag = (tag: components['schemas']['TagWorkSchema']) => {
		const slug = getTagDisplaySlug(tag);
		if (tags.includes(slug)) {
			tags = tags.filter((t) => t !== slug);
		} else {
			tags = [...tags, slug];
		}
	};
</script>

<Section title="Review Source" type="New Work">
	<div class="@container">
		<div class="flex w-full flex-col @[720px]:flex-row">
			<div class="shrink-0">
				<SourceViewer
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
							<td>{data.source.title || 'Untitled'}</td>
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
					</tbody>
				</table>
			</div>
		</div>
	</div>

	<!-- Mode toggle -->
	<div class="mt-4 mb-4 flex gap-2">
		<button
			class={[
				'border px-4 py-1',
				mode === 'create' ? 'bg-otodb-content-primary text-otodb-bg-primary' : ''
			]}
			onclick={() => (mode = 'create')}
		>
			Create New Work
		</button>
		<button
			class={[
				'border px-4 py-1',
				mode === 'bind' ? 'bg-otodb-content-primary text-otodb-bg-primary' : ''
			]}
			onclick={() => (mode = 'bind')}
		>
			Bind to Existing Work
		</button>
	</div>

	{#if mode === 'create'}
		<form method="POST" action="?/create" use:enhance>
			<div class="flex flex-col gap-4">
				<div>
					<label for="title" class="block font-bold">Title</label>
					<input id="title" name="title" type="text" class="w-full" bind:value={title} />
				</div>

				<div>
					<label for="description" class="block font-bold">Description</label>
					<textarea
						id="description"
						name="description"
						class="h-32 w-full"
						bind:value={description}
					></textarea>
				</div>

				<div>
					<label for="rating" class="block font-bold">Rating</label>
					<select id="rating" name="rating" class="border" bind:value={rating}>
						{#each Rating as r, i (i)}
							<option value={i}>{r()}</option>
						{/each}
					</select>
				</div>

				<div>
					<label class="block font-bold">Tags</label>
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
					<input type="hidden" name="tags" value={tags.join(' ')} />
				</div>

				<div>
					<input type="submit" />
				</div>
			</div>
		</form>
	{:else}
		<form method="POST" action="?/bind" use:enhance>
			<input type="hidden" name="source_url" value={data.source.url} />
			<div class="flex flex-col gap-4">
				<div>
					<label class="block font-bold">Work</label>
					<WorkField bind:value={bindWork} name="work_id" />
				</div>

				<div>
					<input type="submit" />
				</div>
			</div>
		</form>
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
