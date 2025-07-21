<script lang="ts">
	import { invalidate } from '$app/navigation';
	import client from './api';
	import { SongRelationTypes, WorkRelationTypes } from './enums';
	import { m } from './paraglide/messages';
	import { getLocale } from './paraglide/runtime';
	import type { components } from './schema';
	import SongField from './SongField.svelte';
	import WorkCard from './WorkCard.svelte';
	import WorkField from './WorkField.svelte';
	import { callSavingToast } from './toast';

	interface Props {
		this_id: number;
		obj_type: 'work' | 'song';
		init_relations: [components['schemas']['RelationSchema'][], { id: number }[]];
	}

	let { this_id, init_relations, obj_type }: Props = $props();

	const endpoint = obj_type === 'work' ? '/api/work/relation' : '/api/tag/song_relation';

	let relations: { swapped: boolean; item: any | null; relation: number }[] = $state(
		init_relations[0]
			.filter(({ A_id, B_id }) => A_id === this_id || B_id === this_id)
			.map(({ A_id, B_id, relation }) => ({
				swapped: A_id === this_id,
				item: init_relations[1].find((e) => e.id === (A_id === this_id ? B_id : A_id)),
				relation
			}))
	);
	const delete_relation = (i: number) => async () => {
		relations.splice(i, 1);
		await client.DELETE(endpoint, {
			fetch,
			params: { query: { A: relations[i].item.id, B: this_id } }
		});
	};
	const post_relation = (i: number, notify: boolean) => async () => {
		const r = relations[i];
		relations = relations.filter((rel, j) => rel.item.id !== r.item.id || j === i);
		if (r.item.id) {
			const p = client.POST(endpoint, {
				fetch,
				body: {
					A_id: !r.swapped ? r.item.id : this_id!,
					B_id: r.swapped ? r.item.id : this_id!,
					relation: r.relation
				}
			});
			if (notify) callSavingToast(p);
			await p;
		}
		invalidate(`/${obj_type === 'song' ? 'tag' : 'work'}/`);
	};
	const swap_relation = (i: number) => async () => {
		relations[i].swapped = !relations[i].swapped;
		await post_relation(i, false)();
	};
	let new_item = $state(null);
	const add_new_item = async () => {
		if (new_item) {
			relations.unshift({ swapped: false, item: new_item, relation: 0 });
			await post_relation(0, false)();
			new_item = null;
		}
	};

	const invert_subordinate_phrase = getLocale() !== 'en';
</script>

<div class="grid w-fit grid-cols-2 gap-3">
	{#if obj_type === 'work'}
		<WorkField bind:value={new_item} />
	{:else if obj_type === 'song'}
		<SongField bind:value={new_item} />
	{/if}
	<button onclick={add_new_item} disabled={!new_item}>{m.swift_dry_gecko_boost()}</button>
</div>

{#snippet work(relation, swapped: boolean)}
	{#if swapped}
		{#if obj_type === 'work'}
			<WorkCard work={relation.item} />
		{:else if obj_type === 'song'}
			<a href="/tag/{relation.item.work_tag}">{relation.item.title}</a>
		{/if}
	{:else}
		{m.stout_frail_warbler_support()}
		{#if obj_type === 'work'}
			{m.grand_merry_fly_succeed()}
		{:else if obj_type === 'song'}
			{m.grand_nice_pony_belong()}
		{/if}
	{/if}
{/snippet}

<table>
	<tbody>
		{#each relations as relation, i (i)}
			<tr>
				<td class="w-64">{@render work(relation, !relation.swapped)}</td>
				<td>{m.grand_vexed_snail_ripple()}</td>
				{#if invert_subordinate_phrase}
					<td class="w-64">{@render work(relation, relation.swapped)}</td>
					<td>{m.clean_best_kangaroo_achieve()}</td>
					<td
						><select
							name="relation"
							bind:value={relation.relation}
							onchange={post_relation(i, true)}
						>
							{#each obj_type === 'work' ? WorkRelationTypes : SongRelationTypes as rel, j (j)}
								<option value={j}>{rel()}</option>
							{/each}
						</select></td
					>
				{:else}
					<td
						><select
							name="relation"
							bind:value={relation.relation}
							onchange={post_relation(i, true)}
						>
							{#each obj_type === 'work' ? WorkRelationTypes : SongRelationTypes as rel, j (j)}
								<option value={j}>{rel()}</option>
							{/each}
						</select></td
					>
					<td>{m.clean_best_kangaroo_achieve()}</td>
					<td class="w-64">{@render work(relation, relation.swapped)}</td>
				{/if}
				<td
					><button type="button" onclick={swap_relation(i)}
						>{m.less_green_angelfish_hunt()}</button
					></td
				>
				<td
					><button type="button" onclick={delete_relation(i)}
						>{m.even_alert_grebe_taste()}</button
					></td
				>
			</tr>
		{/each}
	</tbody>
</table>
