<script lang="ts">
	import Section from '$lib/Section.svelte';
	import { m } from '$lib/paraglide/messages.js';
	import { enhance } from '$app/forms';
	import { debounce } from '$lib/ui';
	import client from '$lib/api';
	import { getDisplayText } from '$lib/tag.js';
	import { goto } from '$app/navigation';
	import { draggable, droppable, type DragDropCallbacks } from '@thisux/sveltednd';
	import { callSavingToast } from '$lib/toast';
	import DisplayText from '$lib/DisplayText.svelte';
	import LoadMoreButton from '$lib/LoadMoreButton.svelte';
	import WorkThumbnail from '$lib/WorkThumbnail.svelte';

	let { data, form } = $props();

	let entries = $derived.by(() => {
		// https://github.com/sveltejs/svelte/issues/16189
		let _ = $state(data.entries!.items);
		return _;
	});

	const handleDrop: DragDropCallbacks<number[]>['onDrop'] = async (state) => {
		const { draggedItem, targetContainer } = state;
		const dragIndex = draggedItem[0];
		const dropIndex = parseInt(targetContainer ?? '0');

		if (dragIndex !== -1 && !isNaN(dropIndex) && dragIndex !== dropIndex) {
			const [item] = entries.splice(dragIndex, 1);
			entries.splice(dropIndex, 0, item);
			entries = entries;
			await client.PUT('/api/list/items', {
				fetch,
				params: { query: { list_id: data.list.id } },
				body: {
					move: [[dragIndex, dropIndex]],
					delete: [],
					update_description: [],
					update_work: []
				}
			});
		}
	};

	async function update_description(index: number, value: string) {
		const p = client.PUT('/api/list/items', {
			fetch,
			params: { query: { list_id: data.list.id } },
			body: {
				update_description: [[index, value]],
				move: [],
				delete: [],
				update_work: []
			}
		});
		callSavingToast(p);
		await p;
	}

	async function delete_item(index: number) {
		const { error } = await client.PUT('/api/list/items', {
			fetch,
			params: { query: { list_id: data.list.id } },
			body: {
				delete: [index],
				update_work: [],
				update_description: [],
				move: [],
				insert_at: []
			}
		});
		if (!error) {
			entries.splice(index, 1);
			entries = entries;
			data.entries.count--;
		}
	}

	const pull = async () => {
		await client.POST('/api/list/pull_upstream', {
			fetch,
			params: { query: { list_id: data.list.id } }
		});
		goto(`/list/${data.list.id}`, { invalidateAll: true });
	};
</script>

<Section title={data.list.name} type={m.stale_loose_squid_cut()} menuLinks={data.links}>
	<form use:enhance method="POST">
		<table>
			<tbody>
				<tr
					><th><label for="name">{m.large_factual_octopus_exhale()}</label></th><td
						><input type="text" name="name" value={form?.name ?? data.list?.name} /></td
					></tr
				>
				<tr
					><th><label for="description">{m.clear_lucky_peacock_pick()}</label></th><td
						><textarea
							name="description"
							value={form?.description ?? data.list?.description}
						></textarea></td
					></tr
				>
			</tbody>
		</table>
		<input type="submit" />
	</form>
	<form action="/list/{data.list.id}/delete">
		<button data-sveltekit-preload-data="tap">{m.key_sea_chicken_boost()}</button>
	</form>
	{#if data.list.upstream}
		<button onclick={pull}>{m.honest_tiny_sparrow_gaze()}</button>
	{/if}
</Section>
<Section title={m.bald_clear_marlin_grasp()}>
	{#if entries.length}
		<table class="w-full">
			<tbody>
				{#each entries as entry, i (entry.work.id)}
					<tr
						class="svelte-dnd-touch-feedback"
						use:droppable={{
							container: i.toString(),
							callbacks: { onDrop: handleDrop }
						}}
						><th>{i + 1}</th><td class="w-10"
							><div
								class="svelte-dnd-touch-feedback w-10 cursor-move border text-center select-none"
								use:draggable={{
									container: i.toString(),
									dragData: [i, entry]
								}}
							>
								=
							</div></td
						><td class="w-56">
							<a target="_blank" href="/work/{entry.work.id}"
								><WorkThumbnail
									class="aspect-video w-56"
									thumbnail={entry.work.thumbnail}
									alt={getDisplayText(entry.work.title)}
								/></a
							>
							<h3>
								<a target="_blank" href="/work/{entry.work.id}"
									><DisplayText value={entry.work.title} /></a
								>
							</h3>
						</td>
						<td>
							<textarea
								class="min-h-30 w-full"
								value={entry.description}
								oninput={debounce(
									(el) =>
										update_description(
											i,
											(el.target as HTMLTextAreaElement).value
										),
									1000
								)}
							></textarea>
						</td>
						<td>
							<button type="button" onclick={() => delete_item(i)}>
								{m.even_alert_grebe_taste()}
							</button>
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
		{#if data.entries?.count}
			<LoadMoreButton
				fetchNextBatch={() =>
					client.GET('/api/list/entries', {
						fetch,
						params: {
							query: {
								list_id: data.list.id,
								limit: data.batch_size,
								offset: entries.length
							}
						}
					})}
				maxCount={data.entries!.count}
				bind:results={entries}
			/>
		{/if}
	{:else}
		<h3>{m.hour_flat_finch_zoom()}</h3>
	{/if}
</Section>

<style>
	:global(.drag-over) {
		outline: 2px solid var(--otodb-color-content-primary);
	}
</style>
