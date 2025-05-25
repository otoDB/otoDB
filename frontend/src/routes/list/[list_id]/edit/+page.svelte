<script lang="ts">
	import Section from '$lib/Section.svelte';
	import type { PageProps } from './$types';
	import { m } from '$lib/paraglide/messages.js';
	import { enhance } from '$app/forms';
	import { debounce } from '$lib/ui';
	import client from '$lib/api';

	let { data, form }: PageProps = $props();

	let entries_copy = data.entries!.items.map((el, i) => Object.assign({}, el, { ui_id: i }));
	let entries = $state(entries_copy);

	let source: number | null = null,
		target: number | null = null;

	function dragenter(e) {
		target = e.target.closest('tr').dataset.ridx;
		if (source && target) {
			entries = [...entries_copy];
			if (source != target) {
				entries.splice(target, 0, entries.splice(source, 1)[0]);
			}
		}
	}

	function ondragstart(e) {
		source = e.target.closest('tr').dataset.ridx;
		e.dataTransfer!.effectAllowed = 'move';
	}

	async function ondragend(e) {
		if (source && target && source != target) {
			await client.PUT('/api/list/items', {
				fetch,
				params: { query: { list_id: data.list.id } },
				body: {
					move: [[source, target]],
					delete: [],
					update_description: [],
					update_work: []
				}
			});
			source = null;
			target = null;
			entries_copy = [...entries];
		}
	}

	async function update_description(el) {
		await client.PUT('/api/list/items', {
			fetch,
			params: { query: { list_id: data.list.id } },
			body: {
				update_description: [[+el.target.closest('tr').dataset.ridx, el.target.value]],
				move: [],
				delete: [],
				update_work: []
			}
		});
	}

	async function delete_item(el) {
		const i = +el.target.closest('tr')!.dataset.ridx!;
		const { error } = await client.PUT('/api/list/items', {
			fetch,
			params: { query: { list_id: data.list.id } },
			body: {
				delete: [i],
				update_work: [],
				update_description: [],
				move: [],
				insert_at: []
			}
		});
		if (!error) {
			entries.splice(i, 1);
			entries_copy = [...entries];
		}
	}
</script>

<svelte:head>
	<title
		>{m.mild_loud_shad_enchant({
			type: m.stale_loose_squid_cut(),
			name: data.list.name
		})}</title
	>
</svelte:head>

<Section
	title={m.mild_loud_shad_enchant({ type: m.stale_loose_squid_cut(), name: data.list.name })}
>
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
</Section>
<Section title="Entries">
	<table>
		<tbody>
			{#each entries as entry, i (entry.ui_id)}
				<tr ondragenter={debounce(dragenter, 50)} data-ridx={i}
					><th>{i + 1}</th><td
						><div
							class="border pr-5 pl-5 select-none"
							draggable="true"
							{ondragstart}
							{ondragend}
							role="none"
						>
							=
						</div></td
					><td>
						<a target="_blank" href="/work/{entry.work.id}"
							><img
								class="w-56"
								src={entry.work.thumbnail}
								alt={entry.work.title}
							/></a
						>
						<h3>
							<a target="_blank" href="/work/{entry.work.id}">{entry.work.title}</a>
						</h3>
					</td><td
						><textarea value={entry.description} oninput={debounce(update_description)}
						></textarea></td
					><td
						><button type="button" onclick={delete_item}
							>{m.even_alert_grebe_taste()}</button
						></td
					></tr
				>
			{/each}
		</tbody>
	</table>
</Section>
